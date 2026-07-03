# Domain Packs Overview

This page explains the current domain-pack model for the evaluator example library.

Use it when your question is not "what does one fixture do?" but instead:

- what is a domain pack?
- which domain packs are implemented already?
- how are the packs structured internally?
- how should I choose which pack to study first?

## What A Domain Pack Is

A domain pack is a small family of executable examples built around one assurance story.

Each pack should be internally consistent across:

- evidence theme
- subject naming
- simple single-subject fixtures
- one combined readiness or core-controls fixture
- positive and negative evidence variants

The point is to let a reader learn a domain in layers rather than by jumping straight into one large test.

## Current Implemented Packs

The current implemented packs are:

1. privileged access approval and review
2. utility / field restore readiness
3. transportation inspection readiness
4. manufacturing line restart readiness
5. payment settlement readiness
6. medical device release packet readiness
7. regulated quality batch release readiness
8. cold-chain exception readiness
9. system-of-systems event confirmation readiness
10. IT / OT boundary readiness
11. application release readiness
12. mission access review readiness
13. fleet telematics reconciliation readiness
14. aviation or maintenance return-to-service readiness
15. healthcare patient-data export governance readiness

## Standard Pack Structure

The current packs now follow one shared pattern:

1. one coherent evidence family under `tests/json/evidence/`
2. simple single-subject fixtures under `tests/json/test_of_detail/`
3. one combined multi-subject fixture under `tests/json/test_of_detail/`
4. pattern-library tests proving caller-owned evaluations are used

That shared structure is intentional.

It means readers can transfer what they learn from one domain pack into the next.

## Pack Summaries

## 1. Privileged Access Approval And Review

### Assurance Story

A privileged access grant should only be considered acceptable when:

- the request is approved
- an approver is recorded
- the review is recent enough

### Simple Fixtures

- `verify_privileged_access_status_approved.py`
- `verify_privileged_access_approver_required.py`
- `verify_privileged_access_review_recent.py`

### Combined Fixture

- `verify_privileged_access_core_controls.py`

### Evidence Variants

- `privileged_access_grant.json`
- `privileged_access_grant_missing_approver.json`
- `privileged_access_grant_stale_review.json`

### Best First Use

Start here if you want the clearest authorization-oriented example pack.

## 2. Utility / Field Restore Readiness

### Assurance Story

A restore drill should only be considered acceptable when:

- the drill completed successfully
- the duration stayed within threshold
- the drill is recent enough

### Simple Fixtures

- `verify_restore_drill_status_successful.py`
- `verify_restore_drill_duration_within_threshold.py`
- `verify_restore_drill_recent.py`

### Combined Fixture

- `verify_restore_drill_core_readiness.py`

### Evidence Variants

- `utility_restore_drill_success.json`
- `utility_restore_drill_stale.json`
- `utility_restore_drill_over_duration.json`

### Best First Use

Start here if you want an operational IT / OT-adjacent example pack.

## 3. Transportation Inspection Readiness

### Assurance Story

A transport asset should only be considered inspection-ready when:

- the inspection status is completed
- the inspection is recent enough

### Simple Fixtures

- `verify_transport_inspection_status_completed.py`
- `verify_transport_inspection_recent.py`

### Combined Fixture

- `verify_transport_inspection_readiness.py`

### Evidence Variants

- `transport_inspection_current.json`
- `transport_inspection_stale.json`
- `transport_inspection_incomplete.json`

### Best First Use

Start here if you want a transportation or fleet operations starter pack.

## 4. Manufacturing Line Restart Readiness

### Assurance Story

A manufacturing line should only be considered ready to restart when:

- maintenance release is approved
- the work order is complete
- restart authorization is approved

### Simple Fixtures

- `verify_manufacturing_maintenance_release_approved.py`
- `verify_manufacturing_work_order_complete.py`
- `verify_manufacturing_restart_authorization_approved.py`

### Combined Fixture

- `verify_manufacturing_line_restart_readiness.py`

### Evidence Variants

- `manufacturing_line_restart_ready.json`
- `manufacturing_line_restart_incomplete_work_order.json`
- `manufacturing_line_restart_blocked.json`

### Best First Use

Start here if you want a plant-floor operational integrity example pack.

## 5. Payment Settlement Readiness

### Assurance Story

A payment settlement record should only be considered ready when:

- the transaction approval status is approved
- the reconciliation status is completed
- the settlement difference amount stays within tolerance

### Simple Fixtures

- `verify_payment_transaction_approval_status.py`
- `verify_payment_reconciliation_status_completed.py`
- `verify_payment_settlement_difference_within_tolerance.py`

### Combined Fixture

- `verify_payment_settlement_readiness.py`

### Evidence Variants

- `payment_settlement_balanced.json`
- `payment_settlement_over_tolerance.json`
- `payment_settlement_blocked.json`

### Best First Use

Start here if you want a business-process and reconciliation-oriented example pack.

## 6. Medical Device Release Packet Readiness

### Assurance Story

A medical device release packet should only be considered ready when:

- the release review status is approved
- an SBOM is present
- unresolved critical vulnerabilities stay within threshold

### Simple Fixtures

- `verify_medical_device_release_review_approved.py`
- `verify_medical_device_sbom_present.py`
- `verify_medical_device_critical_vulnerability_count_maximum.py`

### Combined Fixture

- `verify_medical_device_release_packet_readiness.py`

### Evidence Variants

- `medical_device_release_ready.json`
- `medical_device_release_missing_sbom.json`
- `medical_device_release_blocked.json`

### Best First Use

Start here if you want a safety-critical product release example pack.

## 7. Regulated Quality Batch Release Readiness

### Assurance Story

A regulated quality batch release should only be considered ready when:

- the batch release status is released
- a quality reviewer is present
- the deviation is closed

### Simple Fixtures

- `verify_quality_batch_release_status_released.py`
- `verify_quality_reviewer_present.py`
- `verify_quality_deviation_closed.py`

### Combined Fixture

- `verify_quality_batch_release_readiness.py`

### Evidence Variants

- `quality_batch_release_ready.json`
- `quality_batch_release_missing_reviewer.json`
- `quality_batch_release_open_deviation.json`

### Best First Use

Start here if you want a regulated quality and information-integrity example pack.

## 8. Cold-Chain Exception Readiness

### Assurance Story

A cold-chain shipment exception record should only be considered ready when:

- the temperature excursion count stays within threshold
- chain of custody is complete
- the exception is closed

### Simple Fixtures

- `verify_cold_chain_temperature_excursion_count_maximum.py`
- `verify_cold_chain_chain_of_custody_complete.py`
- `verify_cold_chain_exception_closed.py`

### Combined Fixture

- `verify_cold_chain_exception_readiness.py`

### Evidence Variants

- `cold_chain_exception_ready.json`
- `cold_chain_exception_incomplete_custody.json`
- `cold_chain_exception_open.json`

### Best First Use

Start here if you want a physical-world custody and exception example pack.

## 9. System-Of-Systems Event Confirmation Readiness

### Assurance Story

A system-of-systems event confirmation packet should only be considered ready when:

- interconnection approval is present
- the event is confirmed across systems
- the reported states match across systems

### Simple Fixtures

- `verify_system_interconnection_approval_present.py`
- `verify_system_event_confirmation_status_confirmed.py`
- `verify_system_cross_state_match.py`

### Combined Fixture

- `verify_system_of_systems_event_confirmation.py`

### Evidence Variants

- `system_event_confirmation_ready.json`
- `system_event_confirmation_missing_approval.json`
- `system_event_confirmation_mismatch.json`

### Best First Use

Start here if you want an explicit multi-source confirmation example pack.

## 10. IT / OT Boundary Readiness

### Assurance Story

An IT / OT boundary packet should only be considered ready when:

- remote access is in the expected state
- no disallowed controller internet exposure exists
- the boundary control status is segmented

### Simple Fixtures

- `verify_it_ot_remote_access_disabled.py`
- `verify_it_ot_internet_exposed_controller_count_maximum.py`
- `verify_it_ot_boundary_control_segmented.py`

### Combined Fixture

- `verify_it_ot_boundary_readiness.py`

### Evidence Variants

- `it_ot_boundary_safe.json`
- `it_ot_boundary_remote_access_enabled.json`
- `it_ot_boundary_exposed.json`

### Best First Use

Start here if you want an explicit boundary-control and exposure-verification example pack.

## 11. Application Release Readiness

### Assurance Story

An application release packet should only be considered ready when:

- MFA is required for the admin path
- unresolved critical vulnerabilities stay within threshold
- deployment approval is present

### Simple Fixtures

- `verify_application_mfa_required.py`
- `verify_application_critical_vulnerability_count_maximum.py`
- `verify_application_deployment_approval_present.py`

### Combined Fixture

- `verify_application_release_readiness.py`

### Evidence Variants

- `application_release_ready.json`
- `application_release_mfa_disabled.json`
- `application_release_blocked.json`

### Best First Use

Start here if you want a software-focused release-control example pack.

## 12. Mission Access Review Readiness

### Assurance Story

A mission access review packet should only be considered ready when:

- the mission access status is authorized
- approval is present
- the review is recent enough

### Simple Fixtures

- `verify_mission_access_status_authorized.py`
- `verify_mission_access_approval_present.py`
- `verify_mission_access_review_recent.py`

### Combined Fixture

- `verify_mission_access_readiness.py`

### Evidence Variants

- `mission_access_review_ready.json`
- `mission_access_review_missing_approval.json`
- `mission_access_review_stale.json`

### Best First Use

Start here if you want a governance and authorization recency example pack.

## 13. Fleet Telematics Reconciliation Readiness

### Assurance Story

A fleet telematics reconciliation packet should only be considered ready when:

- a trip record is present
- telematics and trip records agree on vehicle identity
- telematics and trip records agree on reported state

### Simple Fixtures

- `verify_fleet_trip_record_present.py`
- `verify_fleet_telematics_vehicle_match.py`
- `verify_fleet_telematics_state_match.py`

### Combined Fixture

- `verify_fleet_telematics_reconciliation.py`

### Evidence Variants

- `fleet_telematics_reconciled.json`
- `fleet_telematics_missing_trip.json`
- `fleet_telematics_mismatch.json`

### Best First Use

Start here if you want an operational reconciliation example pack.

## 14. Return-To-Service Readiness

### Assurance Story

A return-to-service packet should only be considered ready when:

- maintenance release is approved
- hazards are closed
- calibration is current

### Simple Fixtures

- `verify_return_to_service_maintenance_release_approved.py`
- `verify_return_to_service_hazard_closure_closed.py`
- `verify_return_to_service_calibration_current.py`

### Combined Fixture

- `verify_return_to_service_readiness.py`

### Evidence Variants

- `return_to_service_ready.json`
- `return_to_service_open_hazard.json`
- `return_to_service_blocked.json`

### Best First Use

Start here if you want a safety-readiness example pack centered on return to service.

## 15. Healthcare Patient-Data Export Governance Readiness

### Assurance Story

A patient-data export packet should only be considered governed when:

- an export ticket is present
- export approval is present
- retention execution is completed

### Simple Fixtures

- `verify_patient_data_export_ticket_present.py`
- `verify_patient_data_export_approval_present.py`
- `verify_patient_data_retention_execution_completed.py`

### Combined Fixture

- `verify_patient_data_export_governance.py`

### Evidence Variants

- `patient_data_export_ready.json`
- `patient_data_export_missing_approval.json`
- `patient_data_export_retention_pending.json`

### Best First Use

Start here if you want a healthcare data-governance example pack rather than another access-review variant.

## How To Choose A Pack

Use this default order:

1. privileged access approval and review
2. utility / field restore readiness
3. transportation inspection readiness
4. manufacturing line restart readiness
5. payment settlement readiness
6. medical device release packet readiness
7. regulated quality batch release readiness
8. cold-chain exception readiness
9. system-of-systems event confirmation readiness
10. IT / OT boundary readiness
11. application release readiness
12. mission access review readiness
13. fleet telematics reconciliation readiness
14. aviation or maintenance return-to-service readiness
15. healthcare patient-data export governance readiness

That order is recommended because it moves from:

- enterprise authorization
- to utility / field operations
- to transportation operations
- to manufacturing operations
- to business-process and financial assurance
- to safety-critical product release assurance
- to regulated quality release assurance
- to physical-world custody and exception assurance
- to explicit multi-source system confirmation
- to explicit boundary verification
- to software release verification
- to mission access governance verification
- to fleet and telemetry reconciliation
- to safety return-to-service readiness
- to healthcare data-governance execution verification

while keeping the evaluator model stable.

## Cross-Pack Consistency

The current fifteen-pack set is intentionally consistent on these points:

- every pack has one coherent evidence family
- every pack has simple fixtures before the combined fixture
- every pack lets caller-owned evaluations change the outcome
- every pack uses domain language without turning the transport into a policy language

## Latest Expansion Seam

The latest pack extends the example library into healthcare patient-data handling governance evidence.

Current latest seam:

- healthcare patient-data export governance assurance

Why it was worth adding:

- it adds a healthcare-delivery governance example that is not just another access review
- it introduces approval, ticket-presence, and execution-completion confirmation patterns
- it keeps the example library expanding across materially different evidence stories and operating environments
