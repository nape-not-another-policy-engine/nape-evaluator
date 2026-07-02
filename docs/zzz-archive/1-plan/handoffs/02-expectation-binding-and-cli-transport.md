> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 02: Expectation Binding And CLI Transport

## Purpose

Record the completed state and closure decision for caller-supplied evaluation-input transport work.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/02-expectation-binding-and-cli-transport.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/test-parameter-exploration.md`
5. `docs/reference/evaluator-contract.md`
6. `docs/user/cli-reference.md`

## Current State

- the older transition problem is now resolved
- the selected V2 proposal direction no longer uses `expectation`; it now uses caller-owned `evaluations[*].subject` plus `criteria`
- the selected V2 direct CLI direction is now:
  - `--invoke` for non-file usage
  - `--invoke-file` for file usage
  - `--request-file` for full-request file or stdin usage
  - one repeated invocation packet per test
  - each invocation packet contains both `test` and `evaluations`
- the selected full-request direction is to accept one full outer JSON request packet through `--request-file`, where `-` means stdin, rather than only a repeated invocation list
- the selected V2 CLI transport direction is also packet-based only; micro-flag decomposition is not part of the V2 direction
- that direction is now implemented in the runtime and reflected in current-reference and user-facing docs
- the older positional `--test` plus `--test-parameters-file` transport is baseline history only, not active runtime guidance

## Closure Decision

This workstream is complete.

Do not continue it by default.

If future transport expansion is needed, treat it as a new explicit workstream rather than unfinished residue from Plan 02.

## Why It Closed

- the core V2 CLI transport shape is selected
- the request-packet model is implemented
- the direct CLI and full-request forms are documented
- no remaining core transport ambiguity is recorded in this workstream

## If Reopened Later

Only reopen a similar workstream if one of these becomes true:

- product direction requires a new transport mode
- a new non-CLI integration surface must be standardized
- packet-based-only transport is no longer sufficient for a real caller need

## Guardrails

- do not silently coerce caller input types
- do not mix evaluator-owned metadata with caller-owned comparison input
- do not fall back to positional matching for V2 direct CLI
- do not split one invocation across multiple unrelated CLI flags if the packet-based model has already been chosen
- do not introduce a custom binary transport as the first V2 process-to-process interface
- do not introduce a second micro-flag input language for V2 caller-owned evaluation packets

## Durable Outputs

- the selected packet-based CLI/request transport direction
- the implemented runtime support for:
  - `--invoke`
  - `--invoke-file`
  - `--request-file`
- the aligned current-reference, CLI, and README documentation
