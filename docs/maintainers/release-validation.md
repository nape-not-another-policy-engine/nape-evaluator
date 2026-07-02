# Release Validation

This document defines the pre-deployment clean-install and release-validation procedure for the current V2 evaluator contract.

Use this document when you need confidence that a fresh installation can actually execute the supported evaluator boundary, not just start the CLI entry point.

## Purpose

This procedure exists because:

- `--check-install` proves the CLI starts
- `--check-install` does not prove that typed evidence loaders and runtime dependencies are healthy
- the current evaluator contract now depends on:
  - request-packet validation
  - typed evidence loading
  - evaluator-to-test call execution
  - the V2 JSON result envelope
  - the zero-exit JSON contract for evaluator invocations

## What `--check-install` Does And Does Not Prove

`--check-install` proves:

- the console entry point is present
- the evaluator process can start

`--check-install` does not prove:

- JSON, XML, YAML, TXT, and PDF evidence paths all work
- runtime dependency-backed loaders such as YAML and PDF are healthy
- the V2 request packet contract can be executed end to end
- evaluator invocations return the expected JSON contract in a fresh install

That distinction is intentional.

Keep operator expectations narrow and explicit.

## Validation Modes

Use two modes:

### 1. Local Preflight

Run this from the repository before packaging or release promotion:

```bash
EVALUATOR_USE_MAIN_PY=1 bash ./scripts/release_validation.sh
```

Or use:

```bash
make release-validate-local
```

This validates the current repository runtime shape through `python3 main.py`.

### 2. Clean-Install Validation

Run this after installing the package into a fresh virtual environment or equivalent isolated environment:

```bash
nape-eval --check-install
bash ./scripts/release_validation.sh
```

Or use the repository helper:

```bash
make release-validate-clean-install
```

This validates the installed `nape-eval` console script rather than the repository bootstrap path.

## Validation Matrix

| Surface | Why it matters | Expected result |
| --- | --- | --- |
| `--check-install` | confirms the entry point starts | exit `0`, expected plain-text health message |
| direct `--invoke` | proves core direct-mode V2 invocation works | exit `0`, stdout JSON, completed `true` |
| `--invoke-file` | proves file-backed invocation transport works | exit `0`, stdout JSON, completed `true` |
| `--request-file` | proves full outer request transport works | exit `0`, stdout JSON, completed `true` |
| `.txt` | validates text-line loader path | exit `0`, completed `true`, metadata evidence type `text` |
| `.json` | validates JSON loader path | exit `0`, completed `true` |
| `.xml` | validates XML loader path | exit `0`, completed `true` |
| `.yaml` / `.yml` | validates YAML dependency and loader path | exit `0`, completed `true` |
| `.pdf` | validates PDF dependency and loader path | exit `0`, completed `true` |
| malformed request JSON | validates zero-exit JSON request error behavior | exit `0`, `results == []`, request-scoped evaluator `error` |
| missing evidence path | validates blocked evaluator-owned error shaping | exit `0`, blocked `inconclusive`, evaluator `message_error == 1` |

## Recommended Release Gate

Before wider V2 rollout, the minimum recommendation is:

1. build the release artifact
2. run `make release-validate`
3. create and push the intended release tag
4. let the tag-triggered release workflow handle promotion

If clean-install validation cannot be run in a genuinely fresh environment, do not describe the release as clean-install validated.

Call it local preflight only.

## Current Script

The executable matrix lives here:

- `scripts/release_validation.sh`
- `scripts/release_validation_clean_install.sh`

That script is the canonical implementation of this first-pass validation matrix.
