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

## V1 Evidence Input

Committed V1 passes evidence as text lines:

```python
[
    "{\n",
    '  "author": "Bill Bensing",\n',
    '  "status": "complete"\n',
    "}\n",
]
```

If the evidence is JSON, parse it inside the test:

```python
import json


def evaluate(evidence):
    data = json.loads("".join(evidence))
    if data.get("status") == "complete":
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

## V2 Candidate Evidence Input

Typed evidence loading is candidate V2 behavior. If accepted, `evaluate(evidence)` may receive different object types based on evidence extension:

- JSON: Python object from `json.load`
- XML: `xml.etree.ElementTree` root element
- YAML: Python object from `yaml.safe_load`
- PDF: extracted text lines
- TXT or unknown: text lines

Tests written for V1 text lines may need migration if V2 typed loading becomes official.
