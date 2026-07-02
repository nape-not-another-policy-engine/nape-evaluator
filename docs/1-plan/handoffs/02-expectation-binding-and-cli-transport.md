# Handoff 02: Expectation Binding And CLI Transport

## Purpose

Resume caller-supplied evaluation-input transport work without losing the current implementation context.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/02-expectation-binding-and-cli-transport.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/test-parameter-exploration.md`
5. `docs/reference/evaluator-contract.md`
6. `docs/user/cli-reference.md`

## Current State

- the evaluator currently supports `evaluate(evidence, test_parameters, metadata)`
- direct CLI parameter transport currently uses repeated `--test-parameters-file`
- binding is positional across repeated `--test`
- the current implementation already produces one result item per requested invocation, including blocked invocations
- the selected V2 proposal direction no longer uses `expectation`; it now uses caller-owned `evaluations[*].subject` plus `criteria`
- the selected V2 direct CLI direction is now:
  - `--invoke` for non-file usage
  - `--invoke-file` for file usage
  - `--request-file` for full-request file or stdin usage
  - one repeated invocation packet per test
  - each invocation packet contains both `test` and `evaluations`
- the selected full-request direction is to accept one full outer JSON request packet through `--request-file`, where `-` means stdin, rather than only a repeated invocation list
- the selected V2 CLI transport direction is also packet-based only; micro-flag decomposition is not part of the V2 direction

## Primary Review Questions

The direct binding model is now selected.

Remaining questions are:

None on the core V2 CLI transport shape.

## Current Recommendation

The strongest current direction is:

- keep the three-argument test contract
- keep packet-shaped caller input
- use one repeated invocation packet per test
- support `--invoke` and `--invoke-file`
- support `--request-file` for programmatic callers or full-request submission
- use a full outer request packet for file-or-stdin transport
- keep V2 packet-based only rather than adding micro-flags for decomposed subject/criteria input
- treat current positional file binding as implemented baseline only, not the V2 direction
- keep full-request transport separate from the human direct-flag shape

## Guardrails

- do not hide current implementation terminology when the behavior is still committed as `test_parameters`
- do not silently coerce caller input types
- do not mix evaluator-owned metadata with caller-owned comparison input
- do not fall back to positional matching for V2 direct CLI
- do not split one invocation across multiple unrelated CLI flags if the packet-based model has already been chosen
- do not introduce a custom binary transport as the first V2 process-to-process interface
- do not introduce a second micro-flag input language for V2 caller-owned evaluation packets
