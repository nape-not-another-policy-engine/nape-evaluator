# Quickstart

This quickstart shows the current typed-evidence evaluator contract.

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
def evaluate(evidence_file):
    status = evidence_file.get("status")

    if status == "complete":
        return "pass", "The author has achieved the status of complete."
    if status is None or status == "":
        return "inconclusive", "The expected data field 'status' does not contain a value."
    return "fail", f"The author has not achieved the status of complete, their current status is '{status}'."
```

For `.json` evidence, `nape-eval` passes `evidence_file` as a parsed Python object.

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

## Historical Note

The V1 baseline passed every evidence file as text lines. If you need the older contract for migration review, see `../product/v1-evaluator-baseline.md`.
