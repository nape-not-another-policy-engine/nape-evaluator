# Evidence Formats

## Current Typed Loading

| Extension | Input to `evaluate(evidence)` |
| --- | --- |
| `.txt` | text lines |
| `.json` | parsed JSON object |
| `.xml` | XML root element |
| `.yaml`, `.yml` | parsed YAML object |
| `.pdf` | extracted text lines |
| unknown | text lines |

Structured data parsing for JSON, XML, and YAML now happens in evaluator core rather than inside the test file.

## Historical V1 Contrast

Historical V1 treated every evidence file as text and passed `readlines()` into `evaluate(evidence)`. Tests written for that contract may fail until they are migrated to the current typed-evidence model.
