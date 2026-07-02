# Plan 01: Structured Verification V2

## Goal

Expand the evaluator's current flat request/result contract into a clearer V2 structured model without changing the evaluator's core responsibility.

## Status

Completed as proposal-shaping work. Follow-on implementation planning now lives in `docs/1-plan/plans/03-structured-verification-v2-implementation-planning.md`.

## Baseline

This plan builds on the current implemented evaluator model:

- one shared evidence input per invocation
- one or more requested test invocations
- evaluator-owned execution and summary behavior
- test-owned fact extraction, comparison logic, and human-readable reasoning

Read first:

1. `docs/product/current-evaluator-reference.md`
2. `docs/product/nape-evaluator-product-spec.md`
3. `docs/product/v2-structured-verification-input-proposal.md`
4. `docs/product/v2-structured-verification-result-proposal.md`

## Current State

Current committed behavior:

- test call boundary is `evaluate(evidence, test_parameters, metadata)`
- per-test output is a flat row with `executed`, `outcome`, and `reason`
- evaluator messages and summary data are emitted separately under `evaluator`

Current proposal direction:

- caller-owned input now uses `test` + `evidence` + `evaluations`
- each evaluation item uses `subject` plus object-valued `criteria`
- the aligned test boundary is `evaluate(evidence, evaluations, metadata)`
- per-test output now moves toward explicit outer `execution` plus one combined structured `result`
- the aligned `result` direction is `conclusion`, `facts`, and `reason`, while caller-owned `evaluations` is echoed in the outer envelope

## Scope

In scope:

- proposal refinement for V2 structured input
- proposal refinement for V2 structured result output
- before/after recording for terminology and structure changes
- explicit preservation of current evaluator fundamentals

Out of scope:

- unrelated CLI transport redesign
- claim semantics
- verification report generation
- code implementation before the proposal is sufficiently approved

## Work Plan

1. Keep the baseline explicit.
   Every proposal change should remain anchored to `current-evaluator-reference.md`.

2. Lock the caller-owned input shape.
   Clarify what the caller provides, what the evaluator derives, and what the test receives.

3. Lock the per-test structured result shape.
   Clarify what belongs to evaluator-owned execution state versus test-owned result content.

4. Clarify fact and criteria representation.
   Keep machine-readable fact records and caller-owned echoed criteria understandable for later verification-procedure/report work.

5. Clarify migration pressure.
   Record what changes from the current flat contract to the proposed V2 shape and what remains the same.

6. Reflect approved decisions into permanent docs.
   Product, user, and reference docs should absorb approved decisions once they are stable enough.

## Open Questions

- Which fields are echoed from caller input versus derived by the evaluator versus returned by the test?
- When implementation planning begins, which validation rules should remain evaluator-owned versus test-owned?
- Which proposal decisions are documentation-only for now versus implementation-ready?

## Done Criteria

This plan is ready to close when:

- the V2 input proposal is coherent and grounded in current behavior
- the V2 result proposal is coherent and grounded in current behavior
- before/after records clearly explain the changes from the current contract
- approved durable decisions have been moved into permanent product/reference/user docs
- selected V2 test-authoring guidance exists in durable user docs with a scaffold and input-pattern library
- any remaining implementation work is handed off as explicit follow-up work rather than hidden in proposal text
