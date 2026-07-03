# Plan 22: Domain Example Pack Implementation Wave 7

## Purpose

Implement the seventh domain-rich example pack as executable evaluator examples and routing docs.

Wave 7 starts with pharmaceutical or laboratory regulated quality release assurance.

## Why This Exists

The first six domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, payment settlement readiness, and medical device release packet readiness.

The next gap is a regulated quality and information-integrity example family centered on batch release, reviewer presence, and exception closure before release.

## Selected Direction

The implemented pack will be:

- pharmaceutical or laboratory regulated quality release assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent regulated quality batch-release evidence family
2. batch release status fixture
3. quality reviewer present fixture
4. deviation closed fixture
5. one combined regulated quality release readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new regulated quality evidence fixtures:
  - `tests/json/evidence/quality_batch_release_ready.json`
  - `tests/json/evidence/quality_batch_release_missing_reviewer.json`
  - `tests/json/evidence/quality_batch_release_open_deviation.json`
- new regulated quality single-subject fixtures:
  - `tests/json/test_of_detail/verify_quality_batch_release_status_released.py`
  - `tests/json/test_of_detail/verify_quality_reviewer_present.py`
  - `tests/json/test_of_detail/verify_quality_deviation_closed.py`
- new regulated quality combined fixture:
  - `tests/json/test_of_detail/verify_quality_batch_release_readiness.py`
- pattern-library coverage added in:
  - `tests/json/test_pattern_library.py`
- routing and domain docs updated in:
  - `docs/user/v2-test-authoring/domain-examples.md`
  - `docs/user/v2-test-authoring/authoring-examples-index.md`
  - `docs/user/v2-test-authoring/domain-packs-overview.md`

Validation completed:

- `python3 -m unittest tests.json.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

Closure review result:

- the regulated quality batch release pack is complete enough to serve as the seventh domain-rich exemplar
- the cross-pack progression now extends from authorization and operations through business-process, safety-critical product, and regulated quality assurance
