> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 13 Handoff: Evidence Format Example Deepening

## Status

Complete.

## Resume Goal

Deepen the format-specific authoring examples so they teach ambiguity handling and negative-path fact establishment, not just the first-wave happy paths.

## Selected Direction

The selected direction is:

- keep the current V2 contract unchanged
- extend the format example library rather than redesigning transport or criteria
- focus the next wave on:
  - XML namespaces
  - YAML typed invalid-fact handling
  - text ambiguity
  - PDF ambiguity
  - reader routing by failure mode and domain feel

## Constraints

- examples should stay small and copyable
- public-interface tests should stay bounded
- ambiguity should generally resolve to `inconclusive` when the fact cannot be cleanly established
- the examples should remain about verification of facts, not embedding a new policy language into transport

## What Landed

- XML namespace-aware example:
  - `tests/xml/evidence/author_verification_namespaced.xml`
  - `tests/xml/test_of_detail/verify_author_complete_namespaced.py`
- YAML invalid typed-fact example:
  - `tests/yaml/evidence/component_assurance_invalid_coverage.yaml`
  - `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`
- text ambiguity example:
  - `tests/text/evidence/author_verification_ambiguous_status.txt`
  - `tests/text/test_of_detail/verify_author_complete_ambiguous.py`
- PDF ambiguity example:
  - `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`
- routing updates in:
  - `docs/user/v2-test-authoring/evidence-format-authoring.md`
  - `docs/user/v2-test-authoring/authoring-examples-index.md`

## Validation Performed

- `python3 -m unittest tests.xml.test_pattern_library tests.yaml.test_pattern_library tests.text.test_pattern_library tests.pdf.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

## Follow-On Direction

No immediate follow-on is required for this scope.

If this area is expanded later, the natural next step is broader domain-rich evidence sets rather than more low-level extraction mechanics.

## Primary Files

- `docs/product/current-evaluator-reference.md`
- `docs/reference/evidence-formats.md`
- `docs/user/v2-test-authoring/evidence-format-authoring.md`
- `docs/user/v2-test-authoring/authoring-examples-index.md`
- `tests/xml/`
- `tests/yaml/`
- `tests/text/`
- `tests/pdf/`
