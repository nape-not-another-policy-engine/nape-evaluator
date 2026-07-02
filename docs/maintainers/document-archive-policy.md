# Document Archive Policy

This policy defines how old evaluator documents are archived.

## Archive Root

Use:

- `docs/zzz-archive/`

The archive root is intentionally named with a trailing-sort prefix so it stays visually separate from current documentation while remaining shell-safe and ASCII-only.

## Mirrored Structure

The archive tree mirrors the main `docs/` structure.

Examples:

- `docs/product/old-proposal.md` moves to `docs/zzz-archive/product/old-proposal.md`
- `docs/reference/old-contract.md` moves to `docs/zzz-archive/reference/old-contract.md`
- `docs/1-plan/plans/old-plan.md` moves to `docs/zzz-archive/1-plan/plans/old-plan.md`
- `docs/user/v2-test-authoring/old-guide.md` moves to `docs/zzz-archive/user/v2-test-authoring/old-guide.md`

## Archive Rule

Archive a document when all of the following are true:

- it no longer describes the selected current evaluator behavior or current recommended direction
- its durable conclusions have already been moved into current docs, code comments, or current product/reference/user docs where appropriate
- keeping it in the live docs tree would create confusion about what is current

Do not archive a document only because it is old.

If it is still the current source of truth, keep it in the live docs tree.

## Supersede Vs. Archive

Use a superseded note in place when:

- the document still has active inbound references that should be cleaned up first
- the document still has short-term traceability value at its current path

Move the document into `docs/zzz-archive/` when:

- it is no longer part of current reading paths
- current references have been updated or intentionally removed
- archive placement is clearer than leaving a superseded document in the live tree

## Movement Rules

When archiving a document:

1. move it into the mirrored location under `docs/zzz-archive/`
2. keep the original filename unless a collision requires a dated or clarified name
3. update any live docs that still point at the old location
4. add the standard historical header at the top of the archived Markdown file

## Standard Archived Markdown Header

Every archived Markdown document should start with this exact header block:

```md
> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.
```

Use the same header across archived Markdown files so historical status is obvious and consistent.

Prefer moving over copying so there is not more than one pseudo-authoritative version in the repo.

## Planning Documents

For planning documents specifically:

- do not archive a completed plan or handoff until its durable conclusions have been disseminated
- use `docs/zzz-archive/1-plan/` when a planning document is no longer needed in the live planning tree
- keep the roadmap accurate before archiving related planning files

## Current Structure Baseline

The archive tree should mirror at least these live paths:

- `docs/1-plan/`
- `docs/examples/`
- `docs/maintainers/`
- `docs/product/`
- `docs/reference/`
- `docs/user/`

Add deeper mirrored subdirectories when the live docs tree gains them.
