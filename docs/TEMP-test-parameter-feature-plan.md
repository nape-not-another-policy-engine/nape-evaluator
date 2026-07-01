# TEMP Test Parameter Feature Plan

Date: 2026-06-30

Purpose:

- plan a V2 feature for passing caller-supplied comparison/configuration inputs into a test-of-detail
- pressure-test type handling, failure behavior, and user-facing explicitness before implementation
- keep evaluator metadata ownership separate from caller-owned test parameters

Related documents:

- `docs/product/nape-evaluator-product-spec.md`
- `docs/product/v2-policy-direction.md`
- `docs/product/test-parameter-exploration.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/test-of-detail-authoring.md`

## Problem Statement

The current evaluator can pass:

- `evidence`
- evaluator-owned `metadata`

It cannot yet pass caller-owned comparison inputs such as:

- threshold values
- allowed value sets
- nested policy objects
- action-specific configuration needed by the test-of-detail

This blocks an important class of tests where the evidence is constant in shape but the acceptance criteria vary by action or procedure configuration.

## Feature Goal

Enable a test-of-detail to receive caller-supplied test parameters while preserving:

- explicit contract boundaries
- deterministic execution
- clear failure reporting
- safe defensive behavior under missing or malformed inputs

## Non-Goals

- no attempt to infer business meaning from the parameter values
- no network fetches or external lookups during parameter resolution
- no implicit backward-compatibility mode for old raw-text evidence behavior
- no hidden parameter coercion that changes caller intent silently

## Recommended Direction

Recommended function signature:

```python
def evaluate(evidence, test_parameters, metadata):
    ...
```

Recommended parameter shape:

- JSON-compatible dict at the top level

Recommended ownership split:

- `test_parameters` remains caller-owned
- `metadata` remains evaluator-owned

Locked design decisions for implementation:

- `test_parameters` is always a dict
- no implicit scalar coercion
- V2 breaks the test signature to three arguments
- direct evaluator CLI support uses repeated `--test-parameters-file <json-file>`
- the internal request model moves from bare `test_paths` to per-test invocation objects
- evaluator-side parameter transport/setup failures block only the affected invocation when possible
- test-specific parameter mismatch remains a returned result-level `error`

## Why This Direction

This direction is preferred because it:

- avoids overloading metadata with caller-owned content
- keeps caller-owned comparison inputs adjacent to the evidence under evaluation
- makes contract review and documentation clearer
- lets tests validate only the parameters they actually require
- gives the evaluator a clean place to reject parameter transport failures before execution

## Major Design Workstreams

### 1. Contract Shape

Decide:

- final `evaluate(...)` signature
- whether empty `test_parameters` should be `{}` or `None`
- whether direct CLI invocation will expose this feature or whether NAPE CLI remains the only orchestrator

Recommendation:

- use `evaluate(evidence, test_parameters, metadata)`
- pass `{}` when no parameters exist
- expose direct CLI parameter passing through repeated `--test-parameters-file` inputs

### 2. Request Model

The current request model is:

```python
EvaluateEvidenceRequest(
    evidence_path=...,
    test_paths=[...],
)
```

This feature likely requires a richer invocation model such as:

```python
TestInvocationRequest(
    test_path="...",
    test_parameters={...},
)
```

and then:

```python
EvaluateEvidenceRequest(
    evidence_path="...",
    test_invocations=[...],
)
```

This should be planned before code changes so parameter mapping does not become an ad hoc side table.

### 3. Type Model

Recommended initial allowed types:

- string
- integer
- float
- boolean
- null
- list of JSON-compatible values
- dict with string keys and JSON-compatible values

Recommended first rule:

- no implicit scalar coercion

Examples:

- numeric `80` is accepted as numeric threshold
- string `"80"` is not silently converted to numeric `80`
- string-list requirements remain string-list requirements

Why:

- explicitness is more important than convenience here
- silent coercion makes caller misunderstandings harder to detect

### 4. Failure Ownership

Evaluator-owned failure examples:

- parameter envelope cannot be decoded
- parameters are not structurally passable to the test
- repeated test invocations cannot be matched to the right parameter payload

Recommended evaluator behavior:

- produce evaluator `error` message
- do not call the affected test if the call boundary is unsafe
- continue with other requested test invocations when their parameter inputs are valid

Test-owned failure examples:

- missing required parameter
- wrong parameter type for a known key
- parameter value is present but outside the test's accepted business meaning

Recommended test behavior:

- return result-level `error`
- explain the mismatch explicitly
- preserve `ran` for that invocation

### 5. User-Facing Explicitness

This feature must be explicit for the calling user in at least three places:

- what parameters were expected
- why the evaluator could or could not call the test safely
- why a test rejected or accepted the supplied parameter values

Recommended direction:

- evaluator messages should cover transport/setup failures
- test result reasons should cover test-specific parameter mismatch

Potential future message/result codes to consider:

- evaluator-side:
  - `test_parameter_decode_error`
  - `test_parameter_shape_error`
  - `test_parameter_mapping_error`
- test-side:
  - returned `error` with explicit reason text from the test

### 6. Migration And Breaking Change

This feature is likely a contract-breaking change if the evaluator moves from:

```python
def evaluate(evidence, metadata):
```

to:

```python
def evaluate(evidence, test_parameters, metadata):
```

Planning must decide:

- V2 requires all tests to adopt the new signature
- no temporary bridge will be added for two-argument tests

This is separate from raw-evidence backward compatibility.

## Recommended Implementation Slices

### Slice 0: Product Contract Lock

- completed direction:
  - final signature is `evaluate(evidence, test_parameters, metadata)`
  - top-level parameter shape is dict
  - no-parameter calls pass `{}`

### Slice 1: Domain Model Refactor

- introduce a per-test invocation request model
- stop representing test requests as only bare path strings

### Slice 2: Evaluator Invocation Wiring

- pass parameters through the use case
- update test-of-detail call sites
- preserve current result/message accounting rules

### Slice 3: Failure Translation

- define evaluator-side failure translation for parameter transport/setup errors
- keep those distinct from result-level `error`

### Slice 4: Authoring Contract Update

- document how test authors read and validate `test_parameters`
- provide scalar, list, and nested-object examples
- state clearly that implicit coercion is not assumed

### Slice 5: Test Coverage

Add tests for:

- empty parameters
- missing required parameter
- wrong scalar type
- wrong container type
- nested object success
- evaluator-side parameter envelope failure
- result/error accounting and message accounting under parameter failures

## Deep Review Questions

These questions should be answered before code work:

1. Is top-level `test_parameters` always a dict, or do we need to support scalar top-level values?
2. Should parameter validation be entirely test-owned after basic envelope validation?
3. Should the evaluator include any parameter-shape metadata back to the test, or is separation cleaner?
4. How should repeated test invocations with different parameters be represented in request models and output?
5. If direct CLI support exists later, what input format is explicit enough for non-technical users without hiding types?

## Recommended Next Step

Use `docs/product/test-parameter-exploration.md` as the ideation surface, then turn the answers to the deep review questions into a final product contract before touching the evaluator code.

## Post-Implementation Follow-Up

The core parameter feature is now implemented, but direct CLI binding ergonomics remain open for review.

Current implementation state:

- `evaluate(evidence, test_parameters, metadata)` is active
- direct CLI file-based parameter input exists
- repeated `--test-parameters-file` is currently matched to repeated `--test` by position
- if any parameter file is used, one must currently be provided for every requested test

This means the next planning slice is no longer about whether parameters exist, but about whether the current CLI binding model is the right long-term user contract.

### Slice 6: CLI Binding Ergonomics Review

Review and decide:

- whether positional binding should remain
- whether `--test` should open an explicit current-test scope
- whether one-at-a-time inline parameters should be added
- whether file-based and inline parameter input should be mutually exclusive per test in the first pass
- whether manifest-style binding should remain a later expansion rather than the next step

Recommended next-direction candidate:

- treat each `--test` as an invocation scope
- allow repeated `--test-parameter key=<json-value>` under the current test
- keep `--test-parameters-file` as an alternative under the current test
- reject parameter flags before any `--test`
- reject mixing inline and file-based parameter input for the same test until the simpler contract is proven

Reference:

- `docs/product/test-parameter-exploration.md`
- `docs/TEMP-test-parameter-continuation-handoff.md`
