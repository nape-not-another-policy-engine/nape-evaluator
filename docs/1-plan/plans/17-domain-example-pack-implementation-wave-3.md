# Plan 17: Domain Example Pack Implementation Wave 3

## Purpose

Implement the third domain-rich example pack as executable evaluator examples and routing docs.

Wave 3 starts with transportation inspection freshness assurance.

## Why This Exists

The first two domain-rich packs now cover privileged access and utility / field restore readiness.

The next gap is a transportation-focused operational example family built around inspection status and freshness.

## Selected Direction

The implemented pack will be:

- transportation inspection freshness assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent transportation inspection evidence family
2. inspection status fixture
3. inspection freshness fixture
4. one combined vehicle inspection readiness fixture
5. example-index and domain-doc updates
6. automated validation

## Guardrails

- stay inside the current V2 contract
- keep the examples fact-verification-centered
- do not hide caller-owned criteria inside hardcoded test logic
- keep combined logic bounded and easy to read

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new transportation inspection evidence fixtures:
  - `tests/json/evidence/transport_inspection_current.json`
  - `tests/json/evidence/transport_inspection_stale.json`
  - `tests/json/evidence/transport_inspection_incomplete.json`
- new transportation single-subject fixtures:
  - `tests/json/test_of_detail/verify_transport_inspection_status_completed.py`
  - `tests/json/test_of_detail/verify_transport_inspection_recent.py`
- new transportation combined fixture:
  - `tests/json/test_of_detail/verify_transport_inspection_readiness.py`
- pattern-library coverage added in:
  - `tests/json/test_pattern_library.py`
- routing and domain docs updated in:
  - `docs/user/v2-test-authoring/domain-examples.md`
  - `docs/user/v2-test-authoring/authoring-examples-index.md`

Validation completed:

- `python3 -m unittest tests.json.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

Closure review result:

- the transportation inspection pack is complete enough to serve as the third domain-rich exemplar
- the next wave should move to manufacturing maintenance release and work-order assurance
