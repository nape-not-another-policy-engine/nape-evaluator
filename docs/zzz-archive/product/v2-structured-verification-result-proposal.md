> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# V2 Structured Verification Result Proposal

This document proposes a V2 result model for `nape-evaluator` that separates:

- evaluator-owned execution state
- caller-owned input echoed by the evaluator
- test-owned extracted facts
- test-owned evaluation conclusion
- test-owned human-readable substantiation

It is a design proposal, not a statement about current implementation behavior.

This proposal extends the current evaluator model recorded in `current-evaluator-reference.md`. It does not replace the evaluator's existing outer execution model.

## Purpose

Use this document to:

- define a clearer V2 result contract
- reduce ambiguity between execution failures and evaluation conclusions
- align the result model with the selected V2 input model
- support future V2 verification procedures and verification reports
- expand the current per-test result row rather than redesign the evaluator's core responsibility

## Baseline This Proposal Preserves

The following current implementation fundamentals still apply while this proposal expands the result shape:

- the evaluator remains claim-agnostic
- the evaluator still emits one outer result item per requested test invocation
- the evaluator still owns execution state, blocked invocation handling, messages, and summary behavior
- the Python test still owns fact extraction, comparison logic, and human-readable reasoning
- evidence is still loaded by the evaluator before test execution
- evaluator-owned operational failures remain distinct from test-owned evaluation conclusions

The proposed V2 result work should therefore be read as a structured expansion of today's per-test result row, not as a replacement for the current evaluator model.

## Input Alignment Basis

The paired V2 input proposal now selects:

- outer request shape: `test` + `evidence` + `evaluations`
- test call boundary: `evaluate(evidence, evaluations, metadata)`
- one `subject` plus one object-valued `criteria` packet per `evaluations[*]` item
- strict validation of caller-owned input before test execution

This result proposal is aligned to that selected input direction.

## Current Selected V2 Direction

This section is the current source of truth for the selected V2 result direction.

### Selected Decisions

- the evaluator is claim-agnostic and does not carry claim semantics in its packet
- the outer result envelope is evaluator-owned
- the outer result envelope echoes:
  - `test`
  - `evidence`
  - the full accepted caller-owned `evaluations` array
- the outer result envelope also carries evaluator-owned `execution`
- the Python test-of-detail owns the inner structured `result` payload
- the aligned test return boundary is one combined structured `result` object
- the inner `result` payload uses:
  - `conclusion`
  - `facts`
  - `reason`
- the inner `result` payload does not carry normalized `expectations`
- caller-owned `criteria` remains visible through outer echoed `evaluations[*].criteria`
- `conclusion` values are:
  - `true`
  - `false`
  - `inconclusive`
- evaluator-owned failures stay outside `result` and are represented through `execution` and evaluator messages
- the Python test may use multiple extracted facts and multiple caller-supplied criteria values together when computing one combined conclusion and one combined reason

### Current Recommended Outer Result Item

```json
{
  "test": "./coverage_policy.py",
  "evidence": "./sonar_metrics.json",
  "evaluations": [
    {
      "subject": {
        "name": "branch_coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "threshold_split": 95
      }
    },
    {
      "subject": {
        "name": "line_coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "minimum_when_branch_coverage_below_split": 90,
        "minimum_when_branch_coverage_meets_split": 80
      }
    }
  ],
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "false",
    "facts": [
      {
        "name": "branch_coverage",
        "value": 92.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      },
      {
        "name": "line_coverage",
        "value": 82.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "reason": "Branch coverage is 92.0%, which is below the 95.0% split threshold, so the applicable minimum line coverage is 90.0%. Line coverage is 82.0%, which does not satisfy that requirement."
  }
}
```

## Meaning Of Each Section

### Test

`test` is the caller-supplied test locator echoed by the evaluator.

### Evidence

`evidence` is the caller-supplied evidence locator echoed by the evaluator.

### Evaluations

`evaluations` is the full accepted caller-owned evaluation input echoed by the evaluator.

It remains outer-envelope data because it is caller-owned input, not test-owned derived result content.

### Execution

`execution` is evaluator-owned.

It answers whether the requested invocation actually ran.

Recommended fields:

- `executed`: boolean
- `status`: bounded execution vocabulary such as:
  - `completed`
  - `blocked`
  - `invalid`

Recommended direction:

- use `executed: true` only when the test function actually completed
- use `executed: false` when the evaluator could not safely complete the invocation

### Result

`result` is the structured evaluation payload returned by the Python test-of-detail.

It should be present only when the evaluation layer is actually available.

Recommended subfields:

- `conclusion`
- `facts`
- `reason`

## Facts Model

`facts` are the observed values extracted from evidence and used by the Python test when forming the final conclusion.

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

## Conclusion Model

`conclusion` is the test-owned evaluation outcome for the full test-of-detail invocation.

Recommended values:

- `true`
- `false`
- `inconclusive`

Recommended direction:

- use `true` when the extracted facts satisfy the Python test logic under the supplied criteria values
- use `false` when the extracted facts do not satisfy that logic
- use `inconclusive` when the test cannot safely form a conclusion from the available facts and usable criteria values

Execution or contract failures should remain separate from `conclusion`.

## Reason Model

`reason` remains a human-readable substantiation summary.

It should explain the final combined conclusion clearly, but it should not be the only place where the extracted fact meaning exists.

## Recommended Test Return Contract

The strongest current recommendation is:

- stop returning only `(outcome, reason)` in V2
- return one structured combined `result` object from the test-of-detail
- let the evaluator wrap that test-owned `result` object inside the outer execution/result envelope

Recommended aligned test boundary:

```python
evaluate(evidence, evaluations, metadata)
```

Recommended aligned test return shape:

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
  "reason": "Coverage is 85.0%, which meets the required threshold."
}
```

Rationale:

- the Python test owns the reasoning logic
- one test invocation may use multiple facts and multiple caller-supplied criteria values to produce one final decision
- the evaluator should not infer the final result shape from lower-level fragments

## Type Invariants And Compatibility

### Result Invariants

- outer `test` must be present
- outer `evidence` must be present
- outer `evaluations` must be present when execution completed
- `execution` must always be present
- `result` must be present only when `execution.executed == true`
- when `result` is present, it must contain:
  - `conclusion`
  - `facts`
  - `reason`
- `facts` must be an array
- each fact must carry:
  - `name`
  - `value`
  - `value_type`
  - `status`

### Result-Type Compatibility Note

The input proposal already constrains which criteria variants are compatible with which `subject.data_type` values.

The result proposal should not duplicate caller-owned criteria semantics inside `result`.

Instead:

- outer `evaluations[*].criteria` preserves the accepted caller-owned benchmark values
- inner `result.facts[*]` preserves the extracted observed values actually used by the test
- `result.reason` explains how those facts led to the final conclusion under the test's logic

## Valid Examples

### Simple Threshold Case

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "evaluations": [
    {
      "subject": {
        "name": "coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "minimum": 80
      }
    }
  ],
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
    "reason": "Coverage is 85.0%, which meets the required 80.0% threshold."
  }
}
```

### Combined Multi-Fact Reasoning Case

Clarifying terms used in this proposal:

- `branch_coverage`
  The percentage of branch paths or decision outcomes exercised by tests.
- `line_coverage`
  The percentage of executable lines exercised by tests.

Example policy shape:

- if `branch_coverage < 95`, require `line_coverage >= 90`
- if `branch_coverage >= 95`, require `line_coverage >= 80`

This is intentionally a longer-tail example.

Most uses will still involve one primary subject with a simpler criteria object such as `minimum`.

```json
{
  "test": "./coverage_policy.py",
  "evidence": "./sonar_metrics.json",
  "evaluations": [
    {
      "subject": {
        "name": "branch_coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "threshold_split": 95
      }
    },
    {
      "subject": {
        "name": "line_coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "minimum_when_branch_coverage_below_split": 90,
        "minimum_when_branch_coverage_meets_split": 80
      }
    }
  ],
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "false",
    "facts": [
      {
        "name": "branch_coverage",
        "value": 92.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      },
      {
        "name": "line_coverage",
        "value": 82.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found"
      }
    ],
    "reason": "Branch coverage is 92.0%, which is below the 95.0% split threshold, so the applicable minimum line coverage is 90.0%. Line coverage is 82.0%, which does not satisfy that requirement."
  }
}
```

Meaning of this example:

- there are two extracted facts:
  - `branch_coverage`
  - `line_coverage`
- there are multiple caller-supplied criteria values across the echoed `evaluations` array
- the caller can change those criteria values without changing the Python test logic
- the Python test still owns the conditional reasoning logic that decides which criteria value applies

### Inconclusive Case

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./sonar_metrics.json",
  "evaluations": [
    {
      "subject": {
        "name": "coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "minimum": 80
      }
    }
  ],
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
    "reason": "Unable to evaluate because the coverage fact could not be found in the evidence."
  }
}
```

### Blocked Execution Case

```json
{
  "test": "./code_cover_80.py",
  "evidence": "./image.png",
  "evaluations": [
    {
      "subject": {
        "name": "coverage",
        "data_type": "number"
      },
      "criteria": {
        "required": true,
        "minimum": 80
      }
    }
  ],
  "execution": {
    "executed": false,
    "status": "blocked"
  },
  "result": null
}
```

## Invalid Examples

### Caller-Owned Criteria Repeated In The Inner Result

```json
{
  "result": {
    "conclusion": "true",
    "facts": [],
    "expectations": [
      {
        "name": "minCoverage",
        "value": 80
      }
    ],
    "reason": "ok"
  }
}
```

Invalid for the aligned direction because:

- result-side `expectations` is no longer the selected model
- caller-owned benchmark information should remain visible through outer echoed `evaluations[*].criteria`

### Execution Failure Misrepresented As Test Conclusion

```json
{
  "execution": {
    "executed": false,
    "status": "blocked"
  },
  "result": {
    "conclusion": "false",
    "facts": [],
    "reason": "Evidence file type unsupported."
  }
}
```

Invalid because:

- evaluator-owned execution failures should remain outside the test-owned `result`
- blocked execution should use `result: null`

## Why This Is Better

This gives V2:

- a clean split between evaluator-owned execution state and test-owned evaluation content
- caller-owned input echoed in the outer packet without inventing a second result-side criteria vocabulary
- structured extracted facts instead of relying only on prose
- one combined conclusion and one combined reason that match how one test-of-detail invocation actually works
- support for both:
  - simple one-subject threshold checks
  - longer-tail multi-fact conditional reasoning
- a better basis for future verification reports that add their own higher-level semantics outside the evaluator contract

## Migration Direction

This proposal is intentionally V2-oriented and may justify breaking changes.

Recommended migration direction:

1. align the outer result envelope with the selected `evaluations`-based input model
2. stop emitting result-side `expectations` in the proposed V2 contract
3. update test authoring docs to teach `evaluate(evidence, evaluations, metadata)` and one combined structured `result` return
4. update verification reports to consume:
   - echoed outer `evaluations`
   - extracted `facts`
   - one combined `conclusion`
   - one combined `reason`
5. provide fixture examples for:
   - `true`
   - `false`
   - `inconclusive`
   - blocked execution
   - missing fact
   - combined multi-fact reasoning

## Remaining Follow-Up Points

The main remaining work after this revision is:

1. update user/reference docs that still describe the earlier `expectation`-based proposal direction
2. update test authoring docs to teach `evaluate(evidence, evaluations, metadata)` and the new combined `result` return shape
3. decide later whether result reporting needs:
   - stable evaluation IDs
   - richer fact provenance
   - evaluator-owned aggregation summaries beyond `execution`

## Current Recommendation

The strongest current recommendation is:

- echo caller-owned `test`, `evidence`, and `evaluations` in the outer result envelope
- keep `execution` evaluator-owned
- let the test-of-detail return one combined structured `result`
- keep the inner `result` focused on:
  - `conclusion`
  - `facts`
  - `reason`
- remove result-side `expectations` in favor of outer echoed `evaluations[*].criteria`
- keep comparison operators and evaluation logic inside the Python test-of-detail implementation
- allow one combined conclusion and reason to depend on multiple extracted facts and multiple caller-supplied criteria values
