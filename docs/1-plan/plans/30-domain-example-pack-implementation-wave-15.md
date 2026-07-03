# Plan 30: Domain Example Pack Implementation Wave 15

## Purpose

Implement the fifteenth domain-rich example pack as executable evaluator examples and routing docs.

Wave 15 starts with healthcare patient-data export governance assurance.

## Why This Exists

The first fourteen domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, payment settlement readiness, medical device release packet readiness, regulated quality batch release readiness, cold-chain exception readiness, system-of-systems event confirmation readiness, IT / OT boundary readiness, application release readiness, mission access review readiness, fleet telematics reconciliation readiness, and aviation or maintenance return-to-service readiness.

The next gap is a healthcare-delivery assurance family centered on patient-data export approval, export ticket presence, and retention execution completion.

## Selected Direction

The implemented pack will be:

- healthcare patient-data export governance assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent patient-data export evidence family
2. export ticket presence fixture
3. export approval presence fixture
4. retention execution completion fixture
5. one combined patient-data export governance fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new patient-data export evidence fixtures:
  - `tests/json/evidence/patient_data_export_ready.json`
  - `tests/json/evidence/patient_data_export_missing_approval.json`
  - `tests/json/evidence/patient_data_export_retention_pending.json`
- new patient-data export single-subject fixtures:
  - `tests/json/test_of_detail/verify_patient_data_export_ticket_present.py`
  - `tests/json/test_of_detail/verify_patient_data_export_approval_present.py`
  - `tests/json/test_of_detail/verify_patient_data_retention_execution_completed.py`
- new patient-data export combined fixture:
  - `tests/json/test_of_detail/verify_patient_data_export_governance.py`
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

- the healthcare patient-data export governance pack is complete enough to serve as the fifteenth domain-rich exemplar
- the cross-pack progression now includes a healthcare-delivery governance family that verifies approval, ticket presence, and retention execution without turning the transport into a policy language
