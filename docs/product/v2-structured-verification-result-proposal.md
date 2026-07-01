# V2 Structured Verification Result Proposal

This document proposes a V2 result model for `nape-evaluator` that separates:

- evaluator execution
- evaluation conclusion
- fact extraction
- expectation comparison
- human-readable substantiation

It is a design proposal, not a statement about current implementation behavior.

This proposal extends the current evaluator model recorded in `current-evaluator-reference.md`. It does not replace the evaluator's existing outer execution model.

## Purpose

Use this document to:

- define a clearer V2 verification-result contract
- reduce ambiguity between execution failures and evaluation conclusions
- support future V2 verification procedures and verification reports
- make extracted facts and expected conditions first-class machine-readable data
- expand the current per-test result row rather than redesign the evaluator's core responsibility

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

1. The output must record both extracted facts and supplied expectations, not only a conclusion and reason.
   Addressed by Updates `2026-07-01-6` and `2026-07-01-7`.
2. A single test-of-detail may extract one or more facts before it can conclude anything.
   Addressed by Update `2026-07-01-6` and the `Recommended Test Author Flow` section.
3. Fact and expectation records need human-readable names plus explicit `value` and `value_type`.
   Addressed by Updates `2026-07-01-6` and `2026-07-01-9`.
4. The evaluator packet should not carry comparison operators such as `gte`; that logic stays in the Python test.
   Addressed by Update `2026-07-01-7`.
5. If a required fact cannot be extracted, the result should generally be `inconclusive` and should say which fact could not be found.
   Addressed by Update `2026-07-01-8`.
6. If a required expectation is missing or unusable, the result should generally be `inconclusive` and should say which expectation was missing or unusable.
   Addressed by Update `2026-07-01-8`.
7. `reason` remains the human-readable sentence that explains why the conclusion is `true`, `false`, or `inconclusive`.
   Addressed throughout this proposal and reinforced in Update `2026-07-01-6`.
8. Test authoring should be described as fact extraction first, then expectation validation, then evaluation.
   Addressed by the `Recommended Test Author Flow` section.
9. The proposal needs a bounded set of allowed `value_type` values for fact and expectation records.
   Addressed by Update `2026-07-01-9` and the `Proposed Value Types` section.
10. Input/output symmetry matters, but this proposal is normalizing the output packet first while leaving the outer caller-supplied expectation object intact for now.
    Addressed by the `Caller-Supplied Expectation Input` section and the `Open Design Questions` section.
11. Fact source provenance is not needed in the current V2 packet and should be omitted.
    Addressed by Update `2026-07-01-10`.
12. Expectation records should use the caller-provided input name only and should not carry a separate `fact_name`.
    Addressed by Update `2026-07-01-11`.
13. The inner structured payload object should be named `result`, not `verification`.
    Addressed by Update `2026-07-01-12`.
14. This proposal must be read as an expansion of the implemented evaluator contract, not as a clean-sheet redesign.
    Addressed by Update `2026-07-01-13` and the `Current Fundamentals This Proposal Preserves` section.

## Current Recommended V2 View

This section consolidates the accepted recommendations in this document into one coherent proposal snapshot.

If any historical `Before` or `After` snippet below differs from this section, use this section as the current proposed V2 contract.

### Accepted Decisions

- the evaluator is claim-agnostic and does not carry claim semantics in its packet
- the outer result envelope is evaluator-owned
- the test-of-detail owns the structured `result` payload
- the outer envelope uses `test`, `evidence`, `expectation`, `execution`, and `result`
- the outer `expectation` object remains the caller-supplied input shape for now
- the result payload uses `conclusion`, `facts`, `expectations`, and `reason`
- `conclusion` values are `true`, `false`, and `inconclusive`
- fact and expectation records are normalized and include explicit `name`, `value`, `value_type`, and status fields
- comparison operators and evaluation logic stay in the Python test-of-detail implementation
- missing required facts or expectations generally produce `conclusion: "inconclusive"`
- evaluator-owned failures stay outside `result` and are represented through `execution` and evaluator messages

## Current Fundamentals This Proposal Preserves

These current implementation fundamentals still apply while this proposal expands the result shape:

- the evaluator remains claim-agnostic
- the evaluator still emits one outer result item per requested test invocation
- the evaluator still owns execution state, blocked invocation handling, messages, and summary behavior
- the Python test still owns fact extraction, comparison logic, and human-readable reasoning
- evidence is still loaded by the evaluator before test execution
- evaluator-owned operational failures remain distinct from test-owned evaluation conclusions

The proposed V2 result work should therefore be read as a structured expansion of today's per-test result row, not as a replacement for the current evaluator model.

### Update 2026-07-01-10: Remove `facts.source` from the proposed V2 result payload

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "result": {
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found",
        "source": "component.measures[metric=coverage].value"
      }
    ]
  }
}
```

After:

```json
{
  "result": {
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ]
  }
}
```

Rationale:

- the current evaluator result does not need evidence-location provenance for extracted facts
- removing `source` keeps the packet smaller and easier to author and consume
- fact identity, value, value type, and status are sufficient for the current V2 direction

Intentional non-change:

- this revision does not change how the Python test internally locates or extracts facts from evidence

### Update 2026-07-01-11: Remove `fact_name` from expectation records and preserve the caller-provided input name as `name`

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "result": {
    "expectations": [
      {
        "name": "minimum coverage",
        "fact_name": "coverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ]
  }
}
```

After:

```json
{
  "result": {
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ]
  }
}
```

Rationale:

- the current V2 packet does not need a second naming layer for expectations
- `name` should preserve the caller-provided expectation key from input
- removing `fact_name` keeps expectation records smaller and avoids implying a formal fact-to-expectation mapping contract

Intentional non-change:

- this revision does not change how the Python test internally decides which extracted facts to evaluate against a given expectation input

### Update 2026-07-01-12: Rename the inner structured payload object from `verification` to `result`

Scope:

- proposed V2 outer result envelope only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "verification": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

After:

```json
{
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

Rationale:

- the object is the test-owned evaluation result payload, so `result` is the clearer current V2 term
- using `result` avoids overloading the word `verification` between the packet object and higher-level verification procedures or reports
- the rename makes the outer result envelope easier to explain as evaluator-owned `execution` plus test-owned `result`

Intentional non-change:

- this revision does not rename higher-level phrases such as verification procedures or verification reports

### Update 2026-07-01-13: Re-anchor the proposal as an expansion of the current implemented evaluator contract

Scope:

- proposal framing and interpretation only
- proposed V2 explanations in this document

Before:

```text
This document can be read as a standalone redesign of evaluator output shape.
```

After:

```text
This document extends the implemented evaluator model recorded in current-evaluator-reference.md and only expands the per-test result shape.
```

Rationale:

- the current evaluator already has a stable outer result envelope and execution model that should remain the baseline for V2 evolution
- the proposal work is about enriching the current result row with clearer structure, not replacing the evaluator's core responsibility

Intentional non-change:

- this revision does not change the current proposal direction to move from flat outcome/reason fields toward a structured result payload

### Current Recommended Outer Result Item: Full Evaluator Output Envelope

What this is:

This is the complete V2 result item the evaluator would emit for one requested test execution.

It is the outermost packet because the evaluator owns transport and execution concerns such as:

- which test was requested
- which evidence input was provided
- what caller-supplied expectation input was provided
- whether execution completed or was blocked
- what structured result payload came back from the test

How it came about:

This shape came from the accepted decision to separate evaluator-owned execution state from test-owned result content, while still returning one stable per-test result item to the caller.

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

### Current Recommended Result Payload Returned By The Test: Structured Test-Owned Evaluation Output

What this is:

This is the inner `result` object that the Python test-of-detail itself would return when it completes evaluation.

It exists because the proposal now treats the test as the owner of:

- the conclusion
- the extracted facts
- the normalized expectation records used during evaluation
- the human-readable reason

How it came about:

This shape came from the accepted decision to stop returning only `(outcome, reason)` and instead let the test return a structured result payload that the evaluator wraps inside the outer result envelope.

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "coverage",
      "value": 85.0,
      "value_type": "number",
      "unit": "percent",
      "status": "found"
    }
  ],
  "expectations": [
    {
      "name": "minCoverage",
      "value": 80,
      "value_type": "number",
      "unit": "percent",
      "status": "provided"
    }
  ],
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

### Current Recommended Inconclusive Shape For Missing Facts: Completed Execution But Insufficient Evidence

What this is:

This is the recommended full result shape when the evaluator successfully runs the test, but the test cannot extract a required fact from the evidence.

It is still a completed execution because the evaluator loaded the evidence, loaded the test, and ran the test function successfully. The result is `inconclusive` because the test could not establish the needed fact.

How it came about:

This shape came from the accepted decision that missing required facts should generally be represented inside `result` with explicit fact status, and that this condition should usually conclude `inconclusive` rather than being treated as an evaluator-owned execution failure.

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "inconclusive",
    "facts": [
      {
        "name": "coverage",
        "value": null,
        "value_type": "number",
        "unit": "percent",
        "status": "not_found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Unable to evaluate because the coverage fact could not be found in the evidence."
  }
}
```

### Current Recommended Blocked Execution Shape: Evaluator Could Not Complete The Invocation

What this is:

This is the recommended full result shape when the evaluator cannot safely complete the requested invocation at all.

In this case there is no `result` payload because the test did not produce an evaluation result. Typical reasons would be evaluator-owned failures such as evidence-loading failure, test-loading failure, or another blocked execution path before the test could return structured output.

How it came about:

This shape came from the accepted decision to keep evaluator-owned execution failures outside the result model and to represent them through `execution` plus evaluator messages instead.

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "execution": {
    "executed": false,
    "status": "blocked"
  },
  "result": null
}
```

## Recorded Before/After Updates

### Update 2026-07-01-1: Rename caller-owned outer result field from `test_parameters` to `expectation`

Scope:

- proposed V2 outer result envelope only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./sonar_metrics.json",
  "test_parameters": {
    "minCoverage": 80
  },
  "executed": true,
  "outcome": "pass",
  "reason": "Coverage is 85.0%, which meets the required 80%.",
  "test_parameters_source": "./code_cover_80.parameters.json"
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "executed": true,
  "conclusion": "true",
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

Rationale:

- `expectation` is the stronger domain term for the caller-owned input being checked against extracted facts
- it better aligns the outer result envelope with the fact/expectation/conclusion language used elsewhere in the proposal

Intentional non-change:

- current baseline examples in this proposal still use `test_parameters` when describing the current implementation

### Update 2026-07-01-2: Rename proposed result term from `outcome` to `conclusion` and adopt `true` / `false` / `inconclusive`

Scope:

- proposed V2 result terminology only
- proposed V2 examples, recommendations, and open questions in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "executed": true,
  "outcome": "pass",
  "reason": "Coverage is 85.0%, which meets the required 80%.",
  "test_parameters_source": "./code_cover_80.parameters.json"
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "executed": true,
  "conclusion": "true",
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

Rationale:

- `conclusion` is the stronger domain term for whether the evidence satisfied the test logic
- `true` / `false` / `inconclusive` better distinguish evaluation conclusion from operational execution status
- this keeps `pass` / `fail` language from leaking into a result model that is intended to report evaluation outcomes cleanly

Intentional non-change:

- current baseline examples in this proposal still use `outcome` and `pass` / `fail` / `inconclusive` when describing the current implementation

### Update 2026-07-01-3: Remove `test_parameters_source` from the proposed V2 result envelope

Scope:

- proposed V2 outer result envelope only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "conclusion": "true",
  "reason": "Coverage is 85.0%, which meets the required 80%.",
  "test_parameters_source": "./code_cover_80.parameters.json"
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "conclusion": "true",
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

Rationale:

- the proposal should record the caller-owned expectation itself, not the transport path used to provide it
- expectation input may arrive through more than one mechanism in V2
- those mechanisms may include per-test files, inline CLI binding, manifest-driven binding, or future orchestration inputs
- tracing how the expectation was supplied is not necessary to substantiate the evaluation conclusion

Intentional non-change:

- current baseline examples in this proposal still use `test_parameters_source` when describing the current implementation

### Update 2026-07-01-4: Rename proposed outer evidence locator field from `evidence_file` to `evidence`

Scope:

- proposed V2 outer result envelope only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "conclusion": "true",
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

After:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "conclusion": "true",
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

Rationale:

- the value already identifies the evidence input, so `file` does not add useful meaning
- `evidence` is the simpler domain term and keeps the outer result envelope less transport-specific
- if V2 later allows other evidence locators, the shorter field name remains stable

Intentional non-change:

- current baseline examples in this proposal still use `evidence_file` when describing the current implementation

### Update 2026-07-01-5: Remove `claim` from the proposed V2 result payload

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "result": {
    "claim": {
      "id": "minimum_code_coverage",
      "title": "Minimum Code Coverage",
      "statement": "Code coverage must be at least 80%."
    },
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0
      }
    ],
    "expectation": {
      "fact": "coverage",
      "operator": "gte",
      "value": 80
    },
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

After:

```json
{
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

Rationale:

- the evaluator is only responsible for executing the test-of-detail against evidence using the supplied expectation
- the evaluator does not own or understand any higher-level claim semantics
- if a claim statement is needed, it should be owned by a higher-level verification procedure or reporting layer, not by the evaluator packet

Intentional non-change:

- current baseline examples in this proposal remain focused on the current implementation contract rather than on higher-level claim wording

### Update 2026-07-01-6: Normalize result payloads around named `facts` and `expectations`

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "unit": "percent",
        "source": "component.measures[metric=coverage].value"
      }
    ],
    "expectation": {
      "fact": "coverage",
      "operator": "gte",
      "value": 80,
      "unit": "percent",
      "parameter_key": "minCoverage"
    },
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

After:

```json
{
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

Rationale:

- the packet should show both what was observed and what was expected
- facts need stable extracted names and expectations should preserve the caller-provided input names, with explicit machine-readable values
- one evaluation may depend on more than one fact, so plural normalized records are a better long-term shape
- `reason` stays human-readable, but it should not be the only place where fact and expectation meaning lives

Intentional non-change:

- the outer caller-supplied `expectation` object remains unchanged in this revision

### Update 2026-07-01-7: Keep comparison logic out of the evaluator packet

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "expectation": {
    "fact": "coverage",
    "operator": "gte",
    "value": 80,
    "unit": "percent",
    "parameter_key": "minCoverage"
  }
}
```

After:

```json
{
  "expectations": [
    {
      "name": "minCoverage",
      "value": 80,
      "value_type": "number",
      "unit": "percent",
      "status": "provided"
    }
  ]
}
```

Rationale:

- the evaluator packet should report facts, expectations, and conclusion, not the internal comparison algorithm
- operators such as `gte` belong in the Python test-of-detail logic
- removing operator fields keeps the packet simpler and avoids implying the evaluator understands the business rule

Intentional non-change:

- this proposal does not change how the Python test implements its own comparison logic

### Update 2026-07-01-8: Represent missing facts or expectations explicitly and generally conclude `inconclusive`

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "result": {
    "conclusion": "inconclusive",
    "facts": [],
    "expectation": {
      "fact": "coverage",
      "value": 80
    },
    "reason": "The 'coverage' metric is missing from the evidence."
  }
}
```

After:

```json
{
  "result": {
    "conclusion": "inconclusive",
    "facts": [
      {
        "name": "coverage",
        "value": null,
        "value_type": "number",
        "unit": "percent",
        "status": "not_found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Unable to evaluate because the coverage fact could not be found in the evidence."
  }
}
```

Rationale:

- the packet should say which fact or expectation blocked the evaluation
- empty collections alone do not explain what the test tried to extract or validate
- a bounded missing-data representation makes defensive authoring guidance clearer

Intentional non-change:

- this proposal still leaves room for evaluator-level failures to remain outside `result`

### Update 2026-07-01-9: Add bounded `value_type` fields for facts and expectations

Scope:

- proposed V2 result payload only
- proposed V2 examples and proposed V2 explanations in this document

Before:

```json
{
  "facts": [
    {
      "name": "coverage",
      "value": 85.0
    }
  ],
  "expectations": [
    {
      "name": "minimum coverage",
      "value": 80
    }
  ]
}
```

After:

```json
{
  "facts": [
    {
      "name": "coverage",
      "value": 85.0,
      "value_type": "number"
    }
  ],
  "expectations": [
    {
      "name": "minCoverage",
      "value": 80,
      "value_type": "number"
    }
  ]
}
```

Rationale:

- report consumers should not have to infer value shape from the raw value alone
- explicit value types make authoring rules clearer when a fact is missing, malformed, or evaluated differently by evidence type
- units such as `percent` should stay separate from `value_type`

Intentional non-change:

- this proposal does not require every value type to carry a unit

## Problem

The current evaluator contract is still too execution-oriented.

Today, a test-of-detail returns:

```python
outcome, reason
```

and the evaluator wraps that into a result item such as:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./sonar_metrics.json",
  "test_parameters": {
    "minCoverage": 80
  },
  "executed": true,
  "outcome": "pass",
  "reason": "Coverage is 85.0%, which meets the required 80%.",
  "test_parameters_source": "./code_cover_80.parameters.json"
}
```

That is enough to say what happened, but it is not enough to express:

- what fact or facts were extracted from the evidence
- what expectation or expectations the facts were evaluated against
- whether the conclusion is about expectation satisfaction or failure of execution
- which fact or expectation blocked the evaluation when the result is `inconclusive`

This becomes a real limitation if V2 verification reports need to explain:

- the extracted fact value
- the expected fact value or values
- the basis for the final conclusion

## Core Observation

The current `reason` field is prose.

It is useful for people, but it is not reliable as the machine-readable source of:

- the fact name
- the fact value
- the fact value type
- the expected value
- the expected value type
- the test-owned comparison logic

The evaluator should not try to infer those from:

- free-text `reason`
- parameter key names such as `minCoverage`

That domain meaning already exists inside the test-of-detail logic. V2 should let the test return it explicitly.

## Recommended V2 Design Direction

### 1. Separate execution from verification conclusion

Execution answers:

- did the evaluator load the evidence?
- did it load the test?
- did it call the test successfully?

Result answers:

- what fact or facts were extracted?
- what expectation or expectations applied?
- what conclusion was reached?
- what facts or expectations were missing or unusable?

These should not be encoded in the same field.

### 2. Treat one test-of-detail as one bounded evaluation

The design assumption for V2 should be:

- one test-of-detail performs one bounded evaluation against one evidence input using one supplied expectation object

That evaluation can depend on:

- one fact
- or multiple facts

The model should not artificially restrict the schema to one fact, even if authoring guidance says most tests should evaluate one primary detail.

The common authoring pattern should be:

1. extract facts
2. validate required expectations
3. evaluate the extracted facts against the supplied expectations using Python test logic

### 3. Reserve errors for execution or contract problems

The result layer should focus on:

- `true`
- `false`
- `inconclusive`

Execution or contract failures should remain separate from evaluation conclusion.

This avoids overloading one field to mean both:

- “the evidence did not satisfy the supplied expectation”
- “the system could not perform the evaluation safely”

## Proposed Result Shape

The recommended V2 result shape is:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

## Proposed Meaning Of Each Section

### Execution

`execution` is evaluator-owned.

It answers whether the requested invocation actually ran.

Proposed fields:

- `executed`: boolean
- `status`: bounded execution vocabulary such as:
  - `completed`
  - `blocked`
  - `invalid`

Recommended direction:

- use `executed: true` only when the test function actually completed
- use `executed: false` when the evaluator could not safely complete the invocation

### Caller-Supplied Expectation Input

`expectation` is the caller-owned expectation input preserved in the outer result envelope.

It captures the input object that the caller intended the test to evaluate against.

Recommended direction:

- use `expectation` in the outer V2 result envelope instead of `test_parameters`
- keep it as the caller-supplied object shape, not as a normalized comparison model
- treat it as distinct from `result.expectations`
- do not preserve transport-specific source metadata in the outer V2 result envelope
- do not add source-tracing fields such as file path, manifest locator, or CLI position for expectation provenance
- allow it to remain less structured than the normalized result output for now

Meaning of the distinction:

- outer `expectation`: caller-owned input as supplied to the test
- `result.expectations`: normalized machine-readable expectation records returned by the test for reporting and comparison semantics

### Result

`result` is the structured evaluation payload returned by the test-of-detail.

It should be present only when the evaluation layer is actually available.

Recommended subfields:

- `conclusion`
- `facts`
- `expectations`
- `reason`

### Facts

`facts` are the observed values extracted from evidence.

Recommended fields per fact:

- `name`
- `value`
- `value_type`
- `status`
- optional `unit`

Recommended fact status values:

- `found`
- `not_found`
- `invalid`

### Expectations

`expectations` expresses the caller-supplied expectation records the extracted facts are evaluated against.

Recommended fields per expectation:

- `name`
- `value`
- `value_type`
- `status`
- optional `unit`

This allows the report layer to explain:

- which expectation input was provided
- what was expected
- what was observed

`name` should preserve the caller-provided expectation key from input, such as `minCoverage`.

Recommended expectation status values:

- `provided`
- `not_provided`
- `invalid`

### Proposed Value Types

Recommended bounded `value_type` vocabulary:

- `text`
- `integer`
- `number`
- `boolean`
- `date`
- `datetime`
- `duration`
- `array`
- `object`
- `null`

Recommended direction:

- use `value_type` for the shape of the value
- use `unit` separately for measurement semantics such as `percent`, `days`, or `bytes`
- do not encode comparison logic into `value_type`

### Reason

`reason` remains a human-readable substantiation summary.

It should explain the conclusion clearly, but it should not be the only place where the fact and expectation meaning exists.

### Recommended Test Author Flow

Recommended authoring flow inside a test-of-detail:

1. validate evaluator-owned metadata needed to interpret the evidence safely
2. extract the required facts and record their names, values, value types, and statuses
3. validate the required expectations and record their names, values, value types, and statuses
4. if a required fact is `not_found` or `invalid`, return `conclusion: "inconclusive"`
5. if a required expectation is `not_provided` or `invalid`, return `conclusion: "inconclusive"`
6. only after facts and expectations are usable, apply the Python evaluation logic
7. return a human-readable `reason` that explains the final `true`, `false`, or `inconclusive` conclusion

## Example: Current Coverage Test Reframed For V2

Current caller-owned input object:

```json
{
  "minCoverage": 80
}
```

In the current implementation this input is passed as `test_parameters`.

In the proposed V2 result envelope, this same caller-owned concept is recorded as `expectation`.

Current test-of-detail:

```python
def evaluate(evidence, test_parameters, metadata):
    if metadata.get("evidence_type") != "json":
        return "error", "This test expects JSON evidence."

    min_coverage = test_parameters.get("minCoverage")
    if not isinstance(min_coverage, (int, float)):
        return "error", "This test requires numeric test parameter 'minCoverage'."

    measures = evidence.get("component", {}).get("measures", [])
    coverage_value = None
    for measure in measures:
        if measure.get("metric") == "coverage":
            coverage_value = float(measure.get("value", 0))
            break

    if coverage_value is None:
        return "inconclusive", "The 'coverage' metric is missing from the evidence."
    if coverage_value >= min_coverage:
        return "pass", f"Coverage is {coverage_value}%, which meets the required {min_coverage}%."
    return "fail", f"Coverage is {coverage_value}%, which is below the required {min_coverage}%."
```

Recommended V2 return direction:

```python
def evaluate(evidence, expectation, metadata):
    if metadata.get("evidence_type") != "json":
        raise ValueError("This test expects JSON evidence.")

    min_coverage = expectation.get("minCoverage")

    expectation_record = {
        "name": "minCoverage",
        "value": min_coverage if isinstance(min_coverage, (int, float)) else None,
        "value_type": "number",
        "unit": "percent",
        "status": "provided" if isinstance(min_coverage, (int, float)) else "not_provided",
    }

    if expectation_record["status"] != "provided":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "expectations": [expectation_record],
            "reason": "Unable to evaluate because the required expectation 'minCoverage' was not provided as a numeric value."
        }

    measures = evidence.get("component", {}).get("measures", [])
    coverage_value = None
    for measure in measures:
        if measure.get("metric") == "coverage":
            coverage_value = float(measure.get("value", 0))
            break

    if coverage_value is None:
        return {
            "conclusion": "inconclusive",
            "facts": [
                {
                    "name": "coverage",
                    "value": None,
                    "value_type": "number",
                    "unit": "percent",
                    "status": "not_found"
                }
            ],
            "expectations": [expectation_record],
            "reason": "Unable to evaluate because the coverage fact could not be found in the evidence."
        }

    conclusion = "true" if coverage_value >= min_coverage else "false"
    reason = (
        f"Coverage is {coverage_value}%, which meets the required {min_coverage}%."
        if conclusion == "true"
        else f"Coverage is {coverage_value}%, which is below the required {min_coverage}%."
    )

    return {
        "conclusion": conclusion,
        "facts": [
            {
                "name": "coverage",
                "value": coverage_value,
                "value_type": "number",
                "unit": "percent",
                "status": "found"
            }
        ],
        "expectations": [expectation_record],
        "reason": reason
    }
```

## Why This Is Better

This gives V2:

- structured facts instead of only prose
- structured expectations instead of inferred threshold meaning
- caller-owned input named with a domain term that reflects what it represents
- explicit fact and expectation statuses when required inputs are missing or unusable
- explicit value types for both observed facts and supplied expectations
- a clean split between evaluation conclusion and evaluator execution status
- a better basis for future verification reports that add their own claim wording outside the evaluator

It also avoids pretending the evaluator can infer higher-level claim semantics from generic parameter names.

## Recommended Test Return Contract

The strongest current recommendation is:

- stop returning only `(outcome, reason)` in V2
- return a structured result object from the test-of-detail
- let the evaluator wrap that inside the outer execution/result envelope

Recommended direction:

- evaluator owns the outer result envelope
- test-of-detail owns the structured `result` payload

## Proposed Outer Evaluator Contract

Recommended V2 result item:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80,
        "value_type": "number",
        "unit": "percent",
        "status": "provided"
      }
    ],
    "reason": "Coverage is 85.0%, which meets the required 80%."
  }
}
```

For blocked execution, recommended shape:

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "expectation": {
    "minCoverage": 80
  },
  "execution": {
    "executed": false,
    "status": "blocked"
  },
  "result": null
}
```

Operational details would still live under evaluator messages.

## Migration Direction

This proposal is intentionally V2-oriented and may justify breaking changes.

Recommended migration direction:

1. define the structured result schema first
2. use `conclusion` with `true` / `false` / `inconclusive` at the result layer
3. update test authoring docs to teach fact extraction, expectation validation, and structured returns
4. update verification reports to consume `facts`, `expectations`, and `reason`, while keeping any claim wording outside the evaluator contract
5. provide fixture examples for:
   - `true`
   - `false`
   - `inconclusive`
   - blocked execution
   - missing fact
   - missing expectation

## Open Design Questions

The main questions still needing explicit review are:

1. Should the outer caller-supplied `expectation` object stay free-form, or should V2 later upgrade it into a structured input envelope that names expected facts explicitly?
2. Should the evaluator validate the returned `result` object shape strictly?

## Current Recommendation

The strongest current recommendation is:

- use the `Current Recommended V2 View` section as the source of truth for the current proposed contract
- separate execution status from evaluation conclusion
- make facts and expectations first-class structured fields
- use `expectation` as the outer caller-owned input term in the V2 result envelope
- use `conclusion` as the truth-status term in the V2 result model
- use `true` / `false` / `inconclusive` as the evaluation conclusion vocabulary
- use normalized `facts` and `expectations` records with explicit `name`, `value`, `value_type`, and status fields
- keep comparison operators and evaluation logic inside the Python test-of-detail implementation
- treat missing required facts or expectations as `inconclusive` unless the failure is evaluator-owned
- keep `reason` as prose, not as the sole machine-readable truth source
- let tests return structured result payloads directly
- use this model as the basis for V2 verification procedures and verification reports
