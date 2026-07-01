# Plan 02: Expectation Binding And CLI Transport

## Goal

Define and document how caller-supplied comparison/configuration input should be transported into requested test executions, while preserving explicit ownership and safe failure behavior.

## Naming Note

Current committed code and some current docs still use `test_parameters`.

Current V2 proposal direction prefers `expectation`.

This plan must be explicit about whether a statement refers to:

- the current implemented contract
- the proposed V2 terminology

## Baseline

Read first:

1. `docs/product/current-evaluator-reference.md`
2. `docs/product/test-parameter-exploration.md`
3. `docs/reference/evaluator-contract.md`
4. `docs/user/cli-reference.md`

## Current State

Current committed behavior:

- test call boundary is `evaluate(evidence, test_parameters, metadata)`
- direct CLI support uses repeated `--test-parameters-file`
- parameter files are matched to repeated `--test` arguments by position
- if parameter files are used, one must currently be supplied for every `--test`
- parameter transport/setup failures block only the affected invocation when possible

## Scope

In scope:

- direct CLI binding models
- parameter/expectation transport behavior
- ownership boundaries between evaluator and test
- evaluator-side versus test-side failure handling
- documentation of explicit calling patterns

Out of scope:

- network-based parameter resolution
- hidden type coercion
- claim semantics
- unrelated result-packet redesign beyond what is needed to stay aligned with Plan 01

## Work Plan

1. Preserve the current three-argument test boundary.
   Do not reopen the basic signature unless a deliberate product decision says otherwise.

2. Decide the direct CLI binding model.
   Evaluate positional binding, scoped binding, and inline one-at-a-time inputs.

3. Keep ownership explicit.
   Caller-owned comparison input should stay separate from evaluator-owned metadata.

4. Keep failure ownership explicit.
   Evaluator-side transport/setup failures should remain distinct from test-owned returned errors.

5. Clarify documentation language.
   Make current versus proposed terminology visible so readers do not confuse implemented `test_parameters` with proposed `expectation`.

6. Feed approved outcomes back into permanent docs.
   Update CLI, contract, authoring, and product docs once decisions are stable.

## Open Questions

- Should direct CLI binding remain positional?
- Should `--test` become an explicit current-test scope for subsequent expectation input?
- Should one-at-a-time direct entry be supported, such as `key=<json-value>` bindings?
- Should file-based and inline binding be mutually exclusive per test at first?
- Should manifest-style binding wait until scoped CLI semantics are settled?

## Done Criteria

This plan is ready to close when:

- a binding model is chosen and recorded
- failure ownership is documented clearly
- current versus proposed terminology is explained clearly
- permanent user/reference/product docs reflect the approved direction
