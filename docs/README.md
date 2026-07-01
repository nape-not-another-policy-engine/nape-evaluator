# NAPE Evaluator Documentation

This folder documents the `nape-eval` CLI, its contract with the NAPE CLI, the current typed-evidence behavior, and the historical V1 baseline.

## Start Here

- New users: read [installation](user/installation.md), then [quickstart](user/quickstart.md).
- Test-of-detail authors: read [test-of-detail authoring](user/test-of-detail-authoring.md).
- CLI users: read [CLI reference](user/cli-reference.md).
- Contract readers: read [evaluator contract](reference/evaluator-contract.md), [evidence formats](reference/evidence-formats.md), and [source traceability](reference/source-traceability.md).
- Maintainers: read [architecture](maintainers/architecture.md), [local development](maintainers/local-development.md), [Python engineering standards](maintainers/python-engineering-standards.md), then [software review](maintainers/software-review.md).
- Planning and handoff readers: start with [roadmap](1-plan/roadmap.md).
- Historical and migration readers: read [V1 evaluator baseline](product/v1-evaluator-baseline.md).
- Example readers: inspect [examples](examples/README.md).

## Current Documentation Position

These docs treat committed `main` behavior as the current typed-evidence contract. The V1 baseline document is retained as a historical reference for migration and compatibility review.

## Folder Guide

`product/`

Product-level purpose, current scope, historical V1 baseline, and known limitations.

`user/`

Task-oriented installation, quickstart, CLI, and test authoring docs.

`reference/`

Detailed input/output contracts, evidence format behavior, and source traceability.

`maintainers/`

Implementation flow, local development, packaging, release notes, and validation guidance.

`examples/`

Small example fixtures and expected output shapes for docs and smoke validation planning.

`1-plan/`

Evaluator-specific roadmap, plan, and handoff material.

## Planning Rule

Keep evaluator planning and handoff documents under `docs/1-plan/`.
Do not create new `TEMP-` planning files at the root of `docs/`.
