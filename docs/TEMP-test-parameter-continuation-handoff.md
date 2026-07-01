# TEMP Test Parameter Continuation Handoff

Date: 2026-06-30

Purpose:

- preserve the next review entry point for the test-parameter feature
- tell the next session exactly what to read before making more CLI changes

## Current Implementation State

The evaluator currently supports:

- `evaluate(evidence, test_parameters, metadata)`
- direct CLI parameter files through repeated `--test-parameters-file`
- one result item per requested invocation, including blocked invocations

Current CLI limitation:

- if any `--test-parameters-file` is used, one must currently be supplied for every `--test`
- parameter ownership is matched by position, not by an explicit scoped syntax

## Review First When Resuming

Read these documents in this order:

1. `docs/product/test-parameter-exploration.md`
2. `docs/TEMP-test-parameter-feature-plan.md`
3. `docs/reference/evaluator-contract.md`
4. `docs/user/cli-reference.md`

Focus specifically on the CLI binding options section in `docs/product/test-parameter-exploration.md`.

## Primary Review Questions

Before adding more CLI parameter features, decide:

1. Should direct CLI binding remain positional?
2. Should `--test` become an explicit invocation scope?
3. Should inline one-at-a-time parameters be added as `--test-parameter key=<json-value>`?
4. Should `--test-parameters-file` and inline parameters be mutually exclusive per test in the first version?
5. Should manifest-style binding wait until after the current-test scoped CLI is settled?

## Recommended Next Direction

The strongest current recommendation is:

- keep the current three-argument test contract
- keep dict-only parameter payloads
- move future CLI ergonomics toward current-test scoped binding
- prefer `--test-parameter key=<json-value>` for one-at-a-time direct CLI entry
- keep file-based input as an alternative under the current test

## Stop Conditions

Do not start another CLI syntax implementation until the binding model is explicitly chosen and recorded.
