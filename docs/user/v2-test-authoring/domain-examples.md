# Domain Examples

This page gives a few differing example domains that are common in assurance work and often feed into larger control or assurance frameworks.

No specific framework is required for these examples.

## IT Assurance Example

### Topic

Backup recovery evidence

### Example detail under test

Verify that the most recent successful backup restore drill completed within the required time window.

### Plausible subjects

- `restore_drill_status`
- `restore_drill_duration_minutes`
- `restore_drill_timestamp`

### Why it is useful

- common operational assurance topic
- easy to represent as evidence plus thresholds
- maps well to status, duration, and timestamp checks

## Authorization Assurance Example

### Topic

Privileged access approval and review evidence

### Example detail under test

Verify that a privileged access grant has an approved status, a valid approver, and a review timestamp within the allowed age window.

### Plausible subjects

- `access_request_status`
- `approver_identifier`
- `last_review_timestamp`

### Why it is useful

- common authorization assurance topic
- combines presence, equality, and temporal checks
- can expand into multi-subject conditional logic if needed

## Business Process Assurance Example

### Topic

Invoice approval and match evidence

### Example detail under test

Verify that an invoice is in an approved state, has a valid owner, and that the invoice amount matches the expected business rule or tolerance.

### Plausible subjects

- `invoice_status`
- `invoice_owner`
- `invoice_amount`

### Why it is useful

- common business process assurance topic
- can start simple and later grow into tolerance or segregation-style policy logic

## Suggested Anchor Examples For This Repo

If you want one simple starter example plus one richer conditional example, use:

- simple starter:
  - privileged access approval status
- richer conditional example:
  - branch coverage plus line coverage policy

That gives one non-technical assurance domain example and one engineering-policy example without forcing the guide set into only one kind of assurance use case.
