# Evidence Formats

## Current Typed Loading

| Extension | Input to `evaluate(evidence, evaluations, metadata)` |
| --- | --- |
| `.txt` | text lines |
| `.json` | parsed JSON object |
| `.xml` | XML root element |
| `.yaml`, `.yml` | parsed YAML object |
| `.pdf` | extracted text lines |
| unknown | text lines |

Structured data parsing for JSON, XML, and YAML happens in evaluator core rather than inside the test file.

For `.txt` and unknown extensions, the evaluator sets `metadata["evidence_type"]` to `text`.

## Known Unprocessable Extensions

The evaluator does not attempt text fallback for these extensions and instead returns `unprocessable_evidence_type`:

- `.png`
- `.jpg`
- `.jpeg`
- `.gif`
- `.bmp`
- `.tiff`
- `.webp`
- `.zip`
- `.gz`
- `.tar`
- `.mp3`
- `.mp4`
- `.mov`
- `.avi`
- `.exe`
- `.bin`

## Historical V1 Contrast

Historical V1 treated every evidence file as text and passed `readlines()` into `evaluate(evidence)`. Tests written for that contract need migration to the current typed-evidence model and three-argument test signature.
