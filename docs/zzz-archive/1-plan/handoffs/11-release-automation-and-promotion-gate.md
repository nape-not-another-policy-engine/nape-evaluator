> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 11: Release Automation And Promotion Gate

## Purpose

Resume the release-gate and promotion workstream without re-deriving the current release position.

## Status

This workstream is complete.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/11-release-automation-and-promotion-gate.md`
3. `docs/zzz-archive/1-plan/plans/10-clean-install-and-release-validation.md`
4. `docs/maintainers/release-validation.md`
5. `.github/workflows/release-trigger.yaml`
6. `Makefile`
7. `pyproject.toml`
8. `docs/user/installation.md`
9. `https://docs.napecentral.com/install-nape-from-nape-binary-repo.html#official-nape-binary-repo`

## Current Findings

- the evaluator already has a tag-triggered release workflow in `.github/workflows/release-trigger.yaml`
- that workflow delegates to a shared reusable GitHub Actions workflow
- the local repository still exposes PyPI-oriented maintainer commands rather than an end-to-end release gate
- the current official NAPE binary-repo install doc says only `nape-cli` is available there and that `nape-evaluator` still requires `pip install nape`
- that page currently shows `Last modified: 23 September 2024`

## Selected Starting Direction

- keep tag-triggered releases as the production promotion mechanism
- use the Plan 10 validation matrix as the starting release gate
- keep the evaluator’s current supported release target as PyPI until the official binary-repo artifact target and publication model are explicitly selected

## Immediate Outputs

1. explicit release-gate recommendation
2. publication-target recommendation
3. documentation and automation updates for the selected release path

## Implemented So Far

- `docs/maintainers/release-process.md` now records the current tag-triggered release model
- `Makefile` now exposes standardized release-validation commands
- `scripts/release_validation_clean_install.sh` now provides the clean-install helper path
- the current recommended release gate is `make release-validate`
- `.github/workflows/release-trigger.yaml` now reruns that same gate in automation before the reusable publish workflow runs

## Publication Decision

The evaluator publication target is now selected:

- keep the evaluator’s supported publication target as PyPI
- do not treat official binary-repo publication as part of the current evaluator release contract
- if NAPE later wants an official repository target for the evaluator, design that as a Python-package repository or PyPI-compatible index rather than trying to force the evaluator into the current native-binary download scheme
