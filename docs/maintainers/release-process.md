# Release Process

This document defines the current evaluator release-promotion policy above the lower-level validation steps documented in [release-validation.md](release-validation.md).

## Purpose

Use this document when deciding:

- what must pass before a release tag is created
- what the release tag is expected to trigger
- which publication targets are currently supported for the evaluator

## Current Release Trigger

The repository currently contains one release-trigger workflow:

- [release-trigger.yaml](../../.github/workflows/release-trigger.yaml)

Current trigger modes:

- `workflow_dispatch`
- `push` for tags matching `v*.*.*`

Current implementation note:

- the workflow delegates to the shared reusable workflow `pypi-standard-release-workflow.yaml`
- before delegation, this repository now runs its own explicit `validate` job

Inference:

- based on the reusable workflow name and the local repository’s maintainer commands, the current standardized publication target is PyPI-oriented

That inference matches the current local maintainer command surface:

- `make build-release`
- `make pypi-publish`

Current enforced automation gate:

- the release-trigger workflow now runs `make release-validate` in GitHub Actions before the reusable publish workflow is allowed to run

## Current Supported Evaluator Publication Target

The current supported evaluator publication target is:

- PyPI

This is the current documented truth in this repository:

- [README.md](../../README.md) installs the evaluator with `python3 -m pip install nape`
- [installation.md](../user/installation.md) also installs the evaluator with `python3 -m pip install nape`

## Official NAPE Binary Repository Constraint

The official install documentation page currently states that only `nape-cli` is available from the official NAPE binary repository and that `nape-evaluator` still requires `pip install nape`.

Source:

- https://docs.napecentral.com/install-nape-from-nape-binary-repo.html#official-nape-binary-repo

Important date note:

- that page currently says it was last modified on September 23, 2024

Implication:

- a release policy that assumes evaluator publication to the official NAPE binary repository would go beyond the currently documented evaluator distribution model

Treat that as a separate product and release-design decision, not as something that is already implicitly supported.

## Recommended Current Release Gate

Before creating or pushing a production release tag, run:

```bash
make release-validate
```

That command currently standardizes:

- `python3 -m unittest discover`
- `make docs-smoke`
- repository-runtime release validation
- fresh-virtual-environment clean-install release validation

The same gate is now enforced in the tag-triggered GitHub Actions release workflow before publish.

## Recommended Promotion Flow

Current recommended production flow:

1. ensure the working tree is in the intended release state
2. run `make release-validate`
3. create a semantic version tag such as `v2.0.0`
4. push the tag
5. let the tag-triggered GitHub Actions workflow rerun the release gate in automation
6. if that automation gate passes, let the reusable publish workflow perform the release promotion

## `workflow_dispatch` Recommendation

Keep `workflow_dispatch` available only for controlled maintainer use.

Recommended usage:

- rerunning a release workflow when a tag-based run needs controlled recovery
- intentional manual release testing in a non-production target if the shared workflow supports it

Do not treat `workflow_dispatch` as the normal production promotion path if tagged releases are the intended control mechanism.

## Selected Publication Target

The selected supported evaluator publication target is:

- PyPI only

This is the current chosen production position.

Do not treat official NAPE binary-repository publication as part of the evaluator release contract at this time.

## Publication Target Decision Space

The evaluator is not the same kind of artifact as `nape-cli`.

`nape-cli` is currently documented as a downloadable executable from the official NAPE binary repository.

`nape-evaluator` is currently documented as a Python package installed with `pip install nape`.

That means “publish the evaluator to the official repo” can mean several different things.

### Option 1: Keep Evaluator Publication PyPI-Only

Shape:

- keep publishing `nape` to PyPI
- keep the official binary-repo docs unchanged for the evaluator

Pros:

- matches the current documented install path
- matches the current shared release workflow naming and local maintainer commands
- avoids inventing a second Python package distribution surface immediately

Cons:

- the evaluator does not become an official NAPE binary-repo install target
- organizations that prefer one official NAPE-controlled distribution surface still depend on PyPI for the evaluator

Recommendation:

- this is the safest current production position until a real evaluator artifact model is selected

### Option 2: Publish Evaluator Release Assets, But Keep PyPI As The Install Source Of Truth

Shape:

- continue publishing to PyPI
- also attach wheel and sdist artifacts to GitHub releases or another maintainer-facing artifact surface
- do not yet claim official binary-repo support for evaluator installation

Pros:

- gives maintainers additional artifact visibility and recovery options
- improves traceability of what exact wheel/sdist was released for a given tag

Cons:

- does not solve the “official repo” distribution ask by itself
- creates another artifact surface without changing the actual public install method

Recommendation:

- useful as a supporting improvement, but not a replacement for an explicit official-repo distribution model

### Option 3: Publish Evaluator As A Python Package Through An Official NAPE-Controlled Python Index

Shape:

- continue producing the `nape` wheel and sdist
- publish them to a PyPI-compatible package index controlled by NAPE
- document installation through `pip` against that index or a proxy/mirror of PyPI

Examples of the install experience this would enable:

- `pip install --index-url <nape-python-index> nape`
- or `pip install --extra-index-url <nape-python-index> nape`

Pros:

- fits the evaluator’s real artifact model as a Python package
- supports dependency resolution in the way `pip` expects
- gives NAPE an official controlled distribution surface without pretending the evaluator is a native single-file binary

Cons:

- requires an actual Python-package repository model, not just the current binary-download path scheme
- requires explicit decisions about dependency sourcing:
  - mirror/proxy PyPI
  - curate dependencies internally
  - or allow mixed public/private index resolution
- requires public-doc updates and probably shared-workflow updates

Recommendation:

- if NAPE wants an official repository story for the evaluator, this is the strongest long-term model

### Option 4: Force Evaluator Into The Existing Binary-Download Path Scheme

Shape:

- publish some evaluator-specific downloadable artifact under the current binary-repo path format used for native binaries

Possible examples:

- a raw wheel file under a binary path
- a zip bundle containing a wheel and install wrapper
- a platform-specific packaged environment

Pros:

- keeps everything under one existing repo hostname and path family

Cons:

- this is not a natural fit for a Python package that is currently installed through `pip`
- a raw wheel URL alone does not solve dependency-distribution policy cleanly
- platform-specific bundles would add complexity far beyond the current evaluator packaging model
- this risks creating a confusing “binary repo” story for something that is not really a native binary product

Recommendation:

- do not do this unless product explicitly wants to redesign evaluator distribution around packaged environments rather than normal Python package installation

## Selected Direction

Selected decision:

1. keep the evaluator’s supported production publication target as PyPI
2. if an official NAPE-controlled repository is required later, implement it as a Python-package repository or PyPI-compatible index, not as a fake native-binary download
3. do not update public docs to claim official binary-repo evaluator support unless that Python-package distribution model actually exists

Why this is the selected direction:

- it matches the current documented truth
- it fits the evaluator’s actual artifact type
- it avoids a misleading “binary repo” abstraction for a Python package with Python dependency resolution needs

## Deferred Follow-Up

If the evaluator must later publish through an official NAPE-controlled repository, the follow-up design questions are:

1. what Python-package repository model will be used
2. whether the shared release workflow supports that target
3. how public install docs should change once that target exists
