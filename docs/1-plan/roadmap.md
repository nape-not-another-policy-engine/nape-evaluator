# NAPE Evaluator Roadmap

This roadmap is the planning index for evaluator-specific work.

## Start Order

When resuming evaluator work:

1. read `docs/1-plan/roadmap.md`
2. read the active plan document
3. read the matching handoff document
4. re-ground on `docs/product/current-evaluator-reference.md`

## Baseline Already Established

The following baseline work is already in place and should be treated as prerequisite context, not as a separate active plan:

- `docs/product/current-evaluator-reference.md`
  Current committed evaluator behavior.
- `docs/product/nape-evaluator-product-spec.md`
  Current product scope and direction.
- `docs/product/v2-structured-verification-input-proposal.md`
  Proposed V2 input expansion.
- `docs/product/v2-structured-verification-result-proposal.md`
  Proposed V2 result expansion.

## Active Workstreams

### Plan 01: Structured Verification V2

Status:

- active

Purpose:

- expand evaluator input/output structure for V2 while preserving the current evaluator execution model

Plan:

- `docs/1-plan/plans/01-structured-verification-v2.md`

Handoff:

- `docs/1-plan/handoffs/01-structured-verification-v2.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-structured-verification-input-proposal.md`
- `docs/product/v2-structured-verification-result-proposal.md`

### Plan 02: Expectation Binding And CLI Transport

Status:

- active

Purpose:

- decide and document how caller-supplied expectation input should be transported and bound to requested test executions

Plan:

- `docs/1-plan/plans/02-expectation-binding-and-cli-transport.md`

Handoff:

- `docs/1-plan/handoffs/02-expectation-binding-and-cli-transport.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/test-parameter-exploration.md`
- `docs/user/cli-reference.md`
- `docs/reference/evaluator-contract.md`

## Sequencing Notes

- Plan 01 owns the higher-level V2 input/output shape and terminology direction.
- Plan 02 must stay aligned with Plan 01, especially where current `test_parameters` language may later become V2 `expectation` language.
- Both plans should preserve the current evaluator fundamentals unless a product decision explicitly changes them.

## Operating Rule

If a new evaluator-specific workstream appears:

1. add it here first
2. create its plan doc
3. create its handoff doc
4. update `AGENTS.md` only if the start order or operating rules change
