> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 08: V1 Historical Support And Migration

## Completion Outcome

This plan is now complete.

Selected closure decision:

- keep one bounded historical V1 baseline in the live product docs
- add a user-facing V1-to-V2 migration guide for both test authors and wrapper authors
- keep current-state product truth in:
  - `docs/product/current-evaluator-reference.md`
  - `docs/product/nape-evaluator-product-spec.md`
  - `docs/product/v2-policy-direction.md`
- archive exploratory and proposal-era product docs that no longer belong in the live product reading path

Closure verification:

- current user entry points route to the migration guide
- historical V1 material now points readers toward the migration guide when practical cutover guidance is needed
- archived product docs now carry the standard historical header
- live and archived references were cleaned so current docs no longer point at superseded live product paths

## Goal

Decide and implement the minimum durable documentation needed now that the evaluator is fully committed to the V2 runtime contract and is not backward compatible with V1.

This workstream should answer three practical questions:

1. what V1 material should remain available for historical users
2. what migration guidance current users need in order to move from V1 to V2
3. which old product-thinking documents should remain live versus move into `docs/zzz-archive/`

## Why This Is Its Own Plan

The current evaluator contract is now clearly V2-only in code and in most current docs.

That is the correct current-state posture, but it leaves two follow-on documentation needs:

- historical users still need one bounded place to understand the old V1 contract
- maintainers need a disciplined way to separate:
  - current product/runtime truth
  - historical compatibility reference
  - exploratory product-thinking documents that no longer belong in the live product tree

If this is not handled explicitly, the doc set can become noisy in two directions at once:

- too little migration help for users coming from V1
- too many live product documents that are no longer part of the current product reading path

## Baseline

Read first:

1. `docs/1-plan/roadmap.md`
2. `docs/product/current-evaluator-reference.md`
3. `docs/product/nape-evaluator-product-spec.md`
4. `docs/product/v1-evaluator-baseline.md`
5. `docs/reference/evaluator-contract.md`
6. `docs/user/README.md`
7. `docs/maintainers/document-archive-policy.md`

## Selected Starting Direction

The starting direction for this plan is:

- keep one bounded V1 historical reference document
- add a dedicated V1-to-V2 migration guide for users
- keep current runtime/product truth in the current V2 docs
- review live product docs and recommend which ones should remain live versus move to `docs/zzz-archive/product/`

## Phase 1: Migration Guide

Phase 1 should produce a practical migration guide at:

- `docs/user/v1-to-v2-migration.md`

That guide should be task-oriented rather than purely conceptual.

It should cover at least:

1. CLI transport migration
   - `--test` to `--invoke`, `--invoke-file`, and `--request-file`
2. test function signature migration
   - `evaluate(evidence)` to `evaluate(evidence, evaluations, metadata)`
3. evidence contract migration
   - raw text lines to typed evidence loading
4. result contract migration
   - tuple/pass-fail-error style to structured `conclusion`, `facts`, `reason`
5. operational interpretation migration
   - V1 `error` versus V2 blocked rows, evaluator messages, and completed `inconclusive`
6. before/after examples
7. migration checklists
   - test author checklist
   - wrapper/integration checklist

## Product-Doc Archive Recommendations

Current recommendation set:

### Keep Live

- `docs/product/nape-evaluator-product-spec.md`
- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-policy-direction.md`
- `docs/product/v1-evaluator-baseline.md`

Rationale:

- these documents still serve distinct current roles:
  - product scope and current direction
  - current committed runtime behavior
  - selected V2 policy stance
  - bounded historical V1 baseline for migration and compatibility review

### Archive Now

- `docs/zzz-archive/product/test-parameter-exploration.md`

Rationale:

- it is already labeled as superseded historical exploration
- it does not describe the selected or current runtime contract
- its role is traceability, not live product direction
- archive placement would now be clearer than leaving it in the live product folder

### Review For Possible Later Archive

- `docs/zzz-archive/product/v2-structured-verification-input-proposal.md`
- `docs/zzz-archive/product/v2-structured-verification-result-proposal.md`

Current recommendation:

- archive these after the migration guide and initial product-doc cleanup are sufficient

Rationale:

- they are no longer the runtime contract
- their main remaining value is historical design rationale and selected-shape traceability
- that value is still preserved after archive placement
- live product docs should now be current-state-first:
  - `nape-evaluator-product-spec.md`
  - `current-evaluator-reference.md`
  - `v2-policy-direction.md`
  - user/reference docs

## Initial Execution Order

1. create the migration guide
2. route readers to it from current user entry points
3. tighten V1 historical references so they point at the migration guide where useful
4. record the product-doc archive recommendations in permanent planning state
5. then decide whether to execute archive moves for product docs in this same plan or as a second phase

## Current Status

Active.

Phase 1 is partially landed:

- the first migration guide is now authored and routed from current docs
- the exploratory product document `test-parameter-exploration.md` is now archived under `docs/zzz-archive/product/`
- the migration guide now includes a bounded second pass for wrapper-oriented migration:
  - old versus new subprocess flow
  - old versus new stdout shape
  - a first-pass wrapper response-classification example
- the large V2 input/result proposal docs are now archived under `docs/zzz-archive/product/`

Plan 08 is closed and archived.

## Closure Review Findings And Recommended Fixes

The current closure review found two remaining documentation-alignment issues.

These are recorded here as recommended fixes pending approval.

### 1. Historical V1 baseline still leaves one migration item marked open

Finding:

- `docs/product/v1-evaluator-baseline.md` still says the evidence-input-shape migration row is an open follow-up
- that row currently recommends:
  - preserve a raw text-lines mode, or
  - provide explicit migration guidance
- Plan 08 has now selected and delivered the migration-guidance path through:
  - `docs/user/v1-to-v2-migration.md`

Recommendation:

- update the affected row in `v1-evaluator-baseline.md` so it no longer reads as open
- keep the historical contrast, but change the recommendation/status to reflect the selected direction:
  - typed evidence loading remains the V2 contract
  - explicit migration guidance is the selected compatibility response
  - status should reflect that the migration-guidance path is now documented

Rationale:

- the baseline should remain historical, but it should not imply an unresolved product decision that has already been settled
- keeping the row open would make the historical matrix conflict with the actual delivered migration docs
- this is a documentation-alignment fix, not a product-direction change

Tradeoff:

- the matrix becomes less “open-question historical”
- but more accurate historical traceability is better now that the decision is settled

### 2. Product spec still overstates completed-row `result.reason` ownership

Finding:

- `docs/product/nape-evaluator-product-spec.md` still says:
  - `results[*].result.reason` is test-owned when the test completed
- that is too absolute for the current runtime
- invalid completed result contracts are normalized into completed `inconclusive` rows with evaluator-authored explanatory `reason`

Recommendation:

- align the product spec wording with the already-corrected runtime/reference guidance
- recommended wording direction:
  - completed rows usually carry test-owned reasoning
  - blocked rows carry evaluator-owned blocked reasoning
  - completed rows normalized from invalid completed test result contracts carry evaluator-authored explanatory reasoning

Rationale:

- the product spec should not drift from the committed runtime reference on a contract nuance that affects downstream interpretation
- this exact ownership nuance has already been corrected in other docs and should now be consistent in the product spec too
- wrappers and maintainers should not have to reconcile conflicting ownership statements across current docs

Tradeoff:

- the wording becomes slightly more detailed
- but it avoids a real interpretation mistake and keeps the current product truth coherent
