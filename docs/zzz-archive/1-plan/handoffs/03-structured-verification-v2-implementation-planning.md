> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 03: Structured Verification V2 Implementation Planning

## Purpose

Record the completed state and closure decision for the V2 implementation-planning workstream.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/03-structured-verification-v2-implementation-planning.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/zzz-archive/product/v2-structured-verification-input-proposal.md`
5. `docs/zzz-archive/product/v2-structured-verification-result-proposal.md`
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
- the earlier CLI transport dependency is now resolved because Plan 02 is complete
- the current remaining work is narrower:
  - residual legacy cleanup outside explicit historical notes
  - any implementation-grade validation precision gaps
  - deciding whether Plan 03 is ready to close after that cleanup
- that closure review is now complete
- the last implementation-grade issue found in that review was duplicate `subject.name` within one invocation:
  - the request builder now rejects duplicates
  - test coverage now exists for that validation
- the remaining old-shape references are now confined to explicit historical notes, preserved audit/planning traceability, or future-thinking material

## Closure Decision

This workstream is complete.

Do not continue it by default.

If future implementation work is needed, treat it as a new explicit workstream rather than unfinished residue from Plan 03.

## Why It Closed

- the selected V2 request/result/runtime cutover is implemented
- the selected CLI transport direction is implemented and Plan 02 is complete
- permanent docs are aligned closely enough with the runtime
- the residual legacy cleanup pass has been completed
- the last concrete validation-hardening issue found during closure review has been fixed
- no remaining active runtime contradiction or current-doc contradiction justifies keeping the plan open

## Resume Focus

Only reopen a similar workstream if one of these becomes true:

1. a new implementation-grade validation gap is discovered
2. product direction expands the bounded first-pass criteria surface
3. the runtime and current docs drift apart in a material way
4. a new response/request contract change is selected

## Guardrails

- do not quietly re-open the selected V2 terminology
- do not reopen the selected packet-based CLI transport without a new explicit need
- do not collapse evaluator-owned execution failures into test-owned conclusions
- do not plan any tuple-return compatibility shim
- do not move caller-owned V2 request validation into the gateway or scatter it across the use case body

## Durable Outputs

- the implemented V2 runtime:
  - builder-only request seam
  - packet-based CLI transport
  - structured outer execution plus inner result contract
- the aligned current docs
- the completed residual legacy cleanup pass
- the duplicate-subject validation added during closure review
