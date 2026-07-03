# Domain Examples

This page maps high-risk assurance domains to plausible test-of-detail example packs for the evaluator.

The purpose is not to lock the repo into one framework or one industry.

The purpose is to give future examples a realistic basis in how organizations actually verify risky details from evidence.

## How To Read This Page

This page mixes two layers:

- source-grounded sector themes:
  - common concerns reflected in current public standards, guidance, or sector references
- recommended example-pack inferences:
  - my recommendation for which evaluator examples would best represent those concerns

Those are related, but not identical.

The standards and sector guidance do not define the exact evaluator examples.

They help us choose examples that are plausible and recognizable.

## Cross-Cutting Assurance Problem Families

Across industries, the same underlying test-of-detail shapes appear repeatedly.

The most reusable families are:

- state verification:
  - verify that something is in the required status
- threshold verification:
  - verify that a measured value meets a minimum or maximum
- freshness verification:
  - verify that a review, scan, backup, approval, or calibration happened recently enough
- presence verification:
  - verify that a required field, owner, approver, artifact, or control record exists
- reconciliation verification:
  - verify that two records or systems agree on a value
- segregation verification:
  - verify that the approver or reviewer is not the requester or preparer
- ambiguity handling:
  - verify that the evidence supports one clear fact before claiming `true` or `false`
- system boundary verification:
  - verify that a control was applied at the right interface, especially at an IT / OT, application / infrastructure, or vendor / internal boundary

These families are what let one example pack transfer across multiple verticals.

## Industry And Vertical Map

## Energy, Utilities, And Field Infrastructure

### Example Company Types

- electric utilities
- water and wastewater operators
- pipeline operators
- distributed field infrastructure operators

### High-Risk Assurance Problems

- internet-facing operational technology
- unsafe remote access paths into field or plant systems
- missing separation between IT and OT zones
- unreviewed changes to controllers or safety-relevant infrastructure configurations
- recovery drills that are not recent or not successful
- stale inspection or calibration evidence for field assets

### Plausible Evidence

- network exposure inventories
- firewall or remote access configuration exports
- controller change logs
- backup and restore drill records
- field asset inspection or calibration records
- segmentation diagrams represented as structured data

### Plausible Subjects

- `remote_access_enabled`
- `internet_exposed_controller_count`
- `last_restore_drill_timestamp`
- `restore_drill_status`
- `restore_drill_duration_minutes`
- `asset_calibration_current`
- `last_field_inspection_timestamp`

### Candidate Example Ideas

- verify that no controller is directly internet exposed
- verify that the latest restore drill completed successfully
- verify that the latest restore drill duration stayed within the allowed window
- verify that remote vendor access is disabled or separately approved
- verify that a field inspection or calibration is current for a safety-relevant asset

### Additional Current Repo Pack

This domain now also has an executable IT / OT boundary starter pack under:

- `tests/json/evidence/it_ot_boundary_safe.json`
- `tests/json/evidence/it_ot_boundary_remote_access_enabled.json`
- `tests/json/evidence/it_ot_boundary_exposed.json`
- `tests/json/test_of_detail/verify_it_ot_remote_access_disabled.py`
- `tests/json/test_of_detail/verify_it_ot_internet_exposed_controller_count_maximum.py`
- `tests/json/test_of_detail/verify_it_ot_boundary_control_segmented.py`
- `tests/json/test_of_detail/verify_it_ot_boundary_readiness.py`

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/utility_restore_drill_success.json`
- `tests/json/evidence/utility_restore_drill_stale.json`
- `tests/json/evidence/utility_restore_drill_over_duration.json`
- `tests/json/test_of_detail/verify_restore_drill_status_successful.py`
- `tests/json/test_of_detail/verify_restore_drill_duration_within_threshold.py`
- `tests/json/test_of_detail/verify_restore_drill_recent.py`
- `tests/json/test_of_detail/verify_restore_drill_core_readiness.py`

### Why This Is A Strong Example Domain

- it directly covers the IT / OT divide
- consequences are operational and physical, not only administrative
- it maps well to utility, pipeline, and distributed infrastructure operations

## Transportation And Logistics

### Example Company Types

- trucking fleets
- rail operators
- aviation operators
- maritime operators
- field-service fleets
- public transit operators
- delivery and logistics companies
- warehouse and freight coordinators

### High-Risk Assurance Problems

- inaccurate or incomplete records of duty status
- missing driver / vehicle binding
- stale inspections
- incomplete maintenance release evidence
- route or location records that do not support the asserted event
- telematics data that does not reconcile to claimed operational status
- incomplete chain-of-custody or handoff evidence

### Plausible Evidence

- electronic logging device exports
- trip records
- vehicle inspection reports
- maintenance completion records
- telematics event logs
- shipment handoff records
- maintenance release records

### Plausible Subjects

- `eld_record_present`
- `driving_hours_today`
- `driver_identifier`
- `vehicle_identifier`
- `pre_trip_inspection_status`
- `inspection_timestamp`
- `maintenance_release_status`
- `chain_of_custody_complete`

### Candidate Example Ideas

- verify that an ELD-backed trip record exists for the claimed trip
- verify that the pre-trip inspection is present and completed
- verify that the inspection timestamp is within the allowed freshness window
- verify that telematics and trip records agree on vehicle identity
- verify that a maintenance release is approved before return to service
- verify that chain-of-custody or handoff records are complete across shipment stages

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/transport_inspection_current.json`
- `tests/json/evidence/transport_inspection_stale.json`
- `tests/json/evidence/transport_inspection_incomplete.json`
- `tests/json/test_of_detail/verify_transport_inspection_status_completed.py`
- `tests/json/test_of_detail/verify_transport_inspection_recent.py`
- `tests/json/test_of_detail/verify_transport_inspection_readiness.py`

### Additional Current Repo Pack

This domain now also has an executable fleet or telematics reconciliation starter pack under:

- `tests/json/evidence/fleet_telematics_reconciled.json`
- `tests/json/evidence/fleet_telematics_missing_trip.json`
- `tests/json/evidence/fleet_telematics_mismatch.json`
- `tests/json/test_of_detail/verify_fleet_trip_record_present.py`
- `tests/json/test_of_detail/verify_fleet_telematics_vehicle_match.py`
- `tests/json/test_of_detail/verify_fleet_telematics_state_match.py`
- `tests/json/test_of_detail/verify_fleet_telematics_reconciliation.py`

### Why This Is A Strong Example Domain

- it is broader than fleet compliance alone
- it naturally uses time, identity, and reconciliation checks
- it covers movement, maintenance, handoff, and operational readiness evidence
- it fits text, JSON, XML, and CSV-like evidence patterns well

## Manufacturing And Industrial Operations

### Example Company Types

- discrete manufacturers
- process manufacturers
- plant operators
- industrial maintenance providers
- quality and production service providers

### High-Risk Assurance Problems

- unsafe or unreviewed controller or line configuration changes
- maintenance steps not completed before restart
- production run or work-order state not matching the claimed state
- stale backup or restore readiness evidence for plant systems
- unresolved quality exceptions before release or shipment

### Plausible Evidence

- work-order completion records
- line or controller configuration exports
- production run logs
- maintenance release or restart checklists
- quality exception and closure records
- backup and restore drill records

### Plausible Subjects

- `work_order_complete`
- `line_configuration_approved`
- `production_run_status`
- `maintenance_release_status`
- `quality_exception_closed`
- `restore_drill_status`

### Candidate Example Ideas

- verify that a maintenance release is approved before a line restart
- verify that a production run has the claimed completed status
- verify that a controller or line configuration change has an approval record
- verify that a quality exception was closed before product release
- verify that a restore drill completed successfully for the plant system

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/manufacturing_line_restart_ready.json`
- `tests/json/evidence/manufacturing_line_restart_incomplete_work_order.json`
- `tests/json/evidence/manufacturing_line_restart_blocked.json`
- `tests/json/test_of_detail/verify_manufacturing_maintenance_release_approved.py`
- `tests/json/test_of_detail/verify_manufacturing_work_order_complete.py`
- `tests/json/test_of_detail/verify_manufacturing_restart_authorization_approved.py`
- `tests/json/test_of_detail/verify_manufacturing_line_restart_readiness.py`

### Why This Is A Strong Example Domain

- it separates manufacturing from utilities while preserving OT relevance
- it mixes operational integrity, quality, and cyber-physical assurance
- it gives strong examples for work-order, status, and exception-closure verification

## Healthcare Delivery And Health Information

### Example Company Types

- hospitals
- clinics
- health systems
- revenue-cycle and health information service providers

### High-Risk Assurance Problems

- unauthorized access to sensitive health records
- stale access reviews for privileged users
- incomplete or conflicting patient-data handling records
- exceptions that bypass normal approval or review
- weak protection over electronic protected health information

### Plausible Evidence

- access review records
- privileged access approval records
- audit log extracts
- patient-data export approval records
- data retention and deletion execution logs

### Plausible Subjects

- `access_request_status`
- `approver_identifier`
- `last_review_timestamp`
- `data_export_ticket_present`
- `retention_execution_status`

### Candidate Example Ideas

- verify that privileged access had an approved status and a valid approver
- verify that the latest review is recent enough
- verify that a patient-data export has a linked approval record
- verify that a retention or deletion task completed successfully

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/privileged_access_grant.json`
- `tests/json/evidence/privileged_access_grant_missing_approver.json`
- `tests/json/evidence/privileged_access_grant_stale_review.json`
- `tests/json/test_of_detail/verify_privileged_access_status_approved.py`
- `tests/json/test_of_detail/verify_privileged_access_approver_required.py`
- `tests/json/test_of_detail/verify_privileged_access_review_recent.py`
- `tests/json/test_of_detail/verify_privileged_access_core_controls.py`

### Additional Current Repo Pack

This domain now also has an executable patient-data export governance starter pack under:

- `tests/json/evidence/patient_data_export_ready.json`
- `tests/json/evidence/patient_data_export_missing_approval.json`
- `tests/json/evidence/patient_data_export_retention_pending.json`
- `tests/json/test_of_detail/verify_patient_data_export_ticket_present.py`
- `tests/json/test_of_detail/verify_patient_data_export_approval_present.py`
- `tests/json/test_of_detail/verify_patient_data_retention_execution_completed.py`
- `tests/json/test_of_detail/verify_patient_data_export_governance.py`

### Why This Is A Strong Example Domain

- it gives a non-manufacturing but still high-risk example set
- it mixes privacy, access, and operational record integrity
- it translates well into simple and intermediate evaluator examples

## Medical Device And Digital Health Product Manufacturers

### Example Company Types

- connected medical device vendors
- diagnostic software vendors
- remote monitoring platform vendors
- device manufacturers with embedded software

### High-Risk Assurance Problems

- software components that cannot be traced or inventoried
- device cybersecurity evidence that is incomplete at release time
- patch or vulnerability handling that is not reflected in release records
- configuration states that could affect patient safety

### Plausible Evidence

- release packets
- software bill of materials records
- vulnerability disposition records
- design review approvals
- test execution and defect closure exports

### Plausible Subjects

- `sbom_present`
- `critical_vulnerability_count`
- `release_review_status`
- `safety_test_status`
- `security_signoff_present`

### Candidate Example Ideas

- verify that an SBOM is present for the release under review
- verify that no unresolved critical vulnerabilities remain at release
- verify that both safety and security signoff records exist
- verify that the release status is approved only after required review completion

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/medical_device_release_ready.json`
- `tests/json/evidence/medical_device_release_missing_sbom.json`
- `tests/json/evidence/medical_device_release_blocked.json`
- `tests/json/test_of_detail/verify_medical_device_release_review_approved.py`
- `tests/json/test_of_detail/verify_medical_device_sbom_present.py`
- `tests/json/test_of_detail/verify_medical_device_critical_vulnerability_count_maximum.py`
- `tests/json/test_of_detail/verify_medical_device_release_packet_readiness.py`

### Why This Is A Strong Example Domain

- it is one of the clearest safety-critical software examples
- it bridges product security, software verification, and patient-impact risk
- it helps represent application verification in a regulated setting

## Pharmaceutical, Laboratory, And Regulated Quality Operations

### Example Company Types

- pharmaceutical manufacturers
- biotech firms
- testing laboratories
- contract manufacturing or quality service providers

### High-Risk Assurance Problems

- incomplete audit trails
- unverified batch or sample state transitions
- missing review or release authorization
- data integrity concerns in test results or production records

### Plausible Evidence

- batch release records
- laboratory result files
- electronic audit trail exports
- deviation or exception records
- review signoff records

### Plausible Subjects

- `batch_release_status`
- `quality_reviewer_present`
- `audit_trail_complete`
- `sample_result_status`
- `deviation_closed`

### Candidate Example Ideas

- verify that a batch was released only after quality review
- verify that an audit trail entry exists for each required state transition
- verify that a deviation was closed before release
- verify that a laboratory result has an approved status and reviewer

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/quality_batch_release_ready.json`
- `tests/json/evidence/quality_batch_release_missing_reviewer.json`
- `tests/json/evidence/quality_batch_release_open_deviation.json`
- `tests/json/test_of_detail/verify_quality_batch_release_status_released.py`
- `tests/json/test_of_detail/verify_quality_reviewer_present.py`
- `tests/json/test_of_detail/verify_quality_deviation_closed.py`
- `tests/json/test_of_detail/verify_quality_batch_release_readiness.py`

### Why This Is A Strong Example Domain

- it gives a pure information-integrity and process-integrity example family
- it is a strong fit for status, presence, and timestamp patterns
- it makes “information management as assurance” very concrete

## Financial Services, Payments, And Insurance

### Example Company Types

- banks
- payment processors
- card service providers
- insurers
- fintech platforms

### High-Risk Assurance Problems

- unauthorized access to payment or customer records
- prohibited retention of sensitive authentication data
- weak approval or reconciliation around money movement
- stale control evidence around privileged or production access

### Plausible Evidence

- payment application configuration exports
- transaction approval records
- settlement reconciliation records
- access review records
- customer-data retention or masking reports

### Plausible Subjects

- `sensitive_auth_data_stored`
- `transaction_approval_status`
- `settlement_difference_amount`
- `privileged_access_review_timestamp`
- `pan_masking_enabled`

### Candidate Example Ideas

- verify that prohibited payment authentication data is not retained
- verify that a high-risk transaction has an approval record
- verify that settlement differences stay within the allowed tolerance
- verify that production payment access was reviewed recently enough

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/payment_settlement_balanced.json`
- `tests/json/evidence/payment_settlement_over_tolerance.json`
- `tests/json/evidence/payment_settlement_blocked.json`
- `tests/json/test_of_detail/verify_payment_transaction_approval_status.py`
- `tests/json/test_of_detail/verify_payment_reconciliation_status_completed.py`
- `tests/json/test_of_detail/verify_payment_settlement_difference_within_tolerance.py`
- `tests/json/test_of_detail/verify_payment_settlement_readiness.py`

### Why This Is A Strong Example Domain

- it covers both cyber and transaction-integrity assurance
- it naturally supports reconciliation examples
- it makes value mismatch and tolerance patterns concrete

## Enterprise Software, SaaS, And Cloud Platforms

### Example Company Types

- SaaS vendors
- enterprise software vendors
- internal platform teams
- cloud-native application providers

### High-Risk Assurance Problems

- insecure-by-default release states
- missing security review or release gates
- unresolved critical vulnerabilities at deployment time
- weak identity controls for admin paths
- insufficient evidence that security-relevant tests actually ran

### Plausible Evidence

- CI/CD outputs
- release manifests
- vulnerability scan results
- admin configuration exports
- deployment approval records

### Plausible Subjects

- `mfa_required`
- `critical_vulnerability_count`
- `security_review_status`
- `deployment_approval_present`
- `artifact_signature_verified`

### Candidate Example Ideas

- verify that MFA is required for admin access
- verify that the release has a security review signoff
- verify that critical vulnerabilities are below the allowed threshold
- verify that deployment approval is present before production promotion

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/application_release_ready.json`
- `tests/json/evidence/application_release_mfa_disabled.json`
- `tests/json/evidence/application_release_blocked.json`
- `tests/json/test_of_detail/verify_application_mfa_required.py`
- `tests/json/test_of_detail/verify_application_critical_vulnerability_count_maximum.py`
- `tests/json/test_of_detail/verify_application_deployment_approval_present.py`
- `tests/json/test_of_detail/verify_application_release_readiness.py`

### Why This Is A Strong Example Domain

- it gives application verification examples directly
- it is familiar to engineering-heavy users
- it provides a good bridge between operational assurance and software assurance

## Public Sector, Defense, And Mission Systems

### Example Company Types

- civilian agencies
- defense contractors
- mission system integrators
- emergency service operators

### High-Risk Assurance Problems

- weak boundary control between interconnected systems
- stale authorizations or reviews for mission-sensitive access
- inability to prove that a required event actually happened
- incomplete traceability across system-of-systems handoffs

### Plausible Evidence

- interconnection approval records
- mission access approvals
- sensor or event logs
- configuration baselines
- cross-system status reconciliation exports

### Plausible Subjects

- `interconnection_approval_present`
- `boundary_control_status`
- `event_confirmation_status`
- `mission_access_review_timestamp`
- `cross_system_state_match`

### Candidate Example Ideas

- verify that a system interconnection has a current approval record
- verify that the claimed event appears in both originating and receiving system logs
- verify that mission access reviews are recent enough
- verify that two connected systems agree on operational state

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/system_event_confirmation_ready.json`
- `tests/json/evidence/system_event_confirmation_missing_approval.json`
- `tests/json/evidence/system_event_confirmation_mismatch.json`
- `tests/json/test_of_detail/verify_system_interconnection_approval_present.py`
- `tests/json/test_of_detail/verify_system_event_confirmation_status_confirmed.py`
- `tests/json/test_of_detail/verify_system_cross_state_match.py`
- `tests/json/test_of_detail/verify_system_of_systems_event_confirmation.py`

### Additional Current Repo Pack

This domain now also has an executable mission access review starter pack under:

- `tests/json/evidence/mission_access_review_ready.json`
- `tests/json/evidence/mission_access_review_missing_approval.json`
- `tests/json/evidence/mission_access_review_stale.json`
- `tests/json/test_of_detail/verify_mission_access_status_authorized.py`
- `tests/json/test_of_detail/verify_mission_access_approval_present.py`
- `tests/json/test_of_detail/verify_mission_access_review_recent.py`
- `tests/json/test_of_detail/verify_mission_access_readiness.py`

### Why This Is A Strong Example Domain

- it is the clearest system-of-systems example family
- it supports multi-record, multi-source evidence reasoning
- it keeps the focus on verification of facts rather than transport-side policy logic

## Food, Agriculture, And Cold Chain

### Example Company Types

- food processors
- cold-chain distributors
- agricultural operators
- warehouse and fulfillment providers

### High-Risk Assurance Problems

- missing temperature, inspection, or chain-of-custody evidence
- stale sanitation or safety checks
- mismatched shipment and storage records
- unverified exception handling for spoilage or out-of-range conditions

### Plausible Evidence

- temperature logs
- inspection records
- shipment scan histories
- chain-of-custody records
- exception closure records

### Plausible Subjects

- `temperature_excursion_count`
- `last_sanitation_check_timestamp`
- `chain_of_custody_complete`
- `shipment_state_match`
- `exception_closed`

### Candidate Example Ideas

- verify that no out-of-range temperature excursion remains unresolved
- verify that sanitation checks happened within the required window
- verify that custody records are complete across handoffs
- verify that shipment and storage states reconcile

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/cold_chain_exception_ready.json`
- `tests/json/evidence/cold_chain_exception_incomplete_custody.json`
- `tests/json/evidence/cold_chain_exception_open.json`
- `tests/json/test_of_detail/verify_cold_chain_temperature_excursion_count_maximum.py`
- `tests/json/test_of_detail/verify_cold_chain_chain_of_custody_complete.py`
- `tests/json/test_of_detail/verify_cold_chain_exception_closed.py`
- `tests/json/test_of_detail/verify_cold_chain_exception_readiness.py`

### Why This Is A Strong Example Domain

- it broadens the examples beyond classic cyber and finance use cases
- it gives strong operational and physical-world assurance examples
- it is a good fit for time-series and event-log style evidence

## Aviation, Maritime, And Other Safety-Critical Operations

### Example Company Types

- airlines
- maintenance organizations
- airport operators
- maritime operators
- offshore support operators

### High-Risk Assurance Problems

- incomplete maintenance release evidence
- missing safety review or hazard closure
- weak traceability between planned and completed operational work
- stale inspection, calibration, or readiness evidence

### Plausible Evidence

- maintenance release records
- inspection reports
- readiness checklists
- hazard logs
- work-order completion exports

### Plausible Subjects

- `maintenance_release_status`
- `inspection_timestamp`
- `hazard_closure_status`
- `work_order_complete`
- `calibration_current`

### Candidate Example Ideas

- verify that a maintenance release is approved before return to service
- verify that a required inspection is recent enough
- verify that a recorded hazard is closed before the work item proceeds
- verify that a calibration is current for a safety-relevant asset

### Current Repo Pack

This domain now has an executable starter pack under:

- `tests/json/evidence/return_to_service_ready.json`
- `tests/json/evidence/return_to_service_open_hazard.json`
- `tests/json/evidence/return_to_service_blocked.json`
- `tests/json/test_of_detail/verify_return_to_service_maintenance_release_approved.py`
- `tests/json/test_of_detail/verify_return_to_service_hazard_closure_closed.py`
- `tests/json/test_of_detail/verify_return_to_service_calibration_current.py`
- `tests/json/test_of_detail/verify_return_to_service_readiness.py`

### Why This Is A Strong Example Domain

- it represents explicit safety management rather than only cyber control
- it gives strong timestamp and state-verification examples
- it maps well to systems where “did the event really happen?” matters more than abstract compliance

## Special Cross-Domain Example Families

Some example families cut across many industries and should probably become reusable packs rather than single-vertical artifacts.

### IT / OT Boundary Pack

Good domains:

- utilities
- manufacturing
- transport infrastructure

Good example ideas:

- remote access path review
- internet exposure verification
- backup / restore drill verification

### Fleet And Mobile Operations Pack

Good domains:

- logistics
- field service
- public transport

Good example ideas:

- trip record presence
- inspection freshness
- telematics reconciliation

### Application Verification Pack

Good domains:

- SaaS
- enterprise software
- digital health products
- payment applications

Good example ideas:

- vulnerability threshold
- release approval status
- MFA/admin control state
- release artifact integrity

### System-Of-Systems Pack

Good domains:

- mission systems
- integrated transport operations
- smart facilities
- industrial supervisory systems

Good example ideas:

- cross-system state reconciliation
- interconnection approval verification
- event confirmation across multiple sources

## Recommended Example-Pack Sequencing

My current recommendation is:

### Starter Domains

- privileged access review
- utility or field restore drill verification
- transportation inspection freshness
- invoice approval and owner verification

These are strong starters because they are recognizable, bounded, and can usually stay within one evidence source.

### Intermediate Domains

- transportation maintenance release or telematics reconciliation verification
- manufacturing maintenance release and work-order verification
- payment application or settlement reconciliation verification
- laboratory or batch review verification

These are stronger second-stage examples because they introduce either typed evidence, reconciliation, or domain language that is still broadly understandable.

### Advanced Domains

- IT / OT boundary verification
- medical device release assurance
- system-of-systems event confirmation

These are better later because they require more context and often more than one fact or more than one evidence seam.

## Recommended First Implementation Pack

If we want the first concrete domain-rich implementation set to be broad but still coherent, I recommend this set:

1. privileged access approval and review assurance
2. utility or field restore drill assurance
3. transportation inspection freshness assurance
4. manufacturing maintenance release and work-order assurance
5. payment or settlement reconciliation assurance
6. medical device release packet assurance
7. pharmaceutical or laboratory regulated quality release assurance
8. food or cold-chain exception assurance
9. system-of-systems event confirmation assurance
10. IT / OT boundary verification assurance
11. application verification assurance
12. public-sector or mission access review assurance
13. fleet or telematics reconciliation assurance
14. aviation or maintenance return-to-service assurance
15. healthcare patient-data export governance assurance

Why this first pack set:

- it spans enterprise authorization, utilities / field infrastructure, transportation, manufacturing, business-process assurance, and regulated quality operations
- each example can stay fact-verification-centered without needing a complex policy language
- together they represent information-system, operational / physical-world, financial-process, safety-critical product, regulated quality, custody / exception, multi-source confirmation, explicit boundary verification, software release, access-governance, fleet reconciliation, and healthcare data-governance assurance
- they are understandable to readers before we move into heavier reconciliation or system-of-systems examples

Current implementation status:

- privileged access approval and review assurance is now implemented as the first domain-rich pack
- utility or field restore drill assurance is now implemented as the second domain-rich pack
- transportation inspection freshness assurance is now implemented as the third domain-rich pack
- manufacturing maintenance release and work-order assurance is now implemented as the fourth domain-rich pack
- payment or settlement reconciliation assurance is now implemented as the fifth domain-rich pack
- medical device release packet assurance is now implemented as the sixth domain-rich pack
- pharmaceutical or laboratory regulated quality release assurance is now implemented as the seventh domain-rich pack
- food or cold-chain exception assurance is now implemented as the eighth domain-rich pack
- system-of-systems event confirmation assurance is now implemented as the ninth domain-rich pack
- IT / OT boundary verification assurance is now implemented as the tenth domain-rich pack
- application verification assurance is now implemented as the eleventh domain-rich pack
- public-sector or mission access review assurance is now implemented as the twelfth domain-rich pack
- fleet or telematics reconciliation assurance is now implemented as the thirteenth domain-rich pack
- aviation or maintenance return-to-service assurance is now implemented as the fourteenth domain-rich pack
- healthcare patient-data export governance assurance is now implemented as the fifteenth domain-rich pack

## Selected Example-Pack Set For This Repo

If the goal is to see the currently selected broad example-pack set in one place, use:

1. privileged access approval and review assurance
2. utility or field restore drill assurance
3. transportation inspection and trip evidence assurance
4. manufacturing maintenance release and work-order assurance
5. payment or settlement reconciliation assurance
6. medical device release packet assurance
7. pharmaceutical or laboratory regulated quality release assurance
8. food or cold-chain exception assurance
9. system-of-systems event confirmation assurance
10. IT / OT boundary verification assurance
11. application verification assurance
12. public-sector or mission access review assurance
13. fleet or telematics reconciliation assurance
14. aviation or maintenance return-to-service assurance
15. healthcare patient-data export governance assurance

That set gives:

- authorization assurance
- utility / field operational assurance
- transportation operational assurance
- manufacturing operational assurance
- financial / business assurance
- safety-critical product assurance
- regulated quality assurance
- physical-world custody and exception assurance
- multi-source confirmation assurance
- explicit boundary verification assurance
- software release assurance
- access-governance assurance
- fleet reconciliation assurance
- safety return-to-service assurance
- healthcare data-governance assurance

## Source Anchors

These sources informed the sector themes and example recommendations:

- FMCSA Electronic Logging Devices:
  - https://www.fmcsa.dot.gov/hours-service/elds/electronic-logging-devices
- FDA medical device cybersecurity guidance is reflected in current public references to:
  - "Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions"
  - https://en.wikipedia.org/wiki/Medical_software
  - https://en.wikipedia.org/wiki/Medical_device
- NERC Critical Infrastructure Protection standards overview:
  - https://en.wikipedia.org/wiki/Information_security_standards
- HIPAA / health information security overview:
  - https://en.wikipedia.org/wiki/Health_Insurance_Portability_and_Accountability_Act
- PCI DSS / payment security overview:
  - https://en.wikipedia.org/wiki/Payment_Card_Industry_Data_Security_Standard
- broader critical infrastructure and system-of-systems context:
  - https://en.wikipedia.org/wiki/Critical_infrastructure
  - https://en.wikipedia.org/wiki/U.S._critical_infrastructure_protection

Recommendations on example-pack sequencing and exact evaluator example ideas are my inference from those sector anchors, not language taken directly from those sources.
