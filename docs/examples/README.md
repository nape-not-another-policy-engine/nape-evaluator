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
            "conclusion": "error",
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
      "error": 0,
      "message_count": 0,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 0
    }
  }
}
```

## Recommended Future Smoke Fixtures

Add fixtures for:

- true
- false
- inconclusive
- error

Keep historical V1 text-line fixtures separate from current V2 fixtures.
