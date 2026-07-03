# Plan 16: Domain Example Pack Implementation Wave 2

## Purpose

Implement the second domain-rich example pack as executable evaluator examples and routing docs.

Wave 2 starts with utility and field restore drill assurance.

## Why This Exists

The first domain-rich pack now covers privileged access approval and review assurance.

The next gap is an operational, IT / OT-adjacent example family that shows how the same evaluator model applies to recovery readiness and field operations.

## Selected Direction

The implemented pack will be:

- utility and field restore drill assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent restore-drill evidence family
2. restore drill status fixture
3. restore drill duration-threshold fixture
4. restore drill recency fixture
5. one combined restore readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Guardrails

- stay inside the current V2 contract
- keep the examples fact-verification-centered
- do not hide caller-owned criteria inside hardcoded test logic
- keep combined logic bounded and easy to read

## Work Steps

1. add the active plan and handoff
2. implement restore-drill evidence fixtures
3. implement restore-drill test-of-detail fixtures
4. add proving tests in `tests/json/test_pattern_library.py`
5. update authoring docs and domain map references
6. run targeted tests, full unit tests, and docs smoke
7. closure-review whether the restore-drill pack is complete enough to serve as the second domain-rich exemplar

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new utility / field restore-drill evidence fixtures:
  - `tests/json/evidence/utility_restore_drill_success.json`
  - `tests/json/evidence/utility_restore_drill_stale.json`
  - `tests/json/evidence/utility_restore_drill_over_duration.json`
- new restore-drill single-subject fixtures:
  - `tests/json/test_of_detail/verify_restore_drill_status_successful.py`
  - `tests/json/test_of_detail/verify_restore_drill_duration_within_threshold.py`
  - `tests/json/test_of_detail/verify_restore_drill_recent.py`
- new restore-drill combined fixture:
  - `tests/json/test_of_detail/verify_restore_drill_core_readiness.py`
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

- the restore-drill pack is complete enough to serve as the second domain-rich exemplar
- the next wave should move to transportation inspection freshness or manufacturing maintenance release rather than broadening this pack further
