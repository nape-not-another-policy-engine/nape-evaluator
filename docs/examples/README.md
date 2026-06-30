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

Expected output shape:

```json
{"outcome": "pass", "reason": "The author has achieved the status of complete."}
```

Keep this example as historical reference only. It reflects the pre-typed V1 contract, not the current evaluator output shape.

## Current Typed-JSON Example

Evidence file:

```json
{
  "author": "Bill Bensing",
  "status": "complete"
}
```

Test-of-detail file:

```python
def evaluate(evidence, metadata):
    if metadata.get("evidence_type") != "json":
        return "error", "The evidence metadata does not indicate JSON input."
    if evidence.get("status") == "complete":
        return "pass", "The author has achieved the status of complete."
    return "fail", "The author has not achieved the status of complete."
```

Command:

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

Expected output shape:

```json
{
  "results": [
    {
      "test": "./verify_author_complete.py",
      "outcome": "pass",
      "reason": "The author has achieved the status of complete."
    }
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 1,
      "ran": 1,
      "pass": 1,
      "fail": 0,
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

- pass
- fail
- inconclusive
- error

Keep historical V1 text-line fixtures separate from current typed-evidence fixtures.

Use the historical and current examples above as the basis for future local docs smoke fixtures.
