# Plan 09: CLI Zero-Exit JSON Contract

## Goal

Change the evaluator CLI contract so non-`--check-install` invocations always return:

- exit status `0`
- one machine-readable JSON object on stdout

even when caller-owned request input is malformed or otherwise cannot cross the current request-builder seam.

## Why This Is Its Own Plan

This is a real public-contract change.

Today the evaluator has split behavior:

- evaluator execution problems generally return `0` plus stdout JSON
- CLI misuse and request/JSON parsing problems often return non-zero and human-readable stderr only

That split makes wrapper behavior inconsistent and forces downstream callers to treat parser/request errors differently from evaluator-owned blocked/error reporting.

If the selected product direction is that evaluator invocations should always produce the evaluator-style machine-readable response contract, this needs coordinated changes across:

- CLI behavior
- tests
- reference docs
- user docs
- software-integration guidance

## Baseline

Read first:

1. `docs/1-plan/roadmap.md`
2. `docs/product/current-evaluator-reference.md`
3. `docs/reference/evaluator-contract.md`
4. `docs/user/cli-reference.md`
5. `docs/user/software-integration/request-and-invocation.md`
6. `docs/user/software-integration/response-handling.md`
7. `docs/product/nape-evaluator-product-spec.md`
8. `docs/maintainers/testing-and-interface-standards.md`
9. `src/nape_evaluator/application/io/cli.py`
10. `tests/test_cli_contract.py`

## Selected Starting Direction

Starting recommendation:

- keep `--check-install` as a separate operational command
- keep its current plain-text success behavior unless a later decision explicitly changes it
- change every non-`--check-install` invocation path to return:
  - exit `0`
  - stdout JSON

This starting direction treats `--check-install` as installation/health tooling rather than evaluator-execution transport.

It treats all evaluator-execution paths, including malformed caller input, as part of one machine-readable evaluator boundary.

## Key Design Question

When request input is malformed before a validated request object exists, the CLI still needs to emit a bounded JSON contract.

Recommended first-pass direction:

- emit:
  - `results: []`
  - `evaluator.messages` containing one or more request-scoped `error` messages
  - `evaluator.summary` derived from zero result rows and emitted evaluator messages

Why this direction:

- there may be no safe accepted invocation rows to echo
- it preserves one stable outer JSON shape
- it keeps malformed caller input machine-readable without pretending that blocked per-test rows existed when the request never validated

## Logical Paths This Plan Must Cover

At minimum:

1. no-argument invocation
2. invalid flag combinations
3. missing required direct-mode arguments
4. malformed `--invoke` JSON
5. malformed `--invoke-file` JSON
6. malformed `--request-file` JSON
7. request-file top-level wrong type
8. request-builder validation failures
9. evaluator execution failures that already return JSON today
10. `--check-install` behavior, whether unchanged or intentionally changed

## Expected Documentation Updates

At minimum:

- `README.md`
- `docs/product/current-evaluator-reference.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/cli-reference.md`
- `docs/user/software-integration/request-and-invocation.md`
- `docs/user/software-integration/response-handling.md`
- `docs/product/nape-evaluator-product-spec.md`
- relevant maintainer/testing docs if logical-path expectations change

## Current Status

Complete.

Implemented outputs:

- non-`--check-install` CLI invocations now return exit status `0` plus one JSON object on stdout
- malformed CLI and request input now return request-scoped evaluator `error` messages inside the normal outer JSON envelope
- logical-path CLI tests now cover malformed `--invoke`, malformed `--invoke-file`, malformed `--request-file`, malformed stdin request JSON, unknown flags, and direct-mode validation failures
- current user, reference, product, and maintainer docs have been aligned to the selected contract
