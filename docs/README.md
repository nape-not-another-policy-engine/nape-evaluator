# NAPE Evaluator Documentation

This folder documents the `nape-eval` CLI, its contract with the NAPE CLI, and the current V1 baseline for V2 evaluator planning.

## Start Here

- New users: read [installation](user/installation.md), then [quickstart](user/quickstart.md).
- Test-of-detail authors: read [test-of-detail authoring](user/test-of-detail-authoring.md).
- CLI users: read [CLI reference](user/cli-reference.md).
- Contract readers: read [evaluator contract](reference/evaluator-contract.md), [evidence formats](reference/evidence-formats.md), and [source traceability](reference/source-traceability.md).
- Maintainers: read [architecture](maintainers/architecture.md), then [local development](maintainers/local-development.md).
- V2 planners: read [V1 evaluator baseline](product/v1-evaluator-baseline.md).
- Example readers: inspect [examples](examples/README.md).

## Current Documentation Position

These docs treat committed `main` behavior as the V1 baseline. Current uncommitted typed-evidence changes are documented as V2 candidate behavior only.

## Folder Guide

`product/`

Product-level purpose, scope, V1 baseline, V2 planning inputs, and known limitations.

`user/`

Task-oriented installation, quickstart, CLI, and test authoring docs.

`reference/`

Detailed input/output contracts, evidence format behavior, and source traceability.

`maintainers/`

Implementation flow, local development, packaging, release notes, and validation guidance.

`examples/`

Small example fixtures and expected output shapes for docs and smoke validation planning.

## Temporary Planning Documents

Temporary planning or review documents may appear in this folder with a `TEMP-` prefix. Delete them after their findings are resolved or moved into permanent docs/issues.
