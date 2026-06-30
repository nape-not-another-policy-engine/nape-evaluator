# Quickstart

This quickstart shows the committed V1 evaluator contract.

If you run from a local checkout that contains uncommitted V2 typed-evidence work, this example may not match the dirty worktree behavior. For local maintainer smoke guidance, see `../maintainers/local-development.md`.

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
import json


def evaluate(evidence_file):
    author_evidence = json.loads("".join(evidence_file))
    status = author_evidence.get("status")

    if status == "complete":
        return "pass", "The author has achieved the status of complete."
    if status is None or status == "":
        return "inconclusive", "The expected data field 'status' does not contain a value."
    return "fail", f"The author has not achieved the status of complete, their current status is '{status}'."
```

V1 passes `evidence_file` as text lines. The test function parses JSON itself.

## 3. Run The Evaluator

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

Expected output:

```json
{"outcome": "pass", "reason": "The author has achieved the status of complete."}
```

## 4. Check Install

```bash
nape-eval --check-install
```

Expected output:

```text
NAPE Evaluator CLI is installed and working.
```

## V2 Candidate Note

Typed evidence loading is under consideration in the current worktree. If accepted, JSON tests may receive a Python dict instead of text lines. Do not rely on that behavior for V1.
