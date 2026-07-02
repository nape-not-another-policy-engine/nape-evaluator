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

- complete

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

- decide and document how caller-supplied evaluation input should be transported and bound to requested test executions

Plan:

- `docs/1-plan/plans/02-expectation-binding-and-cli-transport.md`

Handoff:

- `docs/1-plan/handoffs/02-expectation-binding-and-cli-transport.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/test-parameter-exploration.md`
- `docs/user/cli-reference.md`
- `docs/reference/evaluator-contract.md`

### Plan 03: Structured Verification V2 Implementation Planning

Status:

- active

Purpose:

- convert the selected V2 `evaluations` / `subject` / `criteria` input model and combined `result` model into an explicit implementation plan grounded in the current codebase

Plan:

- `docs/1-plan/plans/03-structured-verification-v2-implementation-planning.md`

Handoff:

- `docs/1-plan/handoffs/03-structured-verification-v2-implementation-planning.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-structured-verification-input-proposal.md`
- `docs/product/v2-structured-verification-result-proposal.md`
- `src/nape_evaluator/domain/use_cases.py`
- `src/nape_evaluator/application/io/cli.py`
- `src/nape_evaluator/application/io/output_contract.py`

### Plan 04: V2 Authoring Progression Deepening

Status:

- active

Purpose:

- turn the current V2 authoring progression into a more tutorial-style, beginner-to-expert teaching path without freezing every later section up front

Plan:

- `docs/1-plan/plans/04-v2-authoring-progression-deepening.md`

Handoff:

- `docs/1-plan/handoffs/04-v2-authoring-progression-deepening.md`

Primary dependencies:

- `docs/product/current-evaluator-reference.md`
- `docs/user/test-of-detail-authoring.md`
- `docs/user/v2-test-authoring/README.md`
- `docs/user/v2-test-authoring/authoring-progression.md`
- `docs/user/v2-test-authoring/authoring-examples-index.md`
- `docs/user/v2-test-authoring/evaluation-input-patterns.md`
- `tests/json/test_of_detail/`

## Sequencing Notes

- Plan 01 owns the higher-level V2 input/output shape and terminology direction.
- Plan 01's current input-side direction now uses a selected `test` + `evidence` + `evaluations` request shape with `subject` / `criteria` evaluation items, bounded subject typing, strict pre-test validation, and a dedicated invariants/examples section.
- Plan 01's paired result direction now echoes outer caller-owned `evaluations` and uses one combined test-owned `result` with `conclusion`, `facts`, and `reason`.
- Plan 01's downstream user/reference/test-authoring and maintainer/internal docs now carry labeled V2 direction notes alongside current-implementation material.
- Plan 01's proposal-shaping work is complete; implementation planning now continues in Plan 03.
- Plan 02 must stay aligned with Plan 01, especially where current `test_parameters` language may later become V2 `evaluations` / `criteria` language.
- Plan 02's selected direct V2 CLI direction now uses repeated `--invoke` and `--invoke-file` invocation packets, each carrying both `test` and `evaluations`, adds `--request-file` for one full outer JSON request packet from a file path or from stdin via `-`, and stays packet-based only rather than adding micro-flags.
- Plan 03's first implementation cut is now in code: builder-only request seam, packet-based CLI transport, structured V2 result envelope, and `true` / `false` / `inconclusive` / `error` summary counting are implemented and covered by passing tests.
- Plan 03's permanent doc alignment is now substantially complete across README, user, reference, maintainer, and product-current docs; next follow-up work should focus on any remaining implementation-grade refinements or residual legacy-field cleanup rather than re-explaining the V2 cutover.
- Plan 04 owns the next authoring-doc refinement layer: teaching sequence, stage order, and progressive deepening of the V2 authoring progression should be planned and delivered incrementally rather than locked down as one large up-front rewrite.
- Plan 04's first milestone is now landed: the progression backbone has been reordered and reframed around the selected beginner-to-expert teaching path, the early and later stages have been deepened, visible grouped parts are now present, the main progression now teaches Python-writing order explicitly through `Stage 6`, the advanced synthesis page has now been added, and it now includes worked examples including a canonical derived-fact pattern; the next question is whether any further example or navigation cleanup is still justified.
- All active plans should preserve the current evaluator fundamentals unless a product decision explicitly changes them.

## Operating Rule

If a new evaluator-specific workstream appears:

1. add it here first
2. create its plan doc
3. create its handoff doc
4. update `AGENTS.md` only if the start order or operating rules change
