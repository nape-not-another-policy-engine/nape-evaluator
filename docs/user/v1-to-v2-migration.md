# V1 To V2 Migration

Use this guide when you already understand the historical V1 evaluator contract and need to move tests, wrapper logic, or operator habits to the current V2 contract.

This guide is practical on purpose.

It does not try to restate every current evaluator rule in full.

Use these companion docs when you need exact current contract detail:

- [CLI reference](cli-reference.md)
- [Evaluator contract](../reference/evaluator-contract.md)
- [Current evaluator reference](../product/current-evaluator-reference.md)
- [V1 evaluator baseline](../product/v1-evaluator-baseline.md)

## What Changed At A High Level

The evaluator is now fully committed to the V2 contract.

The important migration consequence is:

- V2 is not backward compatible with the V1 `--test` transport or the V1 tuple-returning test contract

At a high level, V1 to V2 changed these boundaries:

1. one requested test is no longer supplied through `--test`
2. caller-owned comparison input is now explicit through `evaluations`
3. tests now receive `evaluate(evidence, evaluations, metadata)`
4. evidence is no longer always raw text lines
5. completed test results are now structured objects, not tuples
6. evaluator operational failures are now separated from completed-test conclusions more explicitly

If you are migrating wrapper code rather than just Python tests, the practical shift is:

- stop treating the evaluator as a one-test, one-tuple subprocess
- start treating it as a packet-in, structured-JSON-out subprocess with explicit row-level and evaluator-level meaning

## Fast Comparison

| Area | V1 | V2 |
| --- | --- | --- |
| CLI request shape | `--evidence` + `--test` | `--evidence` + repeated `--invoke` / `--invoke-file`, or one `--request-file` |
| Test signature | `evaluate(evidence)` | `evaluate(evidence, evaluations, metadata)` |
| Evidence input | text lines from `readlines()` | typed loading by extension |
| Caller comparison input | usually hardcoded inside the Python test | explicit caller-owned `evaluations` input |
| Test return shape | tuple such as `(\"pass\", \"Reason\")` | object with `conclusion`, `facts`, `reason` |
| Result vocabulary | often `pass` / `fail` / `error` | `true` / `false` / `inconclusive` |
| Evaluator operational failures | often surfaced as output `error` | separated into blocked rows plus `evaluator.messages` |

## Wrapper Migration At A Glance

If your old integration wrapped the evaluator from another script, service, or application, these are usually the most important wrapper-side migrations:

1. replace `--test` subprocess calls with one explicit V2 request packet
2. stop expecting one flat stdout object with only `outcome` and `reason`
3. parse the outer V2 object:
   - `results`
   - `evaluator.messages`
   - `evaluator.summary`
4. classify blocked rows separately from completed rows
5. stop treating all unusual conditions as one generic `error`

## 1. CLI Transport Migration

### V1 Pattern

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

### V2 Direct Pattern

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke '{"test":"./verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

### V2 Full-Request Pattern

```bash
nape-eval --request-file ./request.json
```

with:

```json
{
  "evidence": "./author_verification.json",
  "tests": [
    {
      "test": "./verify_author_complete.py",
      "evaluations": [
        {
          "subject": {
            "name": "status",
            "data_type": "text"
          },
          "criteria": {
            "equals": "complete"
          }
        }
      ]
    }
  ]
}
```

### Migration Recommendation

If you are migrating scripts or wrappers, prefer moving straight to full-request mode with `--request-file`.

Why:

- it makes the new request boundary explicit
- it is easier to retain and replay
- it maps more directly to software integration and multi-test invocation

## 2. Test Function Signature Migration

### V1 Pattern

```python
def evaluate(evidence):
    ...
```

### V2 Pattern

```python
def evaluate(evidence, evaluations, metadata):
    ...
```

New ownership model:

- `evidence`: evaluator-loaded evidence content
- `evaluations`: caller-owned accepted evaluation input
- `metadata`: evaluator-owned execution metadata

Migration rule:

- do not hide caller comparison input in `metadata`
- read caller criteria from `evaluations`
- use `metadata` only for evaluator-owned context such as `evidence_type` and `schema_version`

## 2A. Wrapper Invocation Migration

### V1 Wrapper Habit

Many V1 wrappers effectively did some version of:

1. choose one evidence path
2. choose one test path
3. launch:
   - `nape-eval --evidence ... --test ...`
4. parse stdout as:
   - `outcome`
   - `reason`
5. branch on one final status

That model does not match the current evaluator boundary anymore.

### V2 Wrapper Habit

A V2-aware wrapper should usually do this instead:

1. build one outer request packet
2. include one or more requested test packets inside `tests`
3. invoke:
   - `nape-eval --request-file <path-or->`
4. parse stdout as one outer JSON object
5. classify:
   - each `results[*]` row
   - evaluator messages
   - summary counts

### Before And After Wrapper Flow

V1-style wrapper flow:

```text
argv = [
  "nape-eval",
  "--evidence", evidence_path,
  "--test", test_path,
]

stdout_json = json_decode(run_process(argv).stdout)

if stdout_json.outcome == "pass":
  handle_success()
elif stdout_json.outcome == "fail":
  handle_failed_check()
else:
  handle_error()
```

V2-style wrapper flow:

```text
request = {
  evidence: evidence_path,
  tests: [
    {
      test: test_path,
      evaluations: [...]
    }
  ]
}

write_request_packet(request_path, request)

argv = ["nape-eval", "--request-file", request_path]
stdout_json = json_decode(run_process(argv).stdout)

for row in stdout_json.results:
  classify_row(row.execution, row.result)

for message in stdout_json.evaluator.messages:
  classify_evaluator_message(message)

use_summary_as_aggregate_confirmation(stdout_json.evaluator.summary)
```

## 3. Evidence Contract Migration

### V1 Assumption

V1 tests could assume `evidence` was a list of text lines.

That often led to tests that re-opened or re-parsed JSON-like content themselves.

### V2 Assumption

V2 evidence is typed by extension before the test is called.

Examples:

- `.json` becomes a parsed object
- `.xml` becomes an XML root element
- `.yaml` and `.yml` become parsed YAML objects
- `.pdf` becomes extracted text lines
- `.txt` and unknown extensions remain text lines

### Migration Risk

This is one of the biggest breaking changes.

A V1 test that expects text lines can fail immediately when V2 passes a parsed object instead.

### Migration Recommendation

Rewrite tests so they consume the actual V2 evidence type instead of trying to preserve V1 line-oriented parsing habits.

Example:

V1-style JSON parsing:

```python
import json

def evaluate(evidence):
    payload = json.loads("".join(evidence))
    ...
```

V2-style JSON handling:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test requires JSON evidence."
        }

    payload = evidence
    ...
```

## 4. Comparison Logic Migration

### V1 Habit

Many V1 tests hardcoded their comparison threshold or expected value directly inside the Python test.

Example:

```python
def evaluate(evidence):
    coverage = ...
    if coverage >= 80:
        return "pass", "Coverage meets the requirement."
    return "fail", "Coverage does not meet the requirement."
```

### V2 Direction

V2 makes caller-owned comparison input explicit through `evaluations`.

Example input:

```json
[
  {
    "subject": {
      "name": "coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 80
    }
  }
]
```

Migration recommendation:

- move caller-owned comparison values out of hardcoded test logic when they are truly caller-controlled criteria
- keep fact extraction and evaluation reasoning inside the Python test

## 5. Return-Shape Migration

### V1 Pattern

```python
return "pass", "Reason text"
```

### V2 Pattern

```python
return {
    "conclusion": "true",
    "facts": [
        {
            "name": "status",
            "value": "complete",
            "value_type": "text",
            "status": "found",
        }
    ],
    "reason": "The author has achieved the status of complete.",
}
```

Required completed-result keys:

- `conclusion`
- `facts`
- `reason`

Supported completed-result conclusions:

- `true`
- `false`
- `inconclusive`

Migration rule:

- do not return V1 tuple outcomes such as `pass`, `fail`, or `error`
- do not return partially structured result objects

If a completed V2 test returns an invalid result contract, the evaluator now normalizes that completed row to `inconclusive`.

## 6. Outcome And Error Interpretation Migration

### V1 Mental Model

In V1, `error` often served as both:

- evaluator execution failure
- action-level outcome

### V2 Mental Model

In V2, keep these meanings separate:

- completed `true`
- completed `false`
- completed `inconclusive`
- blocked invocation with evaluator-synthesized `inconclusive`
- evaluator operational messages in `evaluator.messages`

Migration rule:

- do not translate every unusual V2 condition into one wrapper-local “error” bucket

Read these fields together:

- `results[*].execution`
- `results[*].result.conclusion`
- `evaluator.messages`
- `evaluator.summary`

## 6A. Stdout Shape Migration For Wrappers

### V1 Expected Shape

Many V1 wrappers could assume stdout looked roughly like:

```json
{
  "outcome": "pass",
  "reason": "Reason text"
}
```

That shape no longer represents the evaluator boundary.

### V2 Expected Shape

V2 stdout now looks like:

```json
{
  "results": [
    {
      "test": "./verify_author_complete.py",
      "evidence": "./author_verification.json",
      "evaluations": [
        {
          "subject": {
            "name": "status",
            "data_type": "text"
          },
          "criteria": {
            "equals": "complete"
          }
        }
      ],
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "true",
        "facts": [
          {
            "name": "status",
            "value": "complete",
            "value_type": "text",
            "status": "found"
          }
        ],
        "reason": "The author has achieved the status of complete."
      }
    }
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 1,
      "ran": 1,
      "true": 1,
      "false": 0,
      "inconclusive": 0,
      "message_count": 0,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 0
    }
  }
}
```

### Migration Rule

Do not build your V2 wrapper around a synthetic translation back to:

- `pass`
- `fail`
- `error`

Instead:

- read row-level outcome from `results[*]`
- read operational context from `evaluator.messages`
- use `evaluator.summary` as an aggregate check, not as the only interpretation surface

## 6B. Wrapper Classification Example

If your V1 wrapper effectively did:

```text
if stdout_json.outcome == "pass":
  return "success"
if stdout_json.outcome == "fail":
  return "failed_check"
return "error"
```

then a better first-pass V2 wrapper model is:

```text
for row in stdout_json.results:
  if row.execution.executed == true and row.result.conclusion == "true":
    record("completed_true")
  elif row.execution.executed == true and row.result.conclusion == "false":
    record("completed_false")
  elif row.execution.executed == true and row.result.conclusion == "inconclusive":
    record("completed_inconclusive")
  elif row.execution.executed == false and row.result.conclusion == "inconclusive":
    record("blocked_inconclusive")
  else:
    record("contract_or_mapping_problem")

if any(message.level == "error" for message in stdout_json.evaluator.messages):
  record("evaluator_error_present")
```

The important migration idea is:

- row conclusion and evaluator operational state are no longer the same thing

## 7. Before And After Example

### V1 Test

```python
import json

def evaluate(evidence):
    payload = json.loads("".join(evidence))
    status = payload.get("status")
    if status == "complete":
        return "pass", "The author has achieved the status of complete."
    return "fail", "The author has not achieved the status of complete."
```

### V2 Test

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test requires JSON evidence.",
        }

    status = evidence.get("status")
    fact_record = {
        "name": "status",
        "value": status,
        "value_type": "text",
        "status": "found" if status is not None else "not_found",
    }

    if status is None:
        return {
            "conclusion": "inconclusive",
            "facts": [fact_record],
            "reason": "The status fact could not be established from the evidence.",
        }

    status_evaluation = next(
        (
            item for item in evaluations
            if item.get("subject", {}).get("name") == "status"
        ),
        None,
    )
    expected_status = (
        status_evaluation.get("criteria", {}).get("equals")
        if status_evaluation is not None
        else None
    )

    if expected_status is None:
        return {
            "conclusion": "inconclusive",
            "facts": [fact_record],
            "reason": "The caller did not provide status criteria.",
        }

    if status == expected_status:
        return {
            "conclusion": "true",
            "facts": [fact_record],
            "reason": f"Status is {status}, which satisfies the expected value.",
        }

    return {
        "conclusion": "false",
        "facts": [fact_record],
        "reason": f"Status is {status}, which does not satisfy the expected value {expected_status}.",
    }
```

## 8. Test Author Migration Checklist

- update the function signature to `evaluate(evidence, evaluations, metadata)`
- stop assuming `evidence` is always text lines
- add basic defensive checks for expected `metadata["evidence_type"]`
- move caller-controlled thresholds or expected values into `evaluations` where appropriate
- return a structured object with `conclusion`, `facts`, and `reason`
- use only `true`, `false`, or `inconclusive`
- treat missing or unestablishable facts as explicit evaluation conditions, not silent fall-throughs

## 9. Wrapper Or CLI Integration Migration Checklist

- stop invoking the evaluator with `--test`
- move to `--invoke`, `--invoke-file`, or preferably `--request-file`
- build explicit `evaluations` input
- stop assuming stdout is the V1 `{"outcome": ..., "reason": ...}` shape
- parse the outer V2 object with:
  - `results`
  - `evaluator.messages`
  - `evaluator.summary`
- classify blocked invocations separately from completed `inconclusive`
- treat evaluator operational messages separately from completed-test reasoning
- stop reducing the whole evaluator response to one synthetic pass/fail/error scalar unless your own product has a deliberate mapping layer for that

## 10. What To Read Next

- If you are updating tests:
  - [Test-of-detail authoring](test-of-detail-authoring.md)
  - [V2 test authoring](v2-test-authoring/README.md)
- If you are updating software that wraps the evaluator:
  - [Software integration guide](software-integration/README.md)
- If you need exact field-level contract detail:
  - [CLI reference](cli-reference.md)
  - [Evaluator contract](../reference/evaluator-contract.md)
