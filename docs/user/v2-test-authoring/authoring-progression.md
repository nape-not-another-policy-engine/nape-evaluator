# Authoring Progression

This guide is the teaching path from:

- "I just need to get a test working"

to:

- "I can write a test-of-detail that is input-driven, safe, diagnosable, and easy to evolve"

The progression is intentionally staged.

The later stages do not invalidate the earlier ones.

They harden them.

## Two Authoring Modes

This document teaches two equally valid modes of getting started.

### Quick-Start Authoring

Use this when:

- you are new to NAPE
- you are still proving the evidence shape
- you want the fastest possible working test

In this mode, the main goal is:

- get a correct result quickly

### Production-Grade Authoring

Use this when:

- the test is becoming durable
- other people will copy or maintain it
- you need to know exactly why something failed

In this mode, the main goal is:

- make execution safe, explicit, and diagnosable

## Why This Sequence Matters

The progression in this document is not ordered by code style.

It is ordered by learning and operational value.

That means:

1. first get a result
2. then make one rule caller-driven
3. then make the test safe
4. then make facts explicit
5. then choose how to fail
6. then refactor into helpers
7. then scale up to richer logic

That is a better beginner path than introducing helper decomposition too early.

## Part 1: Get Working Quickly

This part is about first success.

The goal is to prove that:

- the evidence shape is usable
- the domain logic is basically correct
- caller-owned `evaluations` can start driving outcomes without rewriting the Python file

## How To Write The Python As You Go

Do not think of this progression as only:

- stage 0 input shape
- stage 1 input shape
- stage 2 validation ideas

It is also the Python-writing sequence.

For a new author, the safest writing order is:

1. write the public `evaluate(evidence, evaluations, metadata)` function
2. make one evidence read work
3. make one returned result object work
4. add one caller-driven lookup
5. add explicit contract validation
6. add explicit fact-establishment handling
7. only then refactor or scale up

That means each stage below should be read as:

- what the test does
- how to change the Python file to reach that stage

If you try to jump straight to the fully hardened version, the file usually becomes harder to understand.

## Stage 0: Hardcoded Starter Test

### Goal

Get one working test-of-detail result with the smallest possible moving parts.

### What You Are Doing Here

At this stage:

- the only external variables are the evidence file and the test-of-detail file
- the test hardcodes its subject and threshold or expected value internally
- `evaluations` may be empty and ignored

Current runtime note:

- conceptually this is still the "no real input parameters yet" stage
- operationally, the current V2 CLI still transports one invocation packet
- the simplest packet shape is:

```json
{
  "test": "./my_test.py",
  "evaluations": []
}
```

### Example Input

Small evidence payload:

```json
{
  "status": "complete"
}
```

Small invocation packet:

```json
{
  "test": "./my_test.py",
  "evaluations": []
}
```

### What You Can Ignore For Now

At this stage, you can ignore:

- dynamic caller-driven criteria
- helper decomposition
- fail-fast versus fail-slow tradeoffs
- multi-subject logic

### Example

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    status = evidence.get("status")
    fact = {
        "name": "status",
        "value": status,
        "value_type": "text",
        "status": "found" if status not in (None, "") else "not_found",
    }

    if fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [fact],
            "reason": "Status could not be established.",
        }

    if status == "complete":
        return {
            "conclusion": "true",
            "facts": [fact],
            "reason": "Status is complete.",
        }

    return {
        "conclusion": "false",
        "facts": [fact],
        "reason": f"Status is '{status}', not 'complete'.",
}
```

### Example Output

Compact successful result:

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "status",
      "value": "complete",
      "value_type": "text",
      "status": "found"
    }
  ],
  "reason": "Status is complete."
}
```

### How To Write This Python

Write this stage in the simplest possible order:

1. write `def evaluate(evidence, evaluations, metadata):`
2. ignore `evaluations` for now
3. read one evidence field such as `status`
4. build one fact dict
5. return:
   - `inconclusive` if the fact is not usable
   - `true` if the value matches your hardcoded expectation
   - `false` otherwise

Smallest safe writing sequence:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    status = evidence.get("status")
    fact = {
        "name": "status",
        "value": status,
        "value_type": "text",
        "status": "found" if status not in (None, "") else "not_found",
    }

    if fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [fact],
            "reason": "Status could not be established.",
        }

    if status == "complete":
        return {
            "conclusion": "true",
            "facts": [fact],
            "reason": "Status is complete.",
        }

    return {
        "conclusion": "false",
        "facts": [fact],
        "reason": f"Status is '{status}', not 'complete'.",
    }
```

Then harden it further by:

- adding the schema-version check
- moving the hardcoded rule into caller-owned `evaluations`

What the author should notice:

- the first working version does not need helpers
- the first working version does not need dynamic input
- the main job is to prove that the file can read evidence and return a correct result object

### What Can Go Wrong

Even the starter test can still fail in meaningful ways:

- the evidence is not JSON
- the evidence does not contain the expected field
- the value is empty or unusable for the test

At this stage, that is acceptable.

The goal is still to prove the first working path.

### Why This Stage Is Valid

This is a legitimate way to start because it proves:

- the evidence contract
- the domain logic
- the end-to-end evaluator path

### Why This Stage Is Not Enough Yet

The main limitation is:

- changing the expected value requires editing the Python test

### What The Next Stage Adds

The next stage keeps the logic simple but moves one hardcoded rule out of the Python file and into caller-owned `evaluations`.

### Canonical Fixture

Related live reference:

- [verify_author_complete.py](../../../tests/json/test_of_detail/verify_author_complete.py)

## Stage 1: Externalize One Rule Into `evaluations`

### Goal

Keep the test logic, but move one hardcoded comparison value out of the Python file and into caller-owned input.

### What You Are Doing Here

Do not change everything at once.

Just replace one hardcoded rule with one caller-driven criterion.

Example caller input:

```json
[
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
```

Small evidence payload:

```json
{
  "status": "complete"
}
```

Updated invocation packet:

```json
{
  "test": "./my_test.py",
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
```

Updated test snippet:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    expected_status = evaluations[0]["criteria"]["equals"]
    actual_status = evidence.get("status")
    status_fact = {
        "name": "status",
        "value": actual_status,
        "value_type": "text",
        "status": "found" if actual_status not in (None, "") else "not_found",
    }

    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [status_fact],
            "reason": "Status could not be established.",
        }

    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"Status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": f"Status is '{actual_status}', not '{expected_status}'.",
    }
```

### Why This Stage Comes Now

This is the cleanest first improvement because:

- the test still stays simple
- the result now changes when the input changes
- threshold and expectation changes no longer require editing the Python test

### What You Can Ignore For Now

You can still ignore:

- heavy refactoring
- multi-fact coordination
- sophisticated diagnostics

### Example Output

Same evidence, two different inputs:

Input A:

```json
{
  "subject": {
    "name": "status",
    "data_type": "text"
  },
  "criteria": {
    "equals": "complete"
  }
}
```

Output A:

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "status",
      "value": "complete",
      "value_type": "text",
      "status": "found"
    }
  ],
  "reason": "Status is complete."
}
```

Input B:

```json
{
  "subject": {
    "name": "status",
    "data_type": "text"
  },
  "criteria": {
    "equals": "approved"
  }
}
```

Output B:

```json
{
  "conclusion": "false",
  "facts": [
    {
      "name": "status",
      "value": "complete",
      "value_type": "text",
      "status": "found"
    }
  ],
  "reason": "Status is 'complete', not 'approved'."
}
```

### How To Write This Python

Do not rewrite the entire file.

Change one thing:

- replace the hardcoded expected value with one value read from `evaluations`

Good incremental sequence:

1. keep the old stage-0 logic
2. read `evaluations[0]["criteria"]["equals"]`
3. compare the evidence value to that caller-provided value
4. prove that changing the input changes the result

Smallest useful rewrite:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    expected_status = evaluations[0]["criteria"]["equals"]
    actual_status = evidence.get("status")
    status_fact = {
        "name": "status",
        "value": actual_status,
        "value_type": "text",
        "status": "found" if actual_status not in (None, "") else "not_found",
    }

    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [status_fact],
            "reason": "Status could not be established.",
        }

    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"Status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": f"Status is '{actual_status}', not '{expected_status}'.",
    }
```

Then improve it by:

- adding the schema-version check
- validating that the caller supplied the criterion the test expects
- replacing positional indexing with a subject-name lookup later

What the author should notice:

- stage 1 is not “make the test advanced”
- stage 1 is only “prove caller input can drive one rule”
- this is still allowed to be a small and slightly rough Python file

### What Can Go Wrong

Now there is a second failure family:

- the caller does not supply the criterion the test expects
- the caller supplies the wrong criterion type for the test logic

At this stage, many authors still handle that lightly.

The next stage makes those expectations explicit.

### Why This Stage Is Not Enough Yet

The test may now be caller-driven, but it still may not explain clearly:

- what assumptions it depends on
- what failed when those assumptions break

### What The Next Stage Adds

The next stage teaches the test to reject unsupported conditions explicitly and return a clear test-level `inconclusive` result.

### Canonical Fixture

Primary live reference:

- [verify_author_complete.py](../../../tests/json/test_of_detail/verify_author_complete.py)

Secondary threshold-style reference:

- [verify_component_coverage_minimum.py](../../../tests/json/test_of_detail/verify_component_coverage_minimum.py)

## Part 2: Make It Safe And Diagnosable

This part is about turning a working test into a trustworthy one.

The goal is to make it clear:

- when the test contract itself is wrong
- when the evidence does not support a decision
- how the test chooses to behave when facts cannot be established

## Stage 2: Add Defensive Validation

### Goal

Make the test explicit about what it needs in order to run safely and meaningfully.

### What You Are Doing Here

At this stage, the test should validate:

- expected `metadata["evidence_type"]`
- expected `metadata["schema_version"]`
- the evidence shape it depends on
- the criterion keys and values the test requires

Example defensive-validation snippet:

```python
if metadata.get("evidence_type") != "json":
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": "This test expects JSON evidence.",
    }

minimum = evaluation.get("criteria", {}).get("minimum")
if not isinstance(minimum, (int, float)) or isinstance(minimum, bool):
    return {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": "This test requires criteria.minimum to be numeric.",
    }
```

This is the first real safety layer.

### Key Rule

If the test understands the problem and can explain it as a contract problem, return:

- `inconclusive`

Examples:

- wrong evidence type
- unsupported schema version
- required criterion missing for this test
- criterion value present but unusable for this test

### Example Output

Compact test-level contract failure:

```json
{
  "conclusion": "inconclusive",
  "facts": [],
  "reason": "This test requires review_date criteria.minimum and criteria.maximum to be ISO-8601 dates."
}
```

### How To Write This Python

At this stage, stop adding more policy logic.

Instead, add explicit checks ahead of the policy logic you already have.

Good writing order:

1. keep the stage-1 comparison working
2. add metadata validation first
3. add validation for the evaluation entry your test requires
4. add validation for the exact criterion key and value type you depend on
5. return `inconclusive` with a concrete reason when the contract is wrong

Good intermediate shape:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    if metadata.get("schema_version") != "2":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test only supports evaluator schema version 2.",
        }

    evaluation = evaluations[0] if evaluations else None
    if evaluation is None:
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test requires one status evaluation.",
        }

    expected_status = evaluation.get("criteria", {}).get("equals")
    if not isinstance(expected_status, str) or not expected_status:
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test requires criteria.equals to be a non-empty string.",
        }

    actual_status = evidence.get("status")
    status_fact = {
        "name": "status",
        "value": actual_status,
        "value_type": "text",
        "status": "found" if actual_status not in (None, "") else "not_found",
    }

    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [status_fact],
            "reason": "Unable to evaluate because the status fact could not be established.",
        }

    if actual_status == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": f"Status is {expected_status}.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": f"Status is '{actual_status}', not '{expected_status}'.",
    }
```

What the author should notice:

- validation is real authoring work, not polish
- `inconclusive` is for a test-known contract problem or a fact-establishment problem that prevents a `true` or `false` conclusion
- this stage is still not about helpers first; it is about making assumptions explicit

### Why This Stage Comes Before Helper Refactoring

The test should first understand its own safety boundaries.

Once those boundaries are explicit, the helper structure becomes obvious.

### What Can Go Wrong

Common problems at this stage:

- the test expects JSON but receives another evidence type
- the test requires `minimum` but the caller supplied `equals`
- the test requires a typed criterion string such as a date or duration and the caller supplied something malformed

This is the stage where the test stops guessing.

### Why This Stage Is Not Enough Yet

Even if the contract is valid, the evidence may still fail to produce usable facts.

### What The Next Stage Adds

The next stage distinguishes:

- “the test can run safely”

from:

- “the evidence supports a decision”

### Canonical Fixtures

Primary live references:

- [verify_author_complete.py](../../../tests/json/test_of_detail/verify_author_complete.py)
- [verify_last_review_timestamp_minimum.py](../../../tests/json/test_of_detail/verify_last_review_timestamp_minimum.py)
- [verify_review_date_range.py](../../../tests/json/test_of_detail/verify_review_date_range.py)

## Stage 3: Add Fact Establishment Discipline

### Goal

Separate:

- "the test can run"

from:

- "the evidence contains usable facts for a decision"

### What You Are Doing Here

At this stage, extract explicit fact records and distinguish:

- `found`
- `not_found`
- `invalid`

Recommended fact shape:

```python
{
    "name": "coverage",
    "value": 85.0,
    "value_type": "number",
    "unit": "percent",
    "status": "found",
}
```

Inline examples of fact status:

Found:

```json
{
  "name": "review_date",
  "value": "2026-06-15",
  "value_type": "date",
  "status": "found"
}
```

Not found:

```json
{
  "name": "service_owner",
  "value": null,
  "value_type": "text",
  "status": "not_found"
}
```

Invalid:

```json
{
  "name": "restore_duration",
  "value": "45 minutes",
  "value_type": "duration",
  "status": "invalid"
}
```

### Key Rule

If the evidence does not yield the usable facts needed for a decision, return:

- `inconclusive`

That is different from a completed test intentionally returning `inconclusive`.

### Why This Stage Matters

This is where the test becomes explainable.

It can now tell the reader:

- what it found
- what it did not find
- what it found but could not use

### Example Output

Compact fact-establishment failure:

```json
{
  "conclusion": "inconclusive",
  "facts": [
    {
      "name": "restore_duration",
      "value": "45 minutes",
      "value_type": "duration",
      "status": "invalid"
    }
  ],
  "reason": "Unable to evaluate because the restore_duration fact could not be established."
}
```

### How To Write This Python

This is the stage where the file stops reasoning directly on raw evidence values.

Instead:

1. extract the raw value
2. convert it into a fact record
3. decide whether the fact is:
   - `found`
   - `not_found`
   - `invalid`
4. only evaluate if the fact is usable

Good intermediate shape:

```python
def _extract_status_fact(evidence):
    raw_value = evidence.get("status")
    if raw_value in (None, ""):
        return {
            "name": "status",
            "value": None,
            "value_type": "text",
            "status": "not_found",
        }
    if not isinstance(raw_value, str):
        return {
            "name": "status",
            "value": raw_value,
            "value_type": "text",
            "status": "invalid",
        }
    return {
        "name": "status",
        "value": raw_value,
        "value_type": "text",
        "status": "found",
    }


def evaluate(evidence, evaluations, metadata):
    expected_status = evaluations[0]["criteria"]["equals"]
    status_fact = _extract_status_fact(evidence)

    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [status_fact],
            "reason": "Unable to evaluate because the status fact could not be established.",
        }

    if status_fact["value"] == expected_status:
        return {
            "conclusion": "true",
            "facts": [status_fact],
            "reason": "Status matches the expected value.",
        }

    return {
        "conclusion": "false",
        "facts": [status_fact],
        "reason": f"Status is '{status_fact['value']}', not '{expected_status}'.",
    }
```

What the author should notice:

- fact extraction is a separate responsibility
- `inconclusive` is for “I cannot establish what I need”
- once this pattern is clear for one fact, it scales much better to typed facts and multiple facts

### What Can Go Wrong

Even when the caller input is valid, the evidence may still fail to support a decision:

- the field is missing
- the field is present but empty
- the field is present but cannot be parsed into the required type
- the field exists but is the wrong shape for the expected fact

That is why this stage is about explicit `inconclusive` handling, not a separate `error` conclusion.

### Why This Stage Is Not Enough Yet

Once a test depends on several facts, it still has to decide whether to stop early or gather more information first.

### What The Next Stage Adds

The next stage introduces the deliberate choice between:

- fail fast
- fail slow

### Canonical Fixtures

Primary live references:

- [verify_review_date_range.py](../../../tests/json/test_of_detail/verify_review_date_range.py)
- [verify_restore_duration_range.py](../../../tests/json/test_of_detail/verify_restore_duration_range.py)
- [verify_service_owner_required.py](../../../tests/json/test_of_detail/verify_service_owner_required.py)

## Stage 4: Choose Fail Fast Or Fail Slow

### Goal

Choose how the test behaves when one or more required facts cannot be established.

### What You Are Doing Here

At this stage, the question is no longer:

- can the test validate its contract?
- can the test establish facts?

Those earlier stages already answered that.

The question now is:

- when fact establishment fails, should the test stop immediately or keep gathering fact context first?

This is an authoring decision.

It is not a runtime switch in the evaluator.

### Fail Fast

Fail fast means:

- stop as soon as one required fact cannot be established
- return `inconclusive` immediately

Good for:

- simple policies
- simpler control flow
- easier starting implementations

### Fail Slow

Fail slow means:

- try to establish all relevant facts first
- then return `inconclusive` with the fuller fact picture if evaluation cannot proceed

Good for:

- better diagnostics
- multi-fact policies
- richer evidence explanations

### Example Contrast

Assume a test depends on two facts:

- `coverage`
- `branch_coverage`

Assume the evidence yields:

- `coverage` as `found`
- `branch_coverage` as `not_found`

Fail-fast behavior:

- establish `coverage`
- fail to establish `branch_coverage`
- return immediately

Typical fail-fast result:

```json
{
  "conclusion": "inconclusive",
  "facts": [
    {
      "name": "branch_coverage",
      "value": null,
      "value_type": "number",
      "status": "not_found"
    }
  ],
  "reason": "Unable to evaluate because the branch_coverage fact could not be established."
}
```

Fail-slow behavior:

- establish `coverage`
- fail to establish `branch_coverage`
- still return the fuller fact picture that was gathered

Typical fail-slow result:

```json
{
  "conclusion": "inconclusive",
  "facts": [
    {
      "name": "coverage",
      "value": 84.0,
      "value_type": "number",
      "status": "found"
    },
    {
      "name": "branch_coverage",
      "value": null,
      "value_type": "number",
      "status": "not_found"
    }
  ],
  "reason": "Unable to evaluate because one or more required facts could not be established."
}
```

### What You Can Ignore For Now

You do not need to redesign the policy logic yet.

At this stage, focus only on:

- fact-establishment flow
- diagnostic depth
- whether the test should return early or continue gathering context

### Why This Choice Matters

Both strategies are valid.

They differ in:

- how much code you have to manage
- how much diagnostic detail you return
- how easy it is to reason about the control flow

That means this is one of the first places where simplicity and diagnosability trade off directly.

### Recommendation

If you are unsure where to start:

- start fail fast first
- grow into fail slow when the policy complexity or diagnostic value justifies it

### How To Write This Python

At this stage, do not change the outer result contract.

Change the fact-establishment control flow.

Good writing order:

1. keep your existing extraction helpers
2. decide whether the test should return on the first missing fact or gather all facts first
3. make that choice explicit in one block of code
4. keep the returned `inconclusive` reason specific to the strategy you chose

Fail-fast intermediate shape:

```python
def evaluate(evidence, evaluations, metadata):
    coverage_fact = _extract_measure_fact(evidence, "coverage")
    if coverage_fact["status"] != "found":
        return _build_inconclusive_result(
            [coverage_fact],
            "Unable to evaluate because the coverage fact could not be established.",
        )

    branch_fact = _extract_measure_fact(evidence, "branch_coverage")
    if branch_fact["status"] != "found":
        return _build_inconclusive_result(
            [branch_fact],
            "Unable to evaluate because the branch_coverage fact could not be established.",
        )

    return _evaluate_policy(coverage_fact, branch_fact)
```

Fail-slow intermediate shape:

```python
def evaluate(evidence, evaluations, metadata):
    facts = {
        "coverage": _extract_measure_fact(evidence, "coverage"),
        "branch_coverage": _extract_measure_fact(evidence, "branch_coverage"),
    }
    missing_or_invalid = [
        fact for fact in facts.values() if fact["status"] != "found"
    ]
    if missing_or_invalid:
        return _build_inconclusive_result(
            list(facts.values()),
            "Unable to evaluate because one or more required facts could not be established.",
        )

    return _evaluate_policy(facts["coverage"], facts["branch_coverage"])
```

What the author should notice:

- stage 4 is mostly about one decision point in control flow
- fail fast and fail slow can use the same extraction helpers
- this is still not the stage where you need a large helper architecture
- the main goal is to make the establishment strategy deliberate and readable

### Canonical Fixtures

Use these two fixtures as the primary comparison pair:

- [verify_dual_coverage_fail_fast.py](../../../tests/json/test_of_detail/verify_dual_coverage_fail_fast.py)
- [verify_dual_coverage_thresholds.py](../../../tests/json/test_of_detail/verify_dual_coverage_thresholds.py)

Use this companion guide for the detailed pattern discussion:

- [Fact Establishment Patterns](fact-establishment-patterns.md)

### Why This Stage Comes Before Helper Decomposition

This is still a responsibility decision, not a formatting decision.

The test should decide how it fails before it decides how to organize helpers around that behavior.

### Why This Stage Is Not Enough Yet

Once the failure strategy is chosen, the test still needs an internal structure that keeps validation, extraction, and evaluation readable.

### What The Next Stage Adds

The next stage turns the responsibilities you have already defined into a maintainable helper layout.

## Part 3: Make It Maintainable And Scalable

This part is about internal structure and richer policy growth.

The goal is to make tests:

- easier to read
- easier to extend
- better aligned to real multi-fact and typed evaluation needs

## Stage 5: Separate The Test Into Small Helpers

### Goal

Refactor the now-clear responsibilities into a cleaner internal structure.

### What You Are Doing Here

Once the test already knows:

- what it expects
- what facts it needs
- how it fails

then the helper structure becomes much more natural.

Recommended breakout:

- `_validate_metadata(...)`
- `_index_evaluations(...)`
- `_extract_facts(...)`
- `_find_missing_or_invalid_facts(...)`
- `_evaluate_policy(...)`
- `_build_inconclusive_result(...)`
- `_build_inconclusive_result(...)`

Compact skeleton:

```python
def evaluate(evidence, evaluations, metadata):
    _validate_metadata(metadata)
    indexed_evaluations = _index_evaluations(evaluations)
    facts = _extract_facts(evidence, indexed_evaluations)
    blocking_facts = _find_missing_or_invalid_facts(facts)
    if blocking_facts:
        return _build_inconclusive_result(blocking_facts)
    return _evaluate_policy(facts, indexed_evaluations)
```

### How To Write This Python

Do not start by splitting everything into many helpers at once.

Refactor in passes.

Good writing order:

1. copy the working stage-4 file
2. circle the repeated responsibility blocks:
   - metadata checks
   - evaluation lookup
   - fact extraction
   - fact-establishment checks
   - policy reasoning
3. move one responsibility at a time into a helper
4. rerun the test after each extraction
5. stop when the file becomes clearly readable, not when it reaches some arbitrary helper count

Safe refactor sequence:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    policy_error = _validate_policy_inputs(evaluation_index)
    if policy_error is not None:
        return policy_error

    facts = _extract_facts(evidence, evaluation_index)
    blocking_result = _handle_unestablished_facts(facts)
    if blocking_result is not None:
        return blocking_result

    return _evaluate_policy(facts, evaluation_index)
```

One reasonable helper extraction order:

1. `_validate_metadata(...)`
2. `_index_evaluations(...)`
3. `_extract_facts(...)`
4. `_handle_unestablished_facts(...)`
5. `_evaluate_policy(...)`
6. small result builders if the file now benefits from them

What the author should notice:

- stage 5 is a refactor stage, not a new policy stage
- each helper should own one responsibility clearly
- helper names should describe real responsibilities, not vague processing
- if the refactor makes the file harder to follow, it is probably too aggressive

### Why Each Helper Exists

- `_validate_metadata(...)`
  Keeps evaluator-owned contract checks separate from domain reasoning.
- `_index_evaluations(...)`
  Gives the test a stable way to look up caller-owned criteria.
- `_extract_facts(...)`
  Isolates evidence reading and parsing from evaluation logic.
- `_find_missing_or_invalid_facts(...)`
  Makes fact-establishment decisions explicit and testable.
- `_evaluate_policy(...)`
  Keeps the actual domain logic readable.
- result builders
  Keep returned contract shape consistent.

### What You Can Ignore For Now

You do not need to create a mini-framework.

The goal is not abstraction for its own sake.

The goal is:

- readable responsibilities
- easier maintenance
- easier debugging
- easier reuse of internal patterns

### Example Guidance

Two good comparison points:

- [verify_author_complete.py](../../../tests/json/test_of_detail/verify_author_complete.py)
- [verify_review_date_range.py](../../../tests/json/test_of_detail/verify_review_date_range.py)

The first shows a simpler helper breakout.

The second shows why typed parsing and stronger diagnostics make helper separation more valuable.

For the full recommended default shape, use:

- [Scaffold Guide](scaffold.md)

### Why This Stage Comes Here

Helper decomposition is important, but it is a consequence of clarified responsibilities.

It should not be introduced as if code organization is the first hardening step.

### What Can Go Wrong

Common overcorrections at this stage:

- too much logic remains in `evaluate(...)`, so the structure never really improves
- too much abstraction gets introduced, so a simple test becomes harder to read
- fact extraction and policy evaluation get mixed together again under vague helper names

The right target is a readable default, not an elaborate architecture.

### Why This Stage Is Not Enough Yet

The test may now be clean and safe for one subject, but many real policies depend on:

- several facts
- several criteria values
- typed parsing
- richer policy logic

That is the final growth stage.

### What The Next Stage Adds

The next stage shows how to grow complexity in controlled steps instead of jumping from a one-subject starter test straight to advanced domain logic.

## Stage 6: Scale Up To Richer Typed And Multi-Subject Logic

### Goal

Move from one-subject starter tests to the more complete shapes the library supports.

### What You Are Doing Here

At this stage, do not think in terms of:

- "now I need a new evaluator feature"

Think in terms of:

- "now I need one more dimension of test-owned reasoning"

That additional dimension might be:

- richer criteria for one subject
- typed parsing for one subject
- structural comparison for one subject
- multi-subject reasoning across several facts

### Recommended Growth Ladder

Grow one step at a time:

1. one text fact with one `equals` criterion
2. one numeric fact with one `minimum` criterion
3. one numeric fact with `minimum` and `maximum`
4. one typed fact such as `date`, `datetime`, or `duration`
5. one structural fact such as `array`, `object`, or explicit `null`
6. two or more subjects used together in one policy decision

This keeps the test understandable while still allowing real policy complexity.

### Pattern Families To Know

Typed scale-up examples:

| Pattern family | What changes | Example fixture |
| --- | --- | --- |
| numeric range | one fact, richer criteria | `verify_component_coverage_range.py` |
| integer range | one fact, integer-specific typing | `verify_build_age_days_range.py` |
| datetime range | one fact, typed temporal parsing | `verify_last_review_timestamp_range.py` |
| date range | one fact, typed calendar comparison | `verify_review_date_range.py` |
| duration range | one fact, typed elapsed-time parsing | `verify_restore_duration_range.py` |
| object equals | one structural fact | `verify_approver_profile_equals.py` |
| array equals | one structural fact | `verify_reviewer_roles_equals.py` |
| null equals | one explicit null-state fact | `verify_revocation_reason_null.py` |
| multi-subject conjunction | several facts, one combined decision | `verify_dual_coverage_thresholds.py` |

### Example Growth Path

You might grow from:

- `status equals`

to:

- `coverage minimum`

to:

- `coverage plus branch_coverage`

to:

- typed temporal checks

and then to:

- structural equality or explicit `null` checks

and then to:

- multi-subject reasoning where several facts influence one result

### What This Stage Is Really Teaching

The important lesson is not just that the library supports more shapes.

The important lesson is:

- the caller can still change criteria without rewriting the core test shape
- typed parsing belongs in the Python test
- richer reasoning belongs in the Python test
- the evaluator transport should stay simple while the test logic grows as needed

### How To Write This Python

At this stage, do not throw away the stage-5 file and start over.

Grow one new dimension at a time.

Good writing order:

1. start from a helper-structured one-subject test
2. add one richer pattern only:
   - one typed fact
   - or one structural fact
   - or one additional subject
3. make that pattern work end to end
4. only then add the next dimension
5. if a derived fact is needed, add it after the prerequisite raw facts are already stable

Safe scale-up sequence:

1. one subject with one criterion
2. one subject with richer criteria such as `minimum` plus `maximum`
3. one typed parsing helper
4. one public-fact helper if the internal parsed state is richer than the returned fact
5. one second subject
6. one combined policy helper
7. one derived-fact helper if the policy needs computed values

Good intermediate shape:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    policy_error = _validate_policy_inputs(evaluation_index)
    if policy_error is not None:
        return policy_error

    facts = _extract_facts(evidence, evaluation_index)
    blocking_result = _handle_unestablished_facts(facts)
    if blocking_result is not None:
        return blocking_result

    derived_facts = _derive_facts(facts, evaluation_index)
    derived_blocking_result = _handle_unestablished_facts(derived_facts)
    if derived_blocking_result is not None:
        return derived_blocking_result

    return _evaluate_policy(facts, derived_facts, evaluation_index)
```

What the author should add in order:

1. `_validate_policy_inputs(...)`
   Make the required subjects and criteria explicit.
2. `_extract_facts(...)`
   Add one new fact family at a time.
3. `_handle_unestablished_facts(...)`
   Reuse the same discipline as earlier stages.
4. `_derive_facts(...)`
   Only when the new pattern truly needs computed facts.
5. `_evaluate_policy(...)`
   Keep the actual reasoning here.

What the author should notice:

- stage 6 is a controlled growth stage, not a rewrite stage
- advanced tests usually stay readable when each new dimension gets one helper or one narrow responsibility block
- typed parsing, structural comparison, and derived facts should be added only after the simpler version already works
- if the file starts becoming hard to follow, stop adding dimensions and split responsibilities more clearly before going further

### Where To Look Next

Use these companion docs deliberately:

- [Authoring Examples Index](authoring-examples-index.md)
  Use this to choose the right fixture to copy next.
- [Evaluation Input Patterns](evaluation-input-patterns.md)
  Use this to choose the simplest viable caller-owned input shape.
- [Scaffold Guide](scaffold.md)
  Use this when the richer logic needs a cleaner internal structure.
- [Advanced Authoring Patterns](advanced-authoring-patterns.md)
  Use this when the test has outgrown simple one-subject or one-pattern authoring.

### What Still Comes Later

Only after this stage should you start reaching for:

- tiered logic
- conditional policies
- lookup-style reasoning
- more specialized domain logic

## Practical Recommendation

If you are brand new and want the most practical path:

1. write the hardcoded starter test
2. run it successfully against real evidence
3. move one hardcoded rule into `evaluations`
4. add defensive validation
5. make fact establishment explicit
6. choose fail fast first
7. refactor into helpers
8. add richer typed or multi-subject logic
9. only then move into more advanced policy shapes

## Where To Go Next

After this progression:

- use [Authoring Examples Index](authoring-examples-index.md) to choose a fixture by difficulty or domain
- use [Scaffold Guide](scaffold.md) for the recommended internal structure
- use [Fact Extraction](fact-extraction.md) and [Fact Establishment Patterns](fact-establishment-patterns.md) to deepen stages 3 and 4
- use [Evaluation Input Patterns](evaluation-input-patterns.md) to choose the right caller-owned input shape
- use [Advanced Authoring Patterns](advanced-authoring-patterns.md) when your test needs multi-subject, typed, structural, or derived-fact scaling guidance
