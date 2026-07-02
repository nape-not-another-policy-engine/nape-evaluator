# Handoff 09: CLI Zero-Exit JSON Contract

## Purpose

Resume the CLI zero-exit JSON contract workstream without re-deriving why it exists.

## Status

This workstream is complete.

The selected contract is now implemented:

- exact standalone `--check-install` remains a plain-text operational command
- every non-`--check-install` invocation returns exit `0` plus stdout JSON
- malformed caller/request input is surfaced as request-scoped evaluator `error` messages inside the normal outer JSON envelope

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/09-cli-zero-exit-json-contract.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/reference/evaluator-contract.md`
5. `docs/user/cli-reference.md`
6. `docs/user/software-integration/request-and-invocation.md`
7. `docs/user/software-integration/response-handling.md`
8. `src/nape_evaluator/application/io/cli.py`
9. `tests/test_cli_contract.py`

## Selected Starting Direction

- `--check-install` stays a separate operational command for now
- non-`--check-install` invocations should always return exit `0` plus stdout JSON
- malformed caller/request input should be represented through evaluator-style request-scoped error messages, not parser-only stderr exits

## Completed Outputs

1. CLI implementation change
2. logical-path tests for malformed input and request validation
3. current-doc alignment across user/reference/product/software-integration docs
