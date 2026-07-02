> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 12 Handoff: Evidence Format Authoring Guides And Examples

## Status

Complete.

## Resume Goal

Extend the V2 authoring docs and executable example library so authors can learn how to write tests against the supported evidence families without inferring the extraction model from loader tests or JSON-only fixtures.

## Selected Direction

The selected direction is:

- add one permanent format-authoring guide under `docs/user/v2-test-authoring/`
- make the guide-set structure and fixture-tree structure explicit in user docs
- add one first-wave parallel example set for JSON, XML, YAML, text, and PDF

## Constraints

- keep the current evaluator boundary unchanged
- keep the current V2 `subject` / `criteria` model unchanged
- keep public-interface tests small
- prefer controlled seams for PDF rather than fragile binary-maintenance-heavy tests

## What Landed

- `docs/user/v2-test-authoring/evidence-format-authoring.md`
- routing updates in:
  - `docs/user/v2-test-authoring/README.md`
  - `docs/user/v2-test-authoring/overview.md`
  - `docs/user/v2-test-authoring/fact-extraction.md`
  - `docs/user/v2-test-authoring/authoring-examples-index.md`
  - `docs/user/test-of-detail-authoring.md`
  - `docs/reference/evidence-formats.md`
- `tests/README.md`
- executable format-specific example trees:
  - `tests/xml/`
  - `tests/yaml/`
  - `tests/text/`
  - `tests/pdf/`

## Validation Performed

- `python3 -m unittest tests.xml.test_pattern_library tests.yaml.test_pattern_library tests.text.test_pattern_library tests.pdf.test_pattern_library tests.json.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

## Follow-On Direction

No immediate follow-on is required for the selected first-wave scope.

If this area is expanded later, the most natural next step is richer negative-path and domain-rich format examples rather than more transport or contract redesign.

## Primary Files

- `docs/product/current-evaluator-reference.md`
- `docs/reference/evidence-formats.md`
- `docs/user/test-of-detail-authoring.md`
- `docs/user/v2-test-authoring/README.md`
- `docs/user/v2-test-authoring/overview.md`
- `docs/user/v2-test-authoring/fact-extraction.md`
- `docs/user/v2-test-authoring/authoring-examples-index.md`
- `tests/json/test_pattern_library.py`
- `tests/test_structured_evidence_loading.py`
- `tests/test_pdf_evidence_loading.py`
