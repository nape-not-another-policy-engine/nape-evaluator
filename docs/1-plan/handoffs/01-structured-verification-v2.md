# Handoff 01: Structured Verification V2

## Purpose

Resume V2 structured verification proposal work without re-deriving the evaluator baseline.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/01-structured-verification-v2.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/nape-evaluator-product-spec.md`
5. `docs/product/v2-structured-verification-input-proposal.md`
6. `docs/product/v2-structured-verification-result-proposal.md`

## Current State

- the current evaluator baseline has been written down in `docs/product/current-evaluator-reference.md`
- the product spec now points to that baseline reference
- the V2 input proposal explicitly says it is an expansion of the current evaluator model
- the V2 result proposal explicitly says it is an expansion of the current evaluator model
- proposal terminology currently explores `expectation`, `execution`, `result`, `conclusion`, `facts`, and `expectations`

## Resume Focus

When resuming this plan, focus on:

1. tightening the proposal details rather than rethinking the evaluator's core role
2. recording current-to-V2 before/after changes clearly
3. keeping fact extraction inside the test and execution ownership with the evaluator
4. deciding only the structure that is needed for the next V2 step

## Guardrails

- do not remove the current baseline framing
- do not add claim semantics to evaluator packets
- do not let proposal examples imply that facts are pre-extracted before the test runs
- do not drift into CLI ergonomics; that belongs primarily to Plan 02

## Next Useful Outputs

- tighter proposal examples
- clarified migration notes from current flat result rows to structured result items
- explicit separation of approved decisions versus open questions
