> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 05: Document Archive Policy

## Completion Outcome

This plan is now complete.

Selected closure decision:

- evaluator docs use a dedicated archive root at `docs/zzz-archive/`
- the archive tree mirrors the main `docs/` structure
- archiving is governed by one durable maintainer policy rather than ad hoc moves
- archived Markdown files use one standard historical header
- `AGENTS.md` now points future archive behavior at that policy and location

Closure rationale:

- completed workstreams created a need for a predictable place for old planning and documentation artifacts
- a mirrored archive tree reduces ambiguity about where archived files belong
- a documented policy prevents inconsistent future archive handling

## Goal

Define how old evaluator documents should be archived and create a durable archive structure that mirrors the main `docs/` tree.

## Scope

In scope:

- archive location
- archive movement rules
- mirrored directory structure
- standard archived Markdown header
- operating-rule updates in repo instructions

Out of scope:

- bulk-moving existing superseded docs in this workstream
- changing the meaning of current product/reference/user docs

## Durable Outputs

- `docs/maintainers/document-archive-policy.md`
- `docs/zzz-archive/` mirrored directory skeleton
- `AGENTS.md` archive-rule update
