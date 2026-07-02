# AGENTS.md

This file is the entry point for agent work inside `nape-evaluator`.

## Start Here

When resuming evaluator work:

1. read [docs/1-plan/roadmap.md](docs/1-plan/roadmap.md)
2. open the active plan under `docs/1-plan/plans/`
3. open the matching handoff under `docs/1-plan/handoffs/`
4. ground all proposal or implementation work against [docs/product/current-evaluator-reference.md](docs/product/current-evaluator-reference.md)

## Planning Rules

- keep evaluator-specific planning documents under `docs/1-plan/`
- do not create new `TEMP-` planning files at the root of `docs/`
- treat `docs/1-plan/roadmap.md` as the status index for active evaluator workstreams
- each active workstream should have:
  - one plan document in `docs/1-plan/plans/`
  - one handoff document in `docs/1-plan/handoffs/`
- when a workstream changes materially, update the roadmap and the relevant handoff before stopping

## Archive Rules

- use `docs/zzz-archive/` as the dedicated archive root for evaluator docs
- mirror the live `docs/` structure under `docs/zzz-archive/` when archiving files
- follow `docs/maintainers/document-archive-policy.md` for archive-versus-supersede decisions and movement rules

## Baseline Rules

- the evaluator is claim-agnostic unless product docs explicitly change that
- current evaluator behavior is documented in `docs/product/current-evaluator-reference.md`
- V2 input/output work is an expansion of the current evaluator model, not a clean-sheet redesign, unless a product decision explicitly says otherwise
- keep the distinction between evaluator-owned execution concerns and test-owned evaluation logic explicit in docs and code

## Working Order

Use this order when making evaluator changes:

1. roadmap
2. active plan
3. active handoff
4. current evaluator reference
5. product/reference/user docs
6. code and tests

## Completion Rule

When a plan is completed:

- move durable conclusions into permanent docs or code comments where appropriate
- update the roadmap status
- delete or archive planning docs only after their information has been disseminated
- if planning docs are archived, move them under the mirrored path in `docs/zzz-archive/1-plan/`
