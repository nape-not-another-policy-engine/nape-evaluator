> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 08: V1 Historical Support And Migration

## Purpose

Resume the V1 historical-support and migration workstream without re-deriving why it exists.

## Status

This workstream is complete.

The migration and product-doc cleanup work described here is already landed.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/08-v1-historical-support-and-migration.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/nape-evaluator-product-spec.md`
5. `docs/product/v1-evaluator-baseline.md`
6. `docs/reference/evaluator-contract.md`
7. `docs/maintainers/document-archive-policy.md`

## Selected Direction

- current docs should stay V2-first and current-runtime-first
- V1 should remain available through one bounded historical baseline plus a migration guide
- the migration guide belongs in `docs/user/`, not `docs/product/`
- archive recommendations for old product-thinking docs should be recorded explicitly before moves are made

## Product-Doc Archive Recommendation Snapshot

Keep live:

- `docs/product/nape-evaluator-product-spec.md`
- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-policy-direction.md`
- `docs/product/v1-evaluator-baseline.md`

Archive now:

- `docs/zzz-archive/product/test-parameter-exploration.md`

Archived later in this workstream:

- `docs/zzz-archive/product/v2-structured-verification-input-proposal.md`
- `docs/zzz-archive/product/v2-structured-verification-result-proposal.md`

## Immediate Outputs

1. `docs/user/v1-to-v2-migration.md`
2. routing updates from current user entry points
3. any small reference wording adjustments needed so V1 material clearly points to the migration guide

## Updated Status

The first migration guide and reader routing are now landed.

The selected “archive now” product-doc move is also now executed:

- `docs/zzz-archive/product/test-parameter-exploration.md`

The migration guide now also includes a bounded wrapper-oriented second pass:

- old versus new subprocess invocation flow
- old versus new stdout/result interpretation shape
- a first-pass wrapper classification example

The large V2 input/result proposal docs are now also archived under `docs/zzz-archive/product/`.

Plan 08 is closed and archived.

## Latest Closure Review Recommendations

The latest closure review found two remaining recommended fixes:

1. update `docs/product/v1-evaluator-baseline.md`
   - selected recommendation:
     - close the evidence-input-shape matrix row so it reflects the selected migration-guidance path rather than leaving the decision open
2. update `docs/product/nape-evaluator-product-spec.md`
   - selected recommendation:
     - stop saying every completed-row `result.reason` is test-owned
     - say completed rows usually carry test-owned reasoning, except for evaluator normalization of invalid completed result contracts

Why these are the recommended direction:

- they align the remaining current/historical docs with decisions that are already settled elsewhere in the doc set
- they do not introduce new product direction
- they are the last identified blockers before Plan 08 can close cleanly
