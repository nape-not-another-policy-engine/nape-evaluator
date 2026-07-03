# Authoring Examples Index

This page is the index into the executable V2 test-of-detail fixture library.

Use it when you want to answer questions like:

- which example should I copy first?
- which examples are simplest?
- which examples match my assurance domain?
- which examples demonstrate fail fast versus fail slow?

If you already know you want one of the implemented domain-rich example families, start with:

- [Domain Packs Overview](domain-packs-overview.md)

All executable fixtures referenced here live under:

- `tests/json/`
- `tests/xml/`
- `tests/yaml/`
- `tests/text/`
- `tests/pdf/`

Each format-family example tree uses the same basic model when practical:

- `evidence/`
- `test_of_detail/`
- `test_pattern_library.py`

## Quick Start Recommendation

If you only want three examples to begin with, use:

1. `verify_author_complete.py`
2. `verify_component_coverage_minimum.py`
3. `verify_dual_coverage_fail_fast.py`

That gives you:

- one simple text equality example
- one simple threshold example
- one simple multi-subject example

## By Evidence Format

### JSON

Use these when you want the broadest current example library.

- `tests/json/test_of_detail/verify_author_complete.py`
- `tests/json/test_of_detail/verify_component_coverage_minimum.py`
- `tests/json/test_of_detail/verify_dual_coverage_fail_fast.py`

### XML

Use this when you want the simplest structured non-dictionary example.

- `tests/xml/test_of_detail/verify_author_complete.py`

Use this next when your XML evidence uses namespaces.

- `tests/xml/test_of_detail/verify_author_complete_namespaced.py`

### YAML

Use this when you want a structured object example that feels close to JSON but still exercises typed YAML loading.

- `tests/yaml/test_of_detail/verify_component_coverage_minimum.py`

Use this next when the YAML value is present but invalid for the subject data type.

- `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`

### Text

Use this when you want the simplest line-oriented parser example.

- `tests/text/test_of_detail/verify_author_complete.py`

Use this next when text evidence contains competing candidate values and the fact cannot be established cleanly.

- `tests/text/test_of_detail/verify_author_complete_ambiguous.py`

### PDF

Use this when you want a text-extraction-backed example and need to see the defensive difference between plain text and PDF-derived text.

- `tests/pdf/test_of_detail/verify_author_complete.py`

Use this next when PDF extraction yields competing candidate values and the result should be `inconclusive`.

- `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`

## By Difficulty

### Starter

These are the best first examples to copy.

| Fixture | Why start here | Main pattern |
| --- | --- | --- |
| `verify_author_complete.py` | simplest text comparison and clean helper breakout | text `equals` |
| `verify_component_coverage_minimum.py` | simplest numeric threshold | number `minimum` |
| `verify_feature_flag_enabled.py` | simplest boolean comparison | boolean `equals` |
| `verify_service_owner_required.py` | simplest presence-only check | `required` |

### Intermediate

These add second criteria, richer type handling, or list/set-style comparisons.

| Fixture | Why it is intermediate | Main pattern |
| --- | --- | --- |
| `verify_component_coverage_range.py` | introduces two compatible numeric criteria in one object | number `minimum` + `maximum` |
| `verify_release_status_allowed_values.py` | moves from single equality to membership | `allowed_values` |
| `verify_release_status_disallowed_values.py` | inverse membership pattern | `disallowed_values` |
| `verify_build_age_days_range.py` | integer-specific range handling | integer `minimum` + `maximum` |
| `verify_last_review_timestamp_minimum.py` | first typed datetime parsing example | datetime `minimum` |
| `verify_review_date_range.py` | typed date parsing plus range | date `minimum` + `maximum` |
| `verify_restore_duration_range.py` | typed duration parsing plus range | duration `minimum` + `maximum` |

### Advanced

These are still bounded first-pass examples, but they are less likely to be the first fixture an author should copy.

| Fixture | Why it is advanced | Main pattern |
| --- | --- | --- |
| `verify_last_review_timestamp_range.py` | datetime parsing plus full window comparison | datetime `minimum` + `maximum` |
| `verify_approver_profile_equals.py` | exact object equality | object `equals` |
| `verify_reviewer_roles_equals.py` | exact array equality | array `equals` |
| `verify_revocation_reason_null.py` | explicit null-state handling | null `equals` |
| `verify_coverage_gap_maximum.py` | derived numeric fact from two raw evidence measures | derived fact `maximum` |
| `verify_dual_coverage_thresholds.py` | multi-subject fail-slow establishment | multi-subject conjunction |
| `verify_dual_coverage_fail_fast.py` | multi-subject fail-fast establishment | multi-subject conjunction |

If you are moving past simple fixture copying and need help understanding how these advanced examples fit together, use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)

## By Domain

### General Starter

These are good when the main goal is to learn the test shape, not to mirror a specific assurance domain.

| Fixture | Domain feel | Main pattern |
| --- | --- | --- |
| `verify_author_complete.py` | generic starter | text `equals` |
| `verify_feature_flag_enabled.py` | generic binary-state check | boolean `equals` |
| `verify_service_owner_required.py` | generic presence check | `required` |
| `tests/text/test_of_detail/verify_author_complete_ambiguous.py` | generic ambiguity handling | text `equals` with ambiguous establishment |
| `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py` | generic extracted-text ambiguity handling | text `equals` with ambiguous establishment |

### Engineering / Software Assurance

These map well to build, test, and component-quality evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_component_coverage_minimum.py` | minimum test coverage | number `minimum` |
| `verify_component_coverage_range.py` | target coverage band | number `minimum` + `maximum` |
| `verify_build_age_days_range.py` | acceptable build age window | integer `minimum` + `maximum` |
| `verify_coverage_gap_maximum.py` | allowable gap between two quality measures | derived fact `maximum` |
| `verify_dual_coverage_thresholds.py` | two required numeric quality gates | multi-subject fail slow |
| `verify_dual_coverage_fail_fast.py` | same domain with simpler establishment flow | multi-subject fail fast |
| `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py` | typed fact present but unusable | numeric threshold with invalid establishment |

### Energy / Utilities / Field Infrastructure

These map well to operational recovery readiness and IT / OT-adjacent evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_restore_drill_status_successful.py` | restore drill completed successfully | text `equals` |
| `verify_restore_drill_duration_within_threshold.py` | restore drill duration stayed under threshold | duration `maximum` |
| `verify_restore_drill_recent.py` | restore drill happened recently enough | datetime `minimum` |
| `verify_restore_drill_core_readiness.py` | restore readiness controls all hold together | multi-subject conjunction |

### Transportation And Logistics

These map well to pre-trip or operational inspection evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_transport_inspection_status_completed.py` | pre-trip inspection status is completed | text `equals` |
| `verify_transport_inspection_recent.py` | inspection happened recently enough | datetime `minimum` |
| `verify_transport_inspection_readiness.py` | transport inspection readiness holds together | multi-subject conjunction |

### Manufacturing And Industrial Operations

These map well to line restart and operational integrity evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_manufacturing_maintenance_release_approved.py` | maintenance release is approved | text `equals` |
| `verify_manufacturing_work_order_complete.py` | work order is complete | boolean `equals` |
| `verify_manufacturing_restart_authorization_approved.py` | restart authorization is approved | text `equals` |
| `verify_manufacturing_line_restart_readiness.py` | manufacturing line restart readiness holds together | multi-subject conjunction |

### Financial Services, Payments, And Insurance

These map well to approval and reconciliation evidence around money movement.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_payment_transaction_approval_status.py` | transaction approval status is approved | text `equals` |
| `verify_payment_reconciliation_status_completed.py` | reconciliation status is completed | text `equals` |
| `verify_payment_settlement_difference_within_tolerance.py` | settlement difference stays within tolerance | number `maximum` |
| `verify_payment_settlement_readiness.py` | payment settlement readiness holds together | multi-subject conjunction |

### Medical Device And Digital Health Product Assurance

These map well to safety-critical release packet and release blocking evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_medical_device_release_review_approved.py` | release review status is approved | text `equals` |
| `verify_medical_device_sbom_present.py` | SBOM is present for the release | boolean `equals` |
| `verify_medical_device_critical_vulnerability_count_maximum.py` | unresolved critical vulnerabilities stay within threshold | integer `maximum` |
| `verify_medical_device_release_packet_readiness.py` | medical device release packet readiness holds together | multi-subject conjunction |

### Healthcare Delivery And Health Information Assurance

These map well to patient-data export governance and retention-handling evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_patient_data_export_ticket_present.py` | patient-data export ticket is present | boolean `equals` |
| `verify_patient_data_export_approval_present.py` | patient-data export has linked approval evidence | boolean `equals` |
| `verify_patient_data_retention_execution_completed.py` | patient-data retention execution is completed | text `equals` |
| `verify_patient_data_export_governance.py` | patient-data export governance holds together | multi-subject conjunction |

### Pharmaceutical, Laboratory, And Regulated Quality Assurance

These map well to reviewer presence, batch state, and deviation-closure evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_quality_batch_release_status_released.py` | batch release status is released | text `equals` |
| `verify_quality_reviewer_present.py` | quality reviewer is present | boolean `equals` |
| `verify_quality_deviation_closed.py` | deviation is closed | boolean `equals` |
| `verify_quality_batch_release_readiness.py` | regulated quality batch release readiness holds together | multi-subject conjunction |

### Food, Agriculture, And Cold-Chain Assurance

These map well to excursion thresholds, custody completeness, and exception closure evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_cold_chain_temperature_excursion_count_maximum.py` | temperature excursion count stays within threshold | integer `maximum` |
| `verify_cold_chain_chain_of_custody_complete.py` | chain of custody is complete | boolean `equals` |
| `verify_cold_chain_exception_closed.py` | exception is closed | boolean `equals` |
| `verify_cold_chain_exception_readiness.py` | cold-chain exception readiness holds together | multi-subject conjunction |

### Public Sector, Defense, And System-Of-Systems Assurance

These map well to multi-source event confirmation and cross-system state evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_system_interconnection_approval_present.py` | interconnection approval is present | boolean `equals` |
| `verify_system_event_confirmation_status_confirmed.py` | required event is confirmed across systems | text `equals` |
| `verify_system_cross_state_match.py` | reported state matches across systems | boolean `equals` |
| `verify_system_of_systems_event_confirmation.py` | system-of-systems event confirmation holds together | multi-subject conjunction |

### IT / OT Boundary Assurance

These map well to remote-access control, exposure thresholds, and boundary-state evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_it_ot_remote_access_disabled.py` | remote access is disabled as expected | boolean `equals` |
| `verify_it_ot_internet_exposed_controller_count_maximum.py` | no disallowed controller internet exposure exists | integer `maximum` |
| `verify_it_ot_boundary_control_segmented.py` | boundary control status is segmented | text `equals` |
| `verify_it_ot_boundary_readiness.py` | IT / OT boundary readiness holds together | multi-subject conjunction |

### Application Verification Assurance

These map well to admin-path control state, vulnerability threshold, and deployment-approval evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_application_mfa_required.py` | MFA is required for the admin path | boolean `equals` |
| `verify_application_critical_vulnerability_count_maximum.py` | unresolved critical vulnerabilities stay within threshold | integer `maximum` |
| `verify_application_deployment_approval_present.py` | deployment approval is present | boolean `equals` |
| `verify_application_release_readiness.py` | application release readiness holds together | multi-subject conjunction |

### Mission Access And Authorization Assurance

These map well to access status, approval presence, and review-recency evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_mission_access_status_authorized.py` | mission access status is authorized | text `equals` |
| `verify_mission_access_approval_present.py` | mission access approval is present | boolean `equals` |
| `verify_mission_access_review_recent.py` | mission access review is recent enough | datetime `minimum` |
| `verify_mission_access_readiness.py` | mission access readiness holds together | multi-subject conjunction |

### Fleet And Telematics Reconciliation Assurance

These map well to trip-record presence and agreement between trip and telematics evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_fleet_trip_record_present.py` | trip record is present | boolean `equals` |
| `verify_fleet_telematics_vehicle_match.py` | telematics and trip records agree on vehicle identity | boolean `equals` |
| `verify_fleet_telematics_state_match.py` | telematics and trip records agree on state | boolean `equals` |
| `verify_fleet_telematics_reconciliation.py` | fleet telematics reconciliation holds together | multi-subject conjunction |

### Aviation And Return-To-Service Assurance

These map well to maintenance release, hazard closure, and calibration-readiness evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_return_to_service_maintenance_release_approved.py` | maintenance release is approved before return to service | text `equals` |
| `verify_return_to_service_hazard_closure_closed.py` | blocking hazard is closed before return to service | text `equals` |
| `verify_return_to_service_calibration_current.py` | safety-relevant calibration is current | boolean `equals` |
| `verify_return_to_service_readiness.py` | return-to-service readiness holds together | multi-subject conjunction |

### Authorization Assurance

These map well to access approval, review, and revocation evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_privileged_access_status_approved.py` | privileged access request status is approved | text `equals` |
| `verify_privileged_access_approver_required.py` | privileged access has a recorded approver | `required` |
| `verify_privileged_access_review_recent.py` | privileged access review is recent enough | datetime `minimum` |
| `verify_privileged_access_core_controls.py` | privileged access core controls all hold together | multi-subject conjunction |
| `verify_last_review_timestamp_minimum.py` | review is recent enough | datetime `minimum` |
| `verify_last_review_timestamp_range.py` | review falls within an allowed window | datetime `minimum` + `maximum` |
| `verify_approver_profile_equals.py` | approver metadata exactly matches expectation | object `equals` |
| `verify_reviewer_roles_equals.py` | reviewer roles exactly match expectation | array `equals` |
| `verify_revocation_reason_null.py` | field is explicitly null, not just absent | null `equals` |
| `tests/xml/test_of_detail/verify_author_complete_namespaced.py` | structured approval/status data with namespace handling | text `equals` with namespace-aware extraction |

### Operational / Timing Assurance

These map well to time-window and elapsed-time evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_review_date_range.py` | review or attestation date window | date `minimum` + `maximum` |
| `verify_restore_duration_range.py` | restore or completion duration window | duration `minimum` + `maximum` |

### Status / State Assurance

These are useful when the evidence carries one or more status-like values.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_release_status_allowed_values.py` | acceptable status list | `allowed_values` |
| `verify_release_status_disallowed_values.py` | prohibited status list | `disallowed_values` |
| `verify_author_complete.py` | exact expected status | text `equals` |

## By Establishment Style

### Fail Fast

- `verify_author_complete.py`
- `verify_component_coverage_minimum.py`
- `verify_component_coverage_range.py`
- `verify_feature_flag_enabled.py`
- `verify_release_status_allowed_values.py`
- `verify_release_status_disallowed_values.py`
- `verify_service_owner_required.py`
- `verify_build_age_days_range.py`
- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_last_review_timestamp_minimum.py`
- `verify_last_review_timestamp_range.py`
- `verify_approver_profile_equals.py`
- `verify_reviewer_roles_equals.py`
- `verify_revocation_reason_null.py`
- `verify_dual_coverage_fail_fast.py`
- `verify_patient_data_export_ticket_present.py`
- `verify_patient_data_export_approval_present.py`
- `verify_patient_data_retention_execution_completed.py`

### Fail Slow

- `verify_coverage_gap_maximum.py`
- `verify_dual_coverage_thresholds.py`
- `verify_patient_data_export_governance.py`

## By Negative Path Type

### Ambiguous Extracted Fact

These examples show evidence that yields more than one competing candidate value, so the test returns `inconclusive` instead of claiming the fact is false.

- `tests/text/test_of_detail/verify_author_complete_ambiguous.py`
- `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`

Related evidence fixtures:

- `tests/text/evidence/author_verification_ambiguous_status.txt`

### Invalid Extracted Fact

These examples show evidence present but unusable, usually leading to `inconclusive`.

- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`

Related evidence fixtures:

- `operations_timing_invalid_review_date.json`
- `operations_timing_invalid_restore_duration.json`
- `tests/yaml/evidence/component_assurance_invalid_coverage.yaml`

### Namespace-Aware Extraction

This example shows evidence that is structurally valid XML but requires one explicit namespace-handling seam in the extraction helper.

- `tests/xml/test_of_detail/verify_author_complete_namespaced.py`

Related evidence fixtures:

- `tests/xml/evidence/author_verification_namespaced.xml`

### Invalid Caller Criteria For The Test

These examples show malformed criteria values that the test recognizes and rejects, usually leading to `inconclusive` with explicit test-owned reasoning.

- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_last_review_timestamp_minimum.py`
- `verify_last_review_timestamp_range.py`

### Derived Fact With Missing Prerequisite

This example shows a derived fact that cannot be established because one required raw evidence fact is missing.

- `verify_coverage_gap_maximum.py`

Related evidence fixture:

- `component_assurance_missing_branch.json`

## Recommended Copy Paths

### If You Want The Simplest Possible Starter

Copy:

- `verify_author_complete.py`

Then evolve to:

- `verify_component_coverage_minimum.py`

### If You Want A Threshold-Based Starter

Copy:

- `verify_component_coverage_minimum.py`

Then evolve to:

- `verify_component_coverage_range.py`
- `verify_build_age_days_range.py`

### If You Want A Typed Temporal Starter

Copy:

- `verify_last_review_timestamp_minimum.py`

Then evolve to:

- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_last_review_timestamp_range.py`

### If You Want A Multi-Subject Starter

Copy:

- `verify_dual_coverage_fail_fast.py`

Then evolve to:

- `verify_dual_coverage_thresholds.py`

That sequence lets authors start with simpler control flow before moving into fail-slow diagnostics.

### If You Want A Derived-Fact Starter

Copy:

- `verify_coverage_gap_maximum.py`

Use it after you already understand:

- one-subject threshold tests
- how facts are established before evaluation

That sequence helps you learn how to compute one explicit derived fact from two raw evidence facts without turning the transport into a policy language.

### If You Want A Domain-Rich Utility / Field Restore Starter Pack

Copy in this order:

- `verify_restore_drill_status_successful.py`
- `verify_restore_drill_duration_within_threshold.py`
- `verify_restore_drill_recent.py`
- `verify_restore_drill_core_readiness.py`

Use these evidence fixtures with that pack:

- `utility_restore_drill_success.json`
- `utility_restore_drill_stale.json`
- `utility_restore_drill_over_duration.json`

That path lets an author learn the domain in layers:

- success state
- duration threshold
- recency
- combined restore readiness

### If You Want A Domain-Rich Transportation Inspection Starter Pack

Copy in this order:

- `verify_transport_inspection_status_completed.py`
- `verify_transport_inspection_recent.py`
- `verify_transport_inspection_readiness.py`

Use these evidence fixtures with that pack:

- `transport_inspection_current.json`
- `transport_inspection_stale.json`
- `transport_inspection_incomplete.json`

That path lets an author learn the domain in layers:

- inspection completion state
- inspection freshness
- combined transport readiness

### If You Want A Domain-Rich Manufacturing Restart Starter Pack

Copy in this order:

- `verify_manufacturing_maintenance_release_approved.py`
- `verify_manufacturing_work_order_complete.py`
- `verify_manufacturing_restart_authorization_approved.py`
- `verify_manufacturing_line_restart_readiness.py`

Use these evidence fixtures with that pack:

- `manufacturing_line_restart_ready.json`
- `manufacturing_line_restart_incomplete_work_order.json`
- `manufacturing_line_restart_blocked.json`

That path lets an author learn the domain in layers:

- maintenance release state
- work-order completion
- restart authorization state
- combined line restart readiness

### If You Want A Domain-Rich Payment Settlement Starter Pack

Copy in this order:

- `verify_payment_transaction_approval_status.py`
- `verify_payment_reconciliation_status_completed.py`
- `verify_payment_settlement_difference_within_tolerance.py`
- `verify_payment_settlement_readiness.py`

Use these evidence fixtures with that pack:

- `payment_settlement_balanced.json`
- `payment_settlement_over_tolerance.json`
- `payment_settlement_blocked.json`

That path lets an author learn the domain in layers:

- approval state
- reconciliation completion state
- settlement tolerance
- combined payment settlement readiness

### If You Want A Domain-Rich Medical Device Release Starter Pack

Copy in this order:

- `verify_medical_device_release_review_approved.py`
- `verify_medical_device_sbom_present.py`
- `verify_medical_device_critical_vulnerability_count_maximum.py`
- `verify_medical_device_release_packet_readiness.py`

Use these evidence fixtures with that pack:

- `medical_device_release_ready.json`
- `medical_device_release_missing_sbom.json`
- `medical_device_release_blocked.json`

That path lets an author learn the domain in layers:

- release review status
- SBOM presence
- critical vulnerability threshold
- combined release packet readiness

### If You Want A Domain-Rich Regulated Quality Release Starter Pack

Copy in this order:

- `verify_quality_batch_release_status_released.py`
- `verify_quality_reviewer_present.py`
- `verify_quality_deviation_closed.py`
- `verify_quality_batch_release_readiness.py`

Use these evidence fixtures with that pack:

- `quality_batch_release_ready.json`
- `quality_batch_release_missing_reviewer.json`
- `quality_batch_release_open_deviation.json`

That path lets an author learn the domain in layers:

- batch release state
- reviewer presence
- deviation closure
- combined regulated quality release readiness

### If You Want A Domain-Rich Cold-Chain Exception Starter Pack

Copy in this order:

- `verify_cold_chain_temperature_excursion_count_maximum.py`
- `verify_cold_chain_chain_of_custody_complete.py`
- `verify_cold_chain_exception_closed.py`
- `verify_cold_chain_exception_readiness.py`

Use these evidence fixtures with that pack:

- `cold_chain_exception_ready.json`
- `cold_chain_exception_incomplete_custody.json`
- `cold_chain_exception_open.json`

That path lets an author learn the domain in layers:

- excursion threshold
- custody completeness
- exception closure
- combined cold-chain exception readiness

### If You Want A Domain-Rich System-Of-Systems Starter Pack

Copy in this order:

- `verify_system_interconnection_approval_present.py`
- `verify_system_event_confirmation_status_confirmed.py`
- `verify_system_cross_state_match.py`
- `verify_system_of_systems_event_confirmation.py`

Use these evidence fixtures with that pack:

- `system_event_confirmation_ready.json`
- `system_event_confirmation_missing_approval.json`
- `system_event_confirmation_mismatch.json`

That path lets an author learn the domain in layers:

- approval presence
- event confirmation across systems
- state reconciliation
- combined system-of-systems confirmation

### If You Want A Domain-Rich IT / OT Boundary Starter Pack

Copy in this order:

- `verify_it_ot_remote_access_disabled.py`
- `verify_it_ot_internet_exposed_controller_count_maximum.py`
- `verify_it_ot_boundary_control_segmented.py`
- `verify_it_ot_boundary_readiness.py`

Use these evidence fixtures with that pack:

- `it_ot_boundary_safe.json`
- `it_ot_boundary_remote_access_enabled.json`
- `it_ot_boundary_exposed.json`

That path lets an author learn the domain in layers:

- remote access state
- exposure threshold
- boundary control state
- combined IT / OT boundary readiness

### If You Want A Domain-Rich Application Verification Starter Pack

Copy in this order:

- `verify_application_mfa_required.py`
- `verify_application_critical_vulnerability_count_maximum.py`
- `verify_application_deployment_approval_present.py`
- `verify_application_release_readiness.py`

Use these evidence fixtures with that pack:

- `application_release_ready.json`
- `application_release_mfa_disabled.json`
- `application_release_blocked.json`

That path lets an author learn the domain in layers:

- admin-path MFA state
- vulnerability threshold
- deployment approval presence
- combined application release readiness

### If You Want A Domain-Rich Mission Access Starter Pack

Copy in this order:

- `verify_mission_access_status_authorized.py`
- `verify_mission_access_approval_present.py`
- `verify_mission_access_review_recent.py`
- `verify_mission_access_readiness.py`

Use these evidence fixtures with that pack:

- `mission_access_review_ready.json`
- `mission_access_review_missing_approval.json`
- `mission_access_review_stale.json`

That path lets an author learn the domain in layers:

- access status
- approval presence
- review recency
- combined mission access readiness

### If You Want A Domain-Rich Fleet Telematics Starter Pack

Copy in this order:

- `verify_fleet_trip_record_present.py`
- `verify_fleet_telematics_vehicle_match.py`
- `verify_fleet_telematics_state_match.py`
- `verify_fleet_telematics_reconciliation.py`

Use these evidence fixtures with that pack:

- `fleet_telematics_reconciled.json`
- `fleet_telematics_missing_trip.json`
- `fleet_telematics_mismatch.json`

That path lets an author learn the domain in layers:

- trip record presence
- vehicle identity reconciliation
- state reconciliation
- combined fleet telematics reconciliation

### If You Want A Domain-Rich Return-To-Service Starter Pack

Copy in this order:

- `verify_return_to_service_maintenance_release_approved.py`
- `verify_return_to_service_hazard_closure_closed.py`
- `verify_return_to_service_calibration_current.py`
- `verify_return_to_service_readiness.py`

Use these evidence fixtures with that pack:

- `return_to_service_ready.json`
- `return_to_service_open_hazard.json`
- `return_to_service_blocked.json`

That path lets an author learn the domain in layers:

- maintenance release state
- hazard closure state
- calibration readiness
- combined return-to-service readiness

### If You Want A Domain-Rich Patient-Data Export Governance Starter Pack

Copy in this order:

- `verify_patient_data_export_ticket_present.py`
- `verify_patient_data_export_approval_present.py`
- `verify_patient_data_retention_execution_completed.py`
- `verify_patient_data_export_governance.py`

Use these evidence fixtures with that pack:

- `patient_data_export_ready.json`
- `patient_data_export_missing_approval.json`
- `patient_data_export_retention_pending.json`

That path lets an author learn the domain in layers:

- export ticket presence
- export approval evidence
- retention execution status
- combined patient-data export governance

### If You Want A Domain-Rich Authorization Starter Pack

Copy in this order:

- `verify_privileged_access_status_approved.py`
- `verify_privileged_access_approver_required.py`
- `verify_privileged_access_review_recent.py`
- `verify_privileged_access_core_controls.py`

Use these evidence fixtures with that pack:

- `privileged_access_grant.json`
- `privileged_access_grant_missing_approver.json`
- `privileged_access_grant_stale_review.json`

That path lets an author learn the domain in layers:

- status
- presence
- temporal freshness
- combined control reasoning

If the next question is no longer "which fixture should I copy?" but instead "how should I scale this authoring model safely?", use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)
