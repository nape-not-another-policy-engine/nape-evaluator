# Plan 20: Domain Example Pack Implementation Wave 5

## Purpose

Implement the fifth domain-rich example pack as executable evaluator examples and routing docs.

Wave 5 starts with payment or settlement reconciliation assurance.

## Why This Exists

The first four domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, and manufacturing line restart readiness.

The next gap is a financial and business-process assurance example family centered on approval and reconciliation around money movement.

## Selected Direction

The implemented pack will be:

- payment or settlement reconciliation assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent payment or settlement evidence family
2. transaction approval status fixture
3. settlement difference tolerance fixture
4. reconciliation status fixture
5. one combined settlement readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new payment settlement evidence fixtures:
  - `tests/json/evidence/payment_settlement_balanced.json`
  - `tests/json/evidence/payment_settlement_over_tolerance.json`
  - `tests/json/evidence/payment_settlement_blocked.json`
- new payment settlement single-subject fixtures:
  - `tests/json/test_of_detail/verify_payment_transaction_approval_status.py`
  - `tests/json/test_of_detail/verify_payment_reconciliation_status_completed.py`
  - `tests/json/test_of_detail/verify_payment_settlement_difference_within_tolerance.py`
- new payment settlement combined fixture:
  - `tests/json/test_of_detail/verify_payment_settlement_readiness.py`
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

- the payment settlement pack is complete enough to serve as the fifth domain-rich exemplar
- the cross-pack progression remains coherent from authorization through operational assurance into business-process reconciliation
