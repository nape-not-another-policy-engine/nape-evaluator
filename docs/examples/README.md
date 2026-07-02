# Examples

This folder documents small evaluator examples. The examples are kept as documentation snippets so they do not interfere with the main implementation or automated tests.

## Historical V1 Text-Line JSON Example

Evidence file:

```json
{
  "author": "Bill Bensing",
  "status": "complete"
}
```

Test-of-detail file:

```python
import json


def evaluate(evidence_file):
    data = json.loads("".join(evidence_file))
    if data.get("status") == "complete":
        return "pass", "The author has achieved the status of complete."
    return "fail", "The author has not achieved the status of complete."
```

Command:

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

Keep this example as historical reference only. It reflects the pre-typed V1 contract, not the current evaluator contract.

## Current V2 JSON Example

Evidence file:

```json
{
  "author": "Bill Bensing",
  "status": "complete"
}
```

Test-of-detail file:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    expected_status = evaluations[0]["criteria"]["equals"]
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

    if status == expected_status:
        return {
            "conclusion": "true",
            "facts": [fact],
            "reason": "The author has achieved the expected status.",
        }

    return {
        "conclusion": "false",
        "facts": [fact],
        "reason": "The author has not achieved the expected status.",
    }
```

Command:

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke '{"test":"./verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

Expected output shape:

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
        "reason": "The author has achieved the expected status."
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

This successful case shows the normal ownership split:

- `results[0].result.reason` is the completed test's reasoning
- `evaluator.messages` is empty because the evaluator had no operational notice to report

## Current V2 Multi-Test Shared-Warning Example

Evidence file with no extension:

```json
{
  "author": "Bill Bensing",
  "status": "complete"
}
```

Requested tests:

```json
{
  "evidence": "./author_verification",
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
    },
    {
      "test": "./verify_author_approved.py",
      "evaluations": [
        {
          "subject": {
            "name": "status",
            "data_type": "text"
          },
          "criteria": {
            "equals": "approved"
          }
        }
      ]
    }
  ]
}
```

Representative output shape:

```json
{
  "results": [
    {
      "test": "./verify_author_approved.py",
      "evidence": "./author_verification",
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "true",
        "reason": "The author has achieved the expected status."
      }
    },
    {
      "test": "./verify_author_approved.py",
      "evidence": "./author_verification",
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "false",
        "reason": "The author has not achieved the expected status."
      }
    }
  ],
  "evaluator": {
    "messages": [
      {
        "scope": "request",
        "level": "warning",
        "source": "evaluator",
        "code": "missing_extension_text_fallback",
        "message": "Evidence file had no extension and was evaluated as text.",
        "evidence_file": "./author_verification",
        "test_file": null,
        "affected_tests": [
          "./verify_author_complete.py",
          "./verify_author_approved.py"
        ],
        "stack_trace": null
      }
    ],
    "summary": {
      "count": 2,
      "ran": 2,
      "true": 1,
      "false": 1,
      "inconclusive": 0,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 1,
      "message_error": 0
    }
  }
}
```

This example shows:

- `result.reason` belongs to each completed test result
- evaluator warnings stay under `evaluator.messages`
- the current runtime counts this shared warning once as a distinct request-scoped event

## Current V2 Blocked-Test Example

If the evaluator cannot load or execute a requested test, the completed test does not provide a `reason` because it never completed. The evaluator synthesizes the blocked-result reasoning instead.

Representative blocked output shape:

```json
{
  "results": [
    {
      "test": "./missing_test.py",
      "evidence": "./author_verification.json",
      "execution": {
        "executed": false,
        "status": "blocked"
      },
      "result": {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": "The test could not be completed, so the conclusion is inconclusive. The evaluator could not find the test file."
      }
    }
  ],
  "evaluator": {
    "messages": [
      {
        "scope": "test",
        "level": "error",
        "source": "evaluator",
        "code": "test_file_not_found",
        "message": "Unable to find the file(s) for evaluation. [Errno 2] ...",
        "evidence_file": "./author_verification.json",
        "test_file": "./missing_test.py",
        "affected_tests": null,
        "stack_trace": "Traceback (most recent call last): ..."
      }
    ],
    "summary": {
      "count": 1,
      "ran": 0,
      "true": 0,
      "false": 0,
      "inconclusive": 1,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 1
    }
  }
}
```

This blocked case shows the difference clearly:

- `results[0].result.reason` is evaluator-generated blocked-result reasoning
- the evaluator explains the operational problem through `evaluator.messages`
- `summary.message_error` increases

## Recommended Future Smoke Fixtures

Add fixtures for:

- true
- false
- inconclusive
- blocked

Keep historical V1 text-line fixtures separate from current V2 fixtures.
