# Plan 18: Domain Example Pack Implementation Wave 4

## Purpose

Implement the fourth domain-rich example pack as executable evaluator examples and routing docs.

Wave 4 starts with manufacturing maintenance release and work-order assurance.

## Why This Exists

The first three domain-rich packs now cover privileged access, utility / field restore readiness, and transportation inspection freshness.

The next gap is a manufacturing-focused operational integrity example family centered on line restart readiness.

## Selected Direction

The implemented pack will be:

- manufacturing maintenance release and work-order assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent manufacturing line-restart evidence family
2. maintenance release status fixture
3. work-order completion fixture
4. restart authorization status fixture
5. one combined line restart readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new manufacturing line-restart evidence fixtures:
  - `tests/json/evidence/manufacturing_line_restart_ready.json`
  - `tests/json/evidence/manufacturing_line_restart_incomplete_work_order.json`
  - `tests/json/evidence/manufacturing_line_restart_blocked.json`
- new manufacturing single-subject fixtures:
  - `tests/json/test_of_detail/verify_manufacturing_maintenance_release_approved.py`
  - `tests/json/test_of_detail/verify_manufacturing_work_order_complete.py`
  - `tests/json/test_of_detail/verify_manufacturing_restart_authorization_approved.py`
- new manufacturing combined fixture:
  - `tests/json/test_of_detail/verify_manufacturing_line_restart_readiness.py`
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

- the manufacturing pack is complete enough to serve as the fourth domain-rich exemplar
