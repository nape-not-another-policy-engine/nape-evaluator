# Handoff 03: Structured Verification V2 Implementation Planning

## Purpose

Resume V2 implementation planning from the audited codebase rather than re-deriving the selected proposal shape.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/03-structured-verification-v2-implementation-planning.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/v2-structured-verification-input-proposal.md`
5. `docs/product/v2-structured-verification-result-proposal.md`
6. `src/nape_evaluator/domain/use_case_models.py`
7. `src/nape_evaluator/domain/use_cases.py`
8. `src/nape_evaluator/application/io/cli.py`
9. `src/nape_evaluator/application/io/output_contract.py`

## Current State

- the selected V2 proposal direction is now documented and aligned across input, result, user, reference, and maintainer docs
- Plan 01 is complete as proposal-shaping work and now hands off to implementation planning
- the first V2 runtime cut is now implemented in code and tests
- the current code-path audit for V2 implementation planning has now been recorded in Plan 03
- the migration stance is now selected: V2 runtime must be a clean contract cutover, not a compatibility-layer transition
- the selected request-seam direction is now also recorded: `EvaluateEvidenceRequest` should become a builder-only verified use-case request seam, with request validation concentrated in `try_build()`
- the selected response-side direction is now also recorded: post-execution test `result` validation should live in `EvaluateEvidenceResponse`
- the selected V2 completed-test conclusion vocabulary is now `true` / `false` / `inconclusive` / `error`
- Plan 03 now includes an explicit implementation task breakdown by file, test surface, and execution order
- the implemented runtime now uses:
  - `EvaluateEvidenceRequest.builder()` and `try_build()`
  - packet-based CLI transport through `--invoke`, `--invoke-file`, and `--request-file`
  - `evaluate(evidence, evaluations, metadata)`
  - outer `execution` plus inner structured `result`
- the permanent docs are now largely aligned to that runtime:
  - root `README.md`
  - current product/reference docs
  - user quickstart and authoring docs
  - maintainer architecture/testing/review docs
- the V2 authoring docs now also include:
  - a progression guide from hardcoded starter tests to defensive input-driven tests
  - a pattern-library view of current canonical, later, and boundary evaluation-input shapes
  - executable canonical pattern fixtures under `tests/json/test_of_detail/`
- the V2-focused and full repository test suites are currently passing
- the highest-impact code paths are:
  - `src/nape_evaluator/application/io/cli.py`
  - `src/nape_evaluator/domain/use_case_models.py`
  - `src/nape_evaluator/domain/use_cases.py`
  - `src/nape_evaluator/application/io/output_contract.py`
- evidence loading appears reusable with minimal structural change
- CLI transport remains the largest cross-plan dependency because Plan 02 still owns how caller input is bound into requests

## Resume Focus

When resuming this plan, focus on:

1. turning the audited phases into implementation-ready tasks
2. checking for any remaining narrow legacy references or null legacy fields that should be removed rather than merely documented
3. tightening any remaining validation precision only if implementation-grade gaps are still present
4. deciding whether any remaining plan material should be promoted into permanent docs or code comments

## Guardrails

- do not quietly re-open the selected V2 terminology
- do not assume CLI ergonomics that Plan 02 has not selected yet
- do not collapse evaluator-owned execution failures into test-owned conclusions
- do not plan any tuple-return compatibility shim
- do not move caller-owned V2 request validation into the gateway or scatter it across the use case body

## Next Useful Outputs

- any residual legacy cleanup outside the now-removed `test_parameters_source` field
- any follow-up validation precision tasks discovered during doc alignment
- any remaining implementation planning notes that are still worth carrying forward after the runtime/doc cutover
- any future expansion of the bounded first-pass criteria surface if richer conditional-policy input becomes a product requirement
