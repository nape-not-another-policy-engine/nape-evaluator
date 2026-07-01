# V2 Structured Verification Input Proposal

This document proposes a V2 input model for `nape-evaluator` that separates:

- caller-owned request input
- evaluator-owned execution metadata
- loaded evidence content passed into the test
- caller-owned expectation input passed into the test

It is a design proposal, not a statement about current implementation behavior.

This proposal extends the current evaluator model recorded in `current-evaluator-reference.md`. It does not replace the evaluator's existing core responsibility.

This proposal supersedes `test-parameter-exploration.md` as the current V2 input-design proposal. That earlier document remains useful as historical exploratory input.

## Purpose

Use this document to:

- define a clearer V2 structured input contract
- align the input model with the V2 structured result proposal
- keep caller-owned expectation input separate from evaluator-owned metadata
- make it easier to explain what the caller provides versus what the evaluator derives
- expand the current request contract without redefining the evaluator's core execution model

## How To Do Before/After Recording

When this proposal changes terminology, structure, or contract shape, record the update in a consistent before/after format.

Use this pattern:

1. record the exact scope of the change
2. record the `Before` term, field, or snippet
3. record the `After` term, field, or snippet
4. record the rationale for the change
5. record any intentional non-change that remains open

Rules:

- keep current-implementation examples intact when they are serving as baseline context
- apply the updated terminology consistently across the proposed V2 sections
- normalize recorded `After` snippets to the current proposed terminology if a later terminology change affects them
- if a related field is intentionally not renamed yet, say so explicitly rather than leaving the difference unexplained

## Cataloged Design Inputs For This Revision

This revision catalogs the following design inputs and maps each one to a recorded proposal update or proposal section.

1. The input should be a structured request item, because the output/result contract echoes some of that caller-owned input back.
   Addressed by Update `2026-07-01-4` and the `Current Recommended V2 View` section.
2. The caller needs to provide the test locator, evidence locator, and expectation input for one requested evaluation.
   Addressed by Update `2026-07-01-4` and the `Current Recommended Input Item` section.
3. The caller-owned comparison input should be named `expectation`, not `test_parameters`.
   Addressed by Update `2026-07-01-1`.
4. The test-of-detail call boundary should be `evaluate(evidence, expectation, metadata)`.
   Addressed by Update `2026-07-01-2`.
5. Evaluator-owned metadata should not be part of the caller input item.
   Addressed by Update `2026-07-01-3`.
6. The input packet should not carry comparison operators or rule logic; that stays in the Python test.
   Addressed by Update `2026-07-01-5`.
7. Expectation input should remain the caller-provided object shape for now, not a normalized expectation-record array.
   Addressed by Update `2026-07-01-6`.
8. Expectation keys should preserve caller-provided names such as `minCoverage`.
   Addressed by Update `2026-07-01-6` and the `Expectation Value Direction` section.
9. Expectation values should be JSON-compatible so the input stays predictable across transports.
   Addressed by the `Expectation Value Direction` section.
10. The unit of input in this proposal is one requested test execution; top-level batch or manifest input is deferred.
    Addressed by the `Current Recommended V2 View` section and the `Open Design Questions` section.
11. The `evidence` argument received by the test is loaded evidence content, not a pre-extracted fact payload.
    Addressed by Update `2026-07-01-7` and the `Current Recommended Evaluator Call Boundary` section.
12. This proposal must be read as an extension of the implemented evaluator contract, not as a clean-sheet redesign.
    Addressed by Update `2026-07-01-8` and the `Current Fundamentals This Proposal Preserves` section.

## Current Recommended V2 View

This section consolidates the accepted recommendations in this document into one coherent proposal snapshot.

If any historical `Before` or `After` snippet below differs from this section, use this section as the current proposed V2 input contract.

### Accepted Decisions

- the unit of input is one requested test execution
- the caller-owned input item uses `test`, `evidence`, and `expectation`
- `test` and `evidence` are caller-supplied locators
- `expectation` is the caller-supplied free-form expectation object
- the evaluator loads evidence, derives metadata, and calls `evaluate(evidence, expectation, metadata)`
- the test extracts facts from loaded evidence content during evaluation
- `metadata` is evaluator-owned and is not part of the caller input item
- the input packet carries no comparison operators or business-rule logic
- expectation keys preserve caller-provided names such as `minCoverage`
- batch, manifest, and aggregate request shapes are out of scope for this proposal

## Current Fundamentals This Proposal Preserves

These current implementation fundamentals still apply while this proposal expands the input shape:

- the evaluator remains claim-agnostic
- the evaluator still accepts one shared evidence input and one or more requested test invocations
- the evaluator still loads evidence before any test runs
- the evaluator still derives evaluator-owned metadata separately from caller-owned comparison input
- the Python test still extracts facts from loaded evidence during execution
- the Python test still owns comparison logic and human-readable reasoning
- the evaluator still owns transport, execution blocking, messages, and summary behavior

The proposed V2 input work should therefore be read as a cleaner representation of today's invocation input, not as a replacement for the current evaluator model.

### Current Recommended Input Item: Full Caller-Owned Request For One Test Execution

What this is:

This is the complete caller-owned request item for one requested test execution.

It is the external input unit because the caller needs to provide:

- which test should run
- which evidence should be loaded
- which expectation input should be supplied to the test

How it came about:

This shape came from the accepted decision to normalize the caller request around one test execution at a time, while keeping evaluator-owned metadata outside the caller packet.

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

### Current Recommended Evaluator Call Boundary: What The Test Actually Receives

What this is:

This is the effective call boundary after the evaluator has accepted the caller input, loaded the evidence, and derived evaluator-owned metadata.

It shows the three arguments the test actually receives:

- `evidence`
- `expectation`
- `metadata`

Here, `evidence` means the loaded evidence content for the supplied evidence input. It is not a pre-extracted fact payload.

How it came about:

This shape came from the accepted decision to keep caller-owned expectation input separate from evaluator-owned metadata, while still passing both explicitly into the test and leaving fact extraction inside the test implementation.

```python
loaded_evidence_content = ...  # loaded from the provided evidence input

evaluate(
    evidence=loaded_evidence_content,
    expectation={
        "minCoverage": 80
    },
    metadata={
        "evidence_type": "json",
        "schema_version": "2",
    },
)
```

### Current Recommended Metadata Boundary: Evaluator-Owned, Not Caller-Owned

What this is:

This is the evaluator-owned context that may be passed into the test, but is not supplied by the caller as part of the structured input item.

How it came about:

This shape came from the accepted decision to keep the caller request focused on requested evaluation input, while reserving execution context such as evidence typing and schema version for the evaluator.

```json
{
  "evidence_type": "json",
  "schema_version": "2"
}
```

## Recorded Before/After Updates

### Update 2026-07-01-1: Rename caller-owned input field from `test_parameters` to `expectation`

Scope:

- proposed V2 caller input only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "test_parameters": {
    "minCoverage": 80
  }
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

Rationale:

- `expectation` is the stronger domain term for caller-owned comparison input
- it aligns the input terminology with the current V2 result proposal

Intentional non-change:

- current baseline examples in this document may still use `test_parameters` when describing current behavior

### Update 2026-07-01-2: Standardize the test call boundary to `evaluate(evidence, expectation, metadata)`

Scope:

- proposed V2 test call boundary only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```python
def evaluate(evidence, test_parameters, metadata):
    ...
```

After:

```python
def evaluate(evidence, expectation, metadata):
    ...
```

Rationale:

- the second argument should use the same caller-owned input term as the external structured input item
- this keeps the call boundary aligned with the current V2 result proposal

Intentional non-change:

- this revision does not change the meaning or ownership of `metadata`

### Update 2026-07-01-3: Keep evaluator-owned `metadata` outside the caller input item

Scope:

- proposed V2 caller input only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "metadata": {
    "evidence_type": "json",
    "schema_version": "2"
  }
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

Rationale:

- `metadata` is evaluator-owned execution context, not caller-owned request input
- keeping it out of the input packet keeps ownership and validation boundaries clearer

Intentional non-change:

- the evaluator may still derive and pass metadata into the test

### Update 2026-07-01-4: Normalize the caller input around one requested test execution

Scope:

- proposed V2 caller input only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```bash
nape-eval \
  --evidence ./sonar_metrics.json \
  --test ./code_cover_80.py \
  --test-parameters-file ./code_cover_80.parameters.json
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

Rationale:

- the CLI is one transport, but it is not the cleanest contract expression for V2
- the structured request item makes the caller-owned input explicit and easier to align with the output/result model

Intentional non-change:

- this revision does not define a top-level batch or manifest request envelope

### Update 2026-07-01-5: Keep comparison logic out of the caller input packet

Scope:

- proposed V2 caller input only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "name": "minCoverage",
    "operator": "gte",
    "value": 80
  }
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

Rationale:

- comparison operators and business-rule logic belong in the Python test-of-detail implementation
- the caller input should express what is being provided, not how the evaluator should compare it

Intentional non-change:

- this revision does not change how the test internally compares extracted facts against expectation values

### Update 2026-07-01-6: Keep the input `expectation` object free-form and preserve caller-provided keys

Scope:

- proposed V2 caller input only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectations": [
    {
      "name": "minCoverage",
      "value": 80,
      "value_type": "number"
    }
  ]
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

Rationale:

- normalized expectation records belong to the result side, not the caller input side
- the caller input should preserve the expectation object shape and key names as provided

Intentional non-change:

- this revision does not prevent future structured input envelopes if a later V2 step justifies them

### Update 2026-07-01-7: Clarify that `evidence` passed into the test is loaded evidence content, not pre-extracted facts

Scope:

- proposed V2 test call boundary only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```python
evaluate(
    evidence={
        "component": {
            "measures": [
                {"metric": "coverage", "value": "85.0"}
            ]
        }
    },
    expectation={
        "minCoverage": 80
    },
    metadata={
        "evidence_type": "json",
        "schema_version": "2",
    },
)
```

After:

```python
loaded_evidence_content = ...  # loaded from the provided evidence input

evaluate(
    evidence=loaded_evidence_content,
    expectation={
        "minCoverage": 80
    },
    metadata={
        "evidence_type": "json",
        "schema_version": "2",
    },
)
```

Rationale:

- the test receives loaded evidence content, not a pre-extracted fact object
- fact extraction belongs inside the test-of-detail implementation
- the input proposal should not imply a specific evidence shape before the test runs

Intentional non-change:

- this revision does not change the evaluator-owned responsibility for loading evidence before calling the test

### Update 2026-07-01-8: Re-anchor the proposal as an expansion of the current implemented evaluator contract

Scope:

- proposal framing and interpretation only
- proposed V2 explanations in this document

Before:

```text
This document can be read as a standalone redesign of evaluator input shape.
```

After:

```text
This document extends the implemented evaluator model recorded in current-evaluator-reference.md and only expands the caller-owned input shape.
```

Rationale:

- the current evaluator already has a stable execution model that should remain the baseline for V2 evolution
- the proposal work is about clarifying and enriching input shape, not replacing the evaluator's core responsibility

Intentional non-change:

- this revision does not alter the current proposal direction to rename caller-owned comparison input from test_parameters to expectation

## Problem

The current evaluator input is still too transport-oriented.

Today, the caller typically expresses intent through CLI flags such as:

```bash
nape-eval \
  --evidence ./sonar_metrics.json \
  --test ./code_cover_80.py \
  --test-parameters-file ./code_cover_80.parameters.json
```

That is enough to run the evaluator, but it is not enough to express the input contract cleanly as:

- one structured request item for one requested test execution
- a clear split between caller-owned input and evaluator-owned metadata
- an input shape that aligns with the current V2 result proposal

## Core Observation

The caller does not provide loaded evidence objects or evaluator-owned metadata.

The caller provides:

- where the test is
- where the evidence is
- what expectation input should be supplied

The evaluator owns:

- loading the evidence
- deriving metadata
- calling the test with `evaluate(evidence, expectation, metadata)`
- letting the test extract facts from the loaded evidence during evaluation

V2 should represent those ownership boundaries directly.

## Recommended V2 Design Direction

### 1. Use one structured caller input item per requested test execution

The design assumption for V2 should be:

- one structured input item represents one requested test execution

That input item should carry:

- `test`
- `evidence`
- `expectation`

### 2. Keep caller-owned input separate from evaluator-owned metadata

Caller input answers:

- which test should run?
- which evidence should be loaded?
- what expectation input should the test receive?

Evaluator-owned metadata answers:

- what evidence type was loaded?
- what schema version or evaluator contract version applies?

These should not be encoded in the same caller input packet.

### 3. Keep expectation input declarative, not procedural

The caller input should focus on:

- supplied expectation values
- caller-provided expectation keys

The caller input should not carry:

- comparison operators
- rule logic
- evaluator-owned execution metadata

## Proposed Input Shape

The recommended V2 input shape is:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

## Proposed Meaning Of Each Section

### Test

`test` is the caller-supplied locator for the test-of-detail to run.

Current recommended direction:

- use a simple string locator for now
- do not introduce a structured test locator object yet

### Evidence

`evidence` is the caller-supplied locator for the evidence input to load.

Current recommended direction:

- use a simple string locator for now
- do not introduce a structured evidence locator object yet

### Expectation

`expectation` is the caller-supplied expectation input object.

Current recommended direction:

- keep it as the caller-provided object shape
- do not normalize it into an array of expectation records in the input contract
- preserve caller-provided keys such as `minCoverage`
- allow the result contract to echo some or all of this outer expectation if that remains part of the paired result proposal

### Metadata

`metadata` is evaluator-owned context and is not part of the caller input item.

Current recommended direction:

- derive it inside the evaluator
- pass it separately into the test
- do not require the caller to provide it in the structured input contract

## Expectation Value Direction

The safest starting point is to treat `expectation` as a JSON-compatible mapping.

Example:

```json
{
  "minCoverage": 80,
  "allowedStatuses": ["complete", "approved"],
  "requireBranchCoverage": true,
  "owner": null,
  "coveragePolicy": {
    "minLineCoverage": 80,
    "minBranchCoverage": 70
  }
}
```

Recommended allowed value classes:

- string
- integer
- number
- boolean
- null
- array of JSON-compatible values
- object/map of JSON-compatible values

Recommended direction:

- pass expectation values as plain Python dict/list/scalar values
- do not auto-wrap them into dynamic attribute objects
- keep caller-provided keys unchanged

## Input/Output Alignment

The current V2 direction is that the result/output contract may echo some of the caller-owned input.

At minimum, the paired result proposal currently aligns around:

- `test`
- `evidence`
- outer `expectation`

The input contract and result contract should stay compatible on those outer fields even when the inner test-owned `result` payload becomes more structured than the input.

## Example: Coverage Input Reframed For V2

Caller-owned structured input:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  }
}
```

Evaluator-owned call boundary:

```python
loaded_evidence_content = ...  # loaded from the provided evidence input

def evaluate(evidence, expectation, metadata):
    min_coverage = expectation.get("minCoverage")
    ...
```

Example evaluator-owned metadata:

```json
{
  "evidence_type": "json",
  "schema_version": "2"
}
```

## Why This Is Better

This gives V2:

- a cleaner caller input contract than transport-specific CLI flags alone
- a direct alignment point with the current structured result proposal
- clearer ownership boundaries between caller input and evaluator metadata
- a simpler rule that the caller provides `test`, `evidence`, and `expectation`
- a clearer call boundary for test authors using `evaluate(evidence, expectation, metadata)`

## Recommended Test Call Contract

The strongest current recommendation is:

- keep the caller input contract separate from the test call contract
- define the caller input item as `test`, `evidence`, and `expectation`
- keep the test call boundary as `evaluate(evidence, expectation, metadata)`

Recommended direction:

- evaluator owns the caller input parsing and evidence loading
- test-of-detail receives loaded `evidence`, caller-owned `expectation`, and evaluator-owned `metadata`

## Migration Direction

This proposal is intentionally V2-oriented and may justify breaking changes.

Recommended migration direction:

1. define the structured caller input item first
2. keep the CLI as one transport that can populate that input item
3. align the result proposal around any caller-owned fields that should be echoed back
4. update test authoring docs to teach `evaluate(evidence, expectation, metadata)`
5. evaluate batch or manifest-level structured input only after the per-test input item is stable

## Open Design Questions

The main questions still needing explicit review are:

1. Should the outer caller input remain one per-test item only, or should V2 later add a top-level list/manifest request shape?
2. Should `test` and `evidence` remain plain string locators, or should they later become structured locator objects?
3. Should the evaluator validate expectation values strictly as JSON-compatible before calling the test?
4. How much of the caller input should the outer result envelope echo back?

## Current Recommendation

The strongest current recommendation is:

- use the `Current Recommended V2 View` section as the source of truth for the current proposed input contract
- use one structured caller input item per requested test execution
- keep the caller input item to `test`, `evidence`, and `expectation`
- keep `expectation` as the caller-provided object shape
- preserve caller-provided expectation keys such as `minCoverage`
- keep evaluator-owned `metadata` outside the caller input item
- keep the test call boundary as `evaluate(evidence, expectation, metadata)`
- keep comparison operators and business-rule logic inside the Python test-of-detail implementation
