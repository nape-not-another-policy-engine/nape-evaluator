> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 05: Document Archive Policy

## Purpose

Record the completed state and closure decision for evaluator document archiving governance.

## Current State

- evaluator docs now use `docs/zzz-archive/` as the dedicated archive root
- the archive tree mirrors the main `docs/` structure
- archive behavior is now documented in a durable maintainer policy
- archived Markdown files now have one required standard historical header
- `AGENTS.md` now routes future archive decisions to that policy and location

## Closure Decision

This workstream is complete.

Do not continue it by default.

If future archive needs arise, use the documented archive policy rather than creating a new workstream unless the policy itself must change materially.

## Durable Outputs

- `docs/maintainers/document-archive-policy.md`
- `docs/zzz-archive/`
- `AGENTS.md`
