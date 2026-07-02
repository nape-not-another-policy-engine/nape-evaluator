> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 11: Release Automation And Promotion Gate

## Goal

Define and standardize the evaluator release gate and promotion path so:

- normal branch integration stays separate from release promotion
- a version tag triggers the real release workflow
- release validation is explicit and repeatable
- publication targets are clear, supported, and documented

## Why This Is Its Own Plan

The evaluator now has a working local and clean-install validation matrix, but release promotion is still only partially standardized.

There is already a tag-triggered GitHub Actions release trigger in this repository, but the surrounding release policy is still incomplete:

- what must pass before a tag is considered releasable
- what exactly the tag-triggered workflow is expected to publish
- whether publication targets include only PyPI or also the official NAPE binary repository
- how maintainer-local release validation connects to the actual GitHub release workflow

## Baseline

Read first:

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/10-clean-install-and-release-validation.md`
3. `docs/zzz-archive/1-plan/handoffs/10-clean-install-and-release-validation.md`
4. `docs/product/current-evaluator-reference.md`
5. `docs/product/nape-evaluator-product-spec.md`
6. `docs/maintainers/release-validation.md`
7. `docs/maintainers/local-development.md`
8. `.github/workflows/release-trigger.yaml`
9. `Makefile`
10. `pyproject.toml`
11. `docs/user/installation.md`
12. `https://docs.napecentral.com/install-nape-from-nape-binary-repo.html#official-nape-binary-repo`

## Current-State Audit

Current committed evaluator release mechanics:

- this repository has one release-trigger workflow:
  - `.github/workflows/release-trigger.yaml`
- it runs on:
  - `workflow_dispatch`
  - `push` tags matching `v*.*.*`
- it delegates to a shared reusable workflow:
  - `nape-not-another-policy-engine/nape-build-deploy-release/.github/workflows/pypi-standard-release-workflow.yaml@main`
- local maintainer commands still center on:
  - `make build-release`
  - `make pypi-publish`
- local validation now includes:
  - `python3 -m unittest discover`
  - `make docs-smoke`
  - `bash ./scripts/release_validation.sh`

Current documented distribution position:

- `docs/user/installation.md` installs the evaluator from PyPI via `pip install nape`
- the official NAPE binary-repo doc currently states that only `nape-cli` is available there
- that same doc states that `nape-evaluator` still requires `pip install nape`
- that page currently shows `Last modified: 23 September 2024`

## Important Current Constraint

As of the current official install documentation page, the evaluator is not yet documented as an official NAPE binary-repository artifact.

That means a tag-triggered release policy that assumes evaluator publication to the official binary repository would go beyond the currently documented distribution model.

This is not just an automation detail.

It is a product/distribution decision.

## Primary Questions

This plan should answer:

1. What exact checks form the evaluator release gate before a release tag is created or promoted?
2. Should release validation be enforced only in GitHub Actions, only locally before tagging, or both?
3. Is the evaluator release target currently:
   - PyPI only
   - PyPI plus GitHub release assets
   - PyPI plus the official NAPE binary repository
4. If the evaluator should publish to the official NAPE binary repository, what artifact type should that repository host for this Python package?
5. Should `workflow_dispatch` remain available for manual release runs, or should tag pushes be the only production release path?

## Starting Recommendation

First-pass recommendation:

- keep the release trigger tag-based for production promotion
- keep `workflow_dispatch` only for controlled manual release operations if maintainers still need it
- require the Plan 10 validation matrix before release promotion
- keep the evaluator’s current supported publication target as PyPI until official binary-repo publication is explicitly defined and documented

Why:

- the tag-based trigger already matches the desired release-control pattern
- the local/clean-install validation surface now exists and can become the release gate
- the official binary-repo story for the evaluator is not yet aligned with current public documentation
- the local repository and shared workflow naming both currently present a PyPI-oriented release surface

## Planned Outputs

1. documented release-gate checklist
2. documented tag-triggered release policy
3. decision and documentation for evaluator publication targets
4. `Makefile` or maintainer command updates if a stable release-validation command surface is needed
5. GitHub Actions updates if the selected gate should be enforced in automation

## Status

Complete.

## Implemented So Far

The first milestone of this plan is now landed:

- `docs/maintainers/release-process.md` defines the current release trigger and promotion policy
- `Makefile` now provides:
  - `make release-validate-local`
  - `make release-validate-clean-install`
  - `make release-validate`
- `scripts/release_validation_clean_install.sh` standardizes the fresh-virtual-environment validation path
- local maintainer docs now point at the standardized release-validation commands
- packaging byproducts are better handled through:
  - `.gitignore` coverage for `*.egg-info/`
  - `clean` removal of `src/*.egg-info`
- `.github/workflows/release-trigger.yaml` now enforces the same `make release-validate` gate in GitHub Actions before the reusable publish workflow runs

## Publication Decision Space

The practical options are:

1. keep evaluator publication PyPI-only for now
2. publish supporting wheel/sdist assets elsewhere but keep PyPI as the install source of truth
3. later add an official NAPE-controlled Python package repository or PyPI-compatible index for the evaluator
4. try to force evaluator distribution into the current native-binary repository path scheme

Selected direction:

- keep PyPI as the supported evaluator publication target
- if official-repo distribution is required later, design it as a Python package repository model rather than as a native-binary artifact model

Rationale:

- the evaluator is currently a Python package, not a standalone native binary
- the current public docs already say `pip install nape`
- a Python index or mirror model fits dependency resolution and artifact semantics much better than a raw binary-download scheme

## Selected Decision

This workstream now treats the evaluator publication target as selected:

- supported production target: PyPI
- not currently supported as part of the evaluator release contract: official NAPE binary-repository publication

The official binary-repo path remains a deferred future product/distribution decision rather than a current evaluator release requirement.

## Current Completion Position

The release-gate and publication-target work for this repository is now materially complete:

- local release validation is standardized
- clean-install validation is standardized
- tag-triggered GitHub Actions now reruns the same release gate before publish
- the evaluator publication target is selected as PyPI

Any future work beyond this plan would be an expansion, such as:

- changing the shared reusable release workflow contract
- adding GitHub release asset policy
- designing an official NAPE-controlled Python package repository
