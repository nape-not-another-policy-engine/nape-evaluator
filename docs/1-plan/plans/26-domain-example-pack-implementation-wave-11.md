# Plan 26: Domain Example Pack Implementation Wave 11

## Purpose

Implement the eleventh domain-rich example pack as executable evaluator examples and routing docs.

Wave 11 starts with application verification assurance.

## Why This Exists

The first ten domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, payment settlement readiness, medical device release packet readiness, regulated quality batch release readiness, cold-chain exception readiness, system-of-systems event confirmation readiness, and IT / OT boundary readiness.

The next gap is an application-verification family centered on admin-path control state, vulnerability threshold, and deployment approval presence.

## Selected Direction

The implemented pack will be:

- application verification assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent application verification evidence family
2. MFA required fixture
3. critical vulnerability count fixture
4. deployment approval present fixture
5. one combined application verification readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new application verification evidence fixtures:
  - `tests/json/evidence/application_release_ready.json`
  - `tests/json/evidence/application_release_mfa_disabled.json`
  - `tests/json/evidence/application_release_blocked.json`
- new application verification single-subject fixtures:
  - `tests/json/test_of_detail/verify_application_mfa_required.py`
  - `tests/json/test_of_detail/verify_application_critical_vulnerability_count_maximum.py`
  - `tests/json/test_of_detail/verify_application_deployment_approval_present.py`
- new application verification combined fixture:
  - `tests/json/test_of_detail/verify_application_release_readiness.py`
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

- the application verification pack is complete enough to serve as the eleventh domain-rich exemplar
- the cross-pack progression now extends from infrastructure and boundary verification into software release verification
