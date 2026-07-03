# Plan 15: Domain Example Pack Implementation Wave 1

## Purpose

Implement the first domain-rich example pack as executable evaluator examples and routing docs.

Wave 1 starts with privileged access approval and review assurance.

## Why This Exists

The domain-mapping work now identifies realistic industries and example-pack candidates.

The next step is to turn at least one of those into concrete, copyable, tested fixtures rather than leaving the domain map as planning-only guidance.

## Selected Direction

The first implemented domain pack will be:

- privileged access approval and review assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent privileged-access evidence family
2. status approval fixture
3. approver-required fixture
4. review-recency fixture
5. one combined multi-subject privileged-access core-controls fixture
6. example-index and domain-doc updates
7. automated validation

## Guardrails

- stay inside the current V2 contract
- keep the examples fact-verification-centered
- do not hide caller-owned criteria inside hardcoded test logic
- keep combined logic bounded and easy to read

## Work Steps

1. add the active plan and handoff
2. implement privileged-access evidence fixtures
3. implement privileged-access test-of-detail fixtures
4. add proving tests in `tests/json/test_pattern_library.py`
5. update authoring docs and domain map references
6. run targeted tests, full unit tests, and docs smoke
7. closure-review whether the privileged-access pack is complete enough to serve as the first domain-rich exemplar

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new privileged-access evidence fixtures:
  - `tests/json/evidence/privileged_access_grant.json`
  - `tests/json/evidence/privileged_access_grant_missing_approver.json`
  - `tests/json/evidence/privileged_access_grant_stale_review.json`
- new privileged-access single-subject fixtures:
  - `tests/json/test_of_detail/verify_privileged_access_status_approved.py`
  - `tests/json/test_of_detail/verify_privileged_access_approver_required.py`
  - `tests/json/test_of_detail/verify_privileged_access_review_recent.py`
- new privileged-access combined fixture:
  - `tests/json/test_of_detail/verify_privileged_access_core_controls.py`
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

- the privileged-access pack is complete enough to serve as the first domain-rich exemplar
- the next wave should move to one of the remaining planned operational packs rather than expanding this pack sideways immediately
