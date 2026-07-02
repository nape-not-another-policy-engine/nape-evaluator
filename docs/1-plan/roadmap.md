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

## Workstreams

### Plan 07: Evaluator Software Integration Guide

Status:

- complete

Purpose:

- define and author the user-facing guide set for software that wraps `nape-evaluator` as a component, grounded in the current CLI packet contract rather than an unstated library API

Plan:

- `docs/zzz-archive/1-plan/plans/07-evaluator-software-integration-guide.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/07-evaluator-software-integration-guide.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/cli-reference.md`
- `docs/product/nape-evaluator-product-spec.md`
- `../../specifications/engineering-standards/6-requirements/21-use-case-documentation-requirements.md`

### Plan 06: Evaluator Summary And Messages Review

Status:

- complete

Purpose:

- review, clarify, and if needed tighten how evaluator-level `summary` and `messages` work, especially for multiple requested tests against one evidence file

Plan:

- `docs/zzz-archive/1-plan/plans/06-evaluator-summary-and-messages-review.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/06-evaluator-summary-and-messages-review.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/nape-evaluator-product-spec.md`
- `docs/reference/evaluator-contract.md`
- `src/nape_evaluator/domain/use_cases.py`
- `src/nape_evaluator/application/io/output_contract.py`
- `tests/test_evaluator_use_case.py`
- `tests/test_output_contract.py`

### Plan 01: Structured Verification V2

Status:

- complete

Purpose:

- expand evaluator input/output structure for V2 while preserving the current evaluator execution model

Plan:

- `docs/zzz-archive/1-plan/plans/01-structured-verification-v2.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/01-structured-verification-v2.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-structured-verification-input-proposal.md`
- `docs/product/v2-structured-verification-result-proposal.md`

### Plan 02: Expectation Binding And CLI Transport

Status:

- complete

Purpose:

- decide and document how caller-supplied evaluation input should be transported and bound to requested test executions

Plan:

- `docs/zzz-archive/1-plan/plans/02-expectation-binding-and-cli-transport.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/02-expectation-binding-and-cli-transport.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/test-parameter-exploration.md`
- `docs/user/cli-reference.md`
- `docs/reference/evaluator-contract.md`

### Plan 03: Structured Verification V2 Implementation Planning

Status:

- complete

Purpose:

- convert the selected V2 `evaluations` / `subject` / `criteria` input model and combined `result` model into an explicit implementation plan grounded in the current codebase

Plan:

- `docs/zzz-archive/1-plan/plans/03-structured-verification-v2-implementation-planning.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/03-structured-verification-v2-implementation-planning.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-structured-verification-input-proposal.md`
- `docs/product/v2-structured-verification-result-proposal.md`
- `src/nape_evaluator/domain/use_cases.py`
- `src/nape_evaluator/application/io/cli.py`
- `src/nape_evaluator/application/io/output_contract.py`

### Plan 04: V2 Authoring Progression Deepening

Status:

- complete

Purpose:

- turn the current V2 authoring progression into a more tutorial-style, beginner-to-expert teaching path without freezing every later section up front

Plan:

- `docs/zzz-archive/1-plan/plans/04-v2-authoring-progression-deepening.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/04-v2-authoring-progression-deepening.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/user/test-of-detail-authoring.md`
- `docs/user/v2-test-authoring/README.md`
- `docs/user/v2-test-authoring/authoring-progression.md`
- `docs/user/v2-test-authoring/authoring-examples-index.md`
- `docs/user/v2-test-authoring/evaluation-input-patterns.md`
- `tests/json/test_of_detail/`

### Plan 05: Document Archive Policy

Status:

- complete

Purpose:

- define how old evaluator docs are archived and establish a durable mirrored archive structure under `docs/zzz-archive/`

Plan:

- `docs/zzz-archive/1-plan/plans/05-document-archive-policy.md`

Handoff:

- `docs/zzz-archive/1-plan/handoffs/05-document-archive-policy.md`

Primary dependencies:

- `AGENTS.md`
- `docs/maintainers/document-archive-policy.md`
- `docs/zzz-archive/`

## Sequencing Notes

- Plan 01 owns the higher-level V2 input/output shape and terminology direction.
- Plan 01's current input-side direction now uses a selected `test` + `evidence` + `evaluations` request shape with `subject` / `criteria` evaluation items, bounded subject typing, strict pre-test validation, and a dedicated invariants/examples section.
- Plan 01's paired result direction now echoes outer caller-owned `evaluations` and uses one combined test-owned `result` with `conclusion`, `facts`, and `reason`.
- Plan 01's downstream user/reference/test-authoring and maintainer/internal docs now carry labeled V2 direction notes alongside current-implementation material.
- Plan 01's proposal-shaping work is complete; implementation planning now continues in Plan 03.
- Plan 02 stayed aligned with Plan 01 while the V2 CLI/request transport cutover was selected and implemented.
- Plan 02 is now complete: the selected CLI/request transport uses repeated `--invoke` and `--invoke-file` invocation packets, `--request-file` for one full outer JSON request packet from a file path or from stdin via `-`, stays packet-based only rather than adding micro-flags, and no longer treats the older positional `--test` / `--test-parameters-file` transport as the active direction.
- Plan 03 is now complete: the V2 runtime cutover is implemented in code, the builder-only request seam, packet-based CLI transport, structured V2 result envelope, `true` / `false` / `inconclusive` result counting, permanent-doc alignment, and the last meaningful request-validation gap found during closure review, duplicate `subject.name` within one invocation, are all closed and covered by tests.
- Plan 07 is now complete: the software-integration guide set under `docs/user/software-integration/` is landed, routed from current user docs, aligned with the current CLI request/output contract, and closure-reviewed for contract-valid examples, response interpretation, and wrapper-side retention/hardening guidance.
- Plan 04 owns the next authoring-doc refinement layer: teaching sequence, stage order, and progressive deepening of the V2 authoring progression should be planned and delivered incrementally rather than locked down as one large up-front rewrite.
- Plan 04's first milestone is now landed: the progression backbone has been reordered and reframed around the selected beginner-to-expert teaching path, the early and later stages have been deepened, visible grouped parts are now present, the main progression now teaches Python-writing order explicitly through `Stage 6`, the advanced synthesis page has now been added, and it now includes worked examples including a canonical derived-fact pattern.
- Plan 04's next refinement pass has now also landed: entry-point routing across the V2 authoring guide set has been tightened, the README and overview now route readers by need as well as by reading order, and the progression's early stage Python examples no longer regress from fact-aware results back to bare `facts: []` success paths.
- Plan 04 is now complete: the selected closure decision is that the current advanced worked-example set is sufficient, and no additional canonical conditional-policy example should be added because this guide set should stay centered on verification of facts and evidence-backed test-of-detail conclusions rather than broader policy branching.
- Plan 05 is now complete: evaluator docs now have a durable archive policy, `AGENTS.md` now points archive behavior at `docs/zzz-archive/`, the archive tree mirrors the main `docs/` structure, and archived Markdown files now use one required standard historical header.
- Plan 06 is now complete: it owned the evaluator-level `summary` and `messages` clarification and implementation pass, including purpose, ownership boundaries, multi-test examples, distinct-event counting, and the `inconclusive`-only result conclusion model.
- Plan 06's implementation is now landed: permanent docs and examples now explain the ownership split between evaluator messages and test reasoning, shared evidence-side notices are represented once as request-scoped distinct events with `affected_tests`, blocked invocations return evaluator-synthesized structured `inconclusive` results, invalid completed-test contracts are normalized to completed `inconclusive` results, and evaluator messages include `stack_trace` when traceback detail exists.
- Plan 06's focused and broader regression coverage is now also landed: use-case, output-contract, CLI-contract, request-builder, and pattern-library tests all reflect the selected summary/message semantics and the executable sample test-of-detail fixtures now align with the documented `inconclusive` contract.
- All active plans should preserve the current evaluator fundamentals unless a product decision explicitly changes them.

## Operating Rule

If a new evaluator-specific workstream appears:

1. add it here first
2. create its plan doc
3. create its handoff doc
4. update `AGENTS.md` only if the start order or operating rules change
