# Evidence Formats

## V1 Baseline

Committed V1 treats every evidence file as text.

Implementation behavior:

```python
with open(args.evidence, "r") as f:
    text = f.readlines()
```

The test-of-detail receives a list of strings. Structured data parsing is the test author's responsibility.

## V1 JSON Example

Evidence:

```json
{
  "status": "complete"
}
```

Test:

```python
import json


def evaluate(evidence):
    data = json.loads("".join(evidence))
    return "pass", data["status"]
```

## V2 Candidate Typed Loading

The current worktree contains candidate typed loading behavior:

| Extension | Candidate input to `evaluate(evidence)` |
| --- | --- |
| `.txt` | text lines |
| `.json` | parsed JSON object |
| `.xml` | XML root element |
| `.yaml`, `.yml` | parsed YAML object |
| `.pdf` | extracted text lines |
| unknown | text lines |

This is not the V1 baseline. If accepted, it should be treated as a V2 contract change.

## Compatibility Risk

V1 tests often parse text lines manually. If V2 passes parsed objects, those tests may fail unless they are migrated or compatibility mode exists.
