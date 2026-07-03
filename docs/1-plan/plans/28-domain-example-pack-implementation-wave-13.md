# Plan 28: Domain Example Pack Implementation Wave 13

## Purpose

Implement the thirteenth domain-rich example pack as executable evaluator examples and routing docs.

Wave 13 starts with fleet or telematics reconciliation assurance.

## Why This Exists

The first twelve domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, payment settlement readiness, medical device release packet readiness, regulated quality batch release readiness, cold-chain exception readiness, system-of-systems event confirmation readiness, IT / OT boundary readiness, application release readiness, and mission access review readiness.

The next gap is a transportation and mobile-operations reconciliation example family centered on trip-record presence and agreement between trip and telematics evidence.

## Selected Direction

The implemented pack will be:

- fleet or telematics reconciliation assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent fleet or telematics evidence family
2. trip record presence fixture
3. telematics vehicle match fixture
4. telematics state match fixture
5. one combined telematics reconciliation fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new fleet or telematics evidence fixtures:
  - `tests/json/evidence/fleet_telematics_reconciled.json`
  - `tests/json/evidence/fleet_telematics_missing_trip.json`
  - `tests/json/evidence/fleet_telematics_mismatch.json`
- new fleet or telematics single-subject fixtures:
  - `tests/json/test_of_detail/verify_fleet_trip_record_present.py`
  - `tests/json/test_of_detail/verify_fleet_telematics_vehicle_match.py`
  - `tests/json/test_of_detail/verify_fleet_telematics_state_match.py`
- new fleet or telematics combined fixture:
  - `tests/json/test_of_detail/verify_fleet_telematics_reconciliation.py`
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

- the fleet or telematics reconciliation pack is complete enough to serve as the thirteenth domain-rich exemplar
- the cross-pack progression now extends from access governance back into operational reconciliation evidence
