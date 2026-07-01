# Handoff 02: Expectation Binding And CLI Transport

## Purpose

Resume caller-supplied expectation transport work without losing the current implementation context.

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

## Primary Review Questions

Before adding more CLI input features, decide:

1. should direct CLI binding remain positional?
2. should `--test` become an explicit invocation scope?
3. should inline one-at-a-time input be added?
4. should inline input and file-based input be mutually exclusive per test in the first version?
5. should manifest-style binding wait until scoped CLI binding is settled?

## Current Recommendation

The strongest current direction is:

- keep the three-argument test contract
- keep dict-shaped caller input
- move future CLI ergonomics toward explicit per-test scoping
- treat current positional file binding as implemented baseline, not necessarily the final ergonomic direction

## Guardrails

- do not hide current implementation terminology when the behavior is still committed as `test_parameters`
- do not silently coerce caller input types
- do not mix evaluator-owned metadata with caller-owned comparison input
- do not start another CLI syntax implementation until the binding model is explicitly chosen and recorded
