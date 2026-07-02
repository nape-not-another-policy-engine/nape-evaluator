# Quickstart

This quickstart shows the current V2 evaluator contract.

## 1. Create Evidence

Create `author_verification.json`:

```json
{
  "author": "Bill Bensing",
  "status": "complete"
}
```

## 2. Create A Test Of Detail

Create `verify_author_complete.py`:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    expected_status = "complete"
    if evaluations:
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
            "reason": "The expected data field 'status' does not contain a value.",
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
        "reason": f"The author status is '{status}', not '{expected_status}'.",
    }
```

For `.json` evidence, `nape-eval` passes `evidence` as a parsed Python object, `evaluations` as the caller-owned evaluation array, and `metadata` with `evidence_type` and `schema_version`.

## 3. Run The Evaluator

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke '{"test":"./verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

Expected output:

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

For full CLI rules and blocked-execution behavior, see `cli-reference.md`.

## 4. Check Install

```bash
nape-eval --check-install
```

Expected output:

```text
NAPE Evaluator CLI is installed and working.
```

## Historical Note

The V1 baseline used `--test` and tuple-returning tests. If you need the older contract for migration review, see `../product/v1-evaluator-baseline.md`.
