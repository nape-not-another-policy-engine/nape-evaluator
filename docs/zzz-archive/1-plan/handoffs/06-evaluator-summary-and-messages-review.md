> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 06: Evaluator Summary And Messages Review

## Purpose

Resume the evaluator summary/messages review without re-deriving the current runtime boundary.

## Status

This workstream is complete.

The approved summary/message contract change is now implemented in code, tests, and permanent docs.

Do not continue this workstream by default.

Open any new follow-up as its own workstream if a new product decision is needed.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/06-evaluator-summary-and-messages-review.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/nape-evaluator-product-spec.md`
5. `docs/reference/evaluator-contract.md`
6. `src/nape_evaluator/domain/use_cases.py`
7. `src/nape_evaluator/application/io/output_contract.py`
8. `tests/test_evaluator_use_case.py`
9. `tests/test_output_contract.py`

## Current State

- the evaluator still emits:
  - `results`
  - `evaluator.messages`
  - `evaluator.summary`
- the current runtime distinction is:
  - `results[*].result.reason` is test-owned reasoning from a completed test
  - `evaluator.messages[*]` are evaluator-owned operational notices
  - `summary.message_error` counts evaluator/runtime error messages
- multi-test runs against one evidence file are supported
- the landed implementation now uses:
  - keep top-level `evaluator.messages`
  - distinct-event message counting semantics
  - explicit message `scope`
  - `affected_tests` on request-scoped shared events
  - only:
    - `true`
    - `false`
    - `inconclusive`
    as result conclusions
  - evaluator-synthesized blocked `inconclusive` results
  - `stack_trace` on evaluator messages when traceback detail exists, especially for execution errors
- permanent docs and examples now show:
  - successful single-test output
  - multi-test shared-warning output
  - blocked-test output
- focused and broader tests now cover:
  - distinct-event summary counting
  - request-scoped versus test-scoped message shaping
  - blocked-result synthesis
  - completed invalid-result normalization to `inconclusive`
  - executable authoring sample fixtures aligned to the current contract

## Closure Decision

This workstream is complete.

Its durable outputs now live in:

- `docs/product/current-evaluator-reference.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/cli-reference.md`
- `docs/examples/README.md`
- `src/nape_evaluator/domain/use_cases.py`
- `src/nape_evaluator/domain/use_case_models.py`
- `src/nape_evaluator/application/io/output_contract.py`
- `src/nape_evaluator/application/driver/evidence_gateway.py`
- focused and broader evaluator tests

## Remaining Ambiguities

- none at the Step 1.0 contract-detail level
- future implementation planning can now proceed from a fully specified proposed direction unless a new product decision changes it

## Guardrails

- do not collapse evaluator-owned operational problems into test-owned reasoning without an explicit product decision
- do not remove `summary` or `messages` by assumption
- do not mix the clarification pass with the later “inconclusive for evaluator error” decision
- keep the evaluator claim-agnostic

## Expected Near-Term Outputs

- none by default; treat this handoff as historical closure context
