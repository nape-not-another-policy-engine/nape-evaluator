> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 01: Structured Verification V2

## Purpose

Resume V2 structured verification proposal work without re-deriving the evaluator baseline.

## Status

Proposal-shaping work for this plan is complete. Follow-on implementation planning now lives in `docs/zzz-archive/1-plan/plans/03-structured-verification-v2-implementation-planning.md`.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/01-structured-verification-v2.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/nape-evaluator-product-spec.md`
5. `docs/product/v2-structured-verification-input-proposal.md`
6. `docs/product/v2-structured-verification-result-proposal.md`

## Current State

- the current evaluator baseline has been written down in `docs/product/current-evaluator-reference.md`
- the product spec now points to that baseline reference
- the V2 input proposal explicitly says it is an expansion of the current evaluator model
- the V2 result proposal explicitly says it is an expansion of the current evaluator model
- the V2 input proposal now uses `evaluations`, `subject`, and `criteria` as the selected caller-owned input terms
- the selected outer request shape is `test` + `evidence` + `evaluations`
- each `evaluations[*]` item now uses one `subject` plus one object-valued `criteria` packet that may contain multiple compatible first-pass keys
- the proposal now includes bounded `subject.data_type` definitions, compatibility guidance, strict no-coercion rules, and a dedicated invariants/examples section
- the proposal now recommends `evaluate(evidence, evaluations, metadata)` as the aligned V2 test call boundary
- the V2 result proposal is now aligned to the selected input model and echoes outer caller-owned `evaluations` while using one combined test-owned `result`
- after result-proposal alignment and cleanup of older `expectation`-based user/reference docs, a later follow-up can tighten validation precision around contradictory multi-key `criteria`, typed `allowed_values` / `disallowed_values`, and whether `equals` on `array` / `object` means exact structural equality only
- downstream user/reference/test-authoring and maintainer/internal docs now carry labeled V2 direction notes alongside current-implementation material
- test authoring docs now include a V2 section and a starter library of plausible evaluation-input patterns, including simple threshold, equality, membership, presence, temporal, and multi-subject conditional-policy shapes
- maintainer/internal docs now also include clearly labeled selected V2 direction notes without rewriting current committed implementation references as if runtime behavior had already changed
- the next likely step is implementation planning against the now-aligned V2 proposal and downstream documentation set

## Resume Focus

When resuming this plan, focus on:

1. tightening the proposal details rather than rethinking the evaluator's core role
2. recording current-to-V2 before/after changes clearly
3. keeping fact extraction inside the test and execution ownership with the evaluator
4. deciding only the structure that is needed for the next V2 step
5. beginning implementation planning against the selected `evaluations[*].subject` / `criteria` input model and the combined V2 result model

## Guardrails

- do not remove the current baseline framing
- do not add claim semantics to evaluator packets
- do not let proposal examples imply that facts are pre-extracted before the test runs
- do not drift into CLI ergonomics; that belongs primarily to Plan 02

## Next Useful Outputs

- updates to user/reference docs that still describe the earlier `expectation`-based proposal direction
- updates to test authoring docs that teach `evaluate(evidence, evaluations, metadata)` and one combined structured `result` return
- clarified migration notes from current flat result rows to the selected combined V2 result content
- implementation-planning work that can begin from the now-aligned V2 proposal and downstream documentation set
