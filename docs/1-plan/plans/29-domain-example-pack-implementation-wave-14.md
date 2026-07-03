# Plan 29: Domain Example Pack Implementation Wave 14

## Purpose

Implement the fourteenth domain-rich example pack as executable evaluator examples and routing docs.

Wave 14 starts with aviation or maintenance return-to-service assurance.

## Why This Exists

The first thirteen domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, payment settlement readiness, medical device release packet readiness, regulated quality batch release readiness, cold-chain exception readiness, system-of-systems event confirmation readiness, IT / OT boundary readiness, application release readiness, mission access review readiness, and fleet telematics reconciliation readiness.

The next gap is an explicit safety-return example family centered on maintenance release, hazard closure, and calibration readiness before return to service.

## Selected Direction

The implemented pack will be:

- aviation or maintenance return-to-service assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent return-to-service evidence family
2. maintenance release status fixture
3. hazard closure status fixture
4. calibration current fixture
5. one combined return-to-service readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new return-to-service evidence fixtures:
  - `tests/json/evidence/return_to_service_ready.json`
  - `tests/json/evidence/return_to_service_open_hazard.json`
  - `tests/json/evidence/return_to_service_blocked.json`
- new return-to-service single-subject fixtures:
  - `tests/json/test_of_detail/verify_return_to_service_maintenance_release_approved.py`
  - `tests/json/test_of_detail/verify_return_to_service_hazard_closure_closed.py`
  - `tests/json/test_of_detail/verify_return_to_service_calibration_current.py`
- new return-to-service combined fixture:
  - `tests/json/test_of_detail/verify_return_to_service_readiness.py`
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

- the aviation or maintenance return-to-service pack is complete enough to serve as the fourteenth domain-rich exemplar
- the cross-pack progression now includes an explicit safety return-to-service example family in addition to the prior authorization, operational, reconciliation, release, and mission-governance packs
