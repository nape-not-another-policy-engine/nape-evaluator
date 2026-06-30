# Test-Of-Detail Authoring

A test-of-detail file is a Python file loaded by `nape-eval`.

## Required Function

Define:

```python
def evaluate(evidence):
    return "pass", "Reason text"
```

The function must return two values:

- `outcome`
- `reason`

## Evidence Input

The evaluator passes evidence into `evaluate(evidence)` based on the evidence file extension:

- JSON: Python object from `json.load`
- XML: `xml.etree.ElementTree` root element
- YAML: Python object from `yaml.safe_load`
- PDF: extracted text lines
- TXT or unknown: text lines

Example JSON input:

```python
{
    "author": "Bill Bensing",
    "status": "complete",
}
```

If the evidence is JSON, read it directly as a Python object:

```python
def evaluate(evidence):
    if evidence.get("status") == "complete":
        return "pass", "Status is complete."
    return "fail", "Status is not complete."
```

## Recommended Outcome Use

Use `pass` when the evidence satisfies the test.

Use `fail` when the evidence is present and valid but does not satisfy the test.

Use `inconclusive` when the evidence is missing expected fields or cannot support a decision.

Use `error` when the test itself cannot run as intended.

## Authoring Rules

- Keep tests deterministic.
- Return a concise human-readable reason.
- Do not print extra output from the test file.
- Do not depend on local machine state unless that state is part of the evidence.
- Handle missing fields explicitly.
- Treat test files as executable code; do not publish or run tests that perform unrelated filesystem, network, credential, or destructive operations.

## Historical Note

The V1 baseline passed every evidence file as text lines. Tests written for that older contract may need migration if they parse structured content inside `evaluate(...)`.
