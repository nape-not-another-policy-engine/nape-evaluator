# Examples

This folder documents small evaluator examples. The examples are shown here as documentation snippets so they do not interfere with the current code WIP.

## V1 Text-Line JSON Example

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

## Recommended Future Smoke Fixtures

Add fixtures for:

- pass
- fail
- inconclusive
- error

Keep V1 text-line fixtures separate from V2 typed-evidence fixtures if typed loading is accepted.
