> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# V2 Structured Verification Input Proposal

This document proposes a V2 input model for `nape-evaluator` that separates:

- caller-owned request input
- evaluator-owned execution metadata
- loaded evidence content passed into the test
- test-owned extraction and evaluation logic

It is a design proposal, not a statement about current implementation behavior.

This proposal extends the current evaluator model recorded in `current-evaluator-reference.md`. It does not replace the evaluator's existing core responsibility.

This proposal supersedes `test-parameter-exploration.md` as the active V2 input-design proposal.

## Purpose

Use this document to:

- define a clearer V2 structured input contract
- align the input model with the V2 structured result proposal
- keep caller-owned evaluation input separate from evaluator-owned metadata
- make it easier to explain what the caller provides versus what the evaluator derives
- expand the current request contract without redefining the evaluator's core execution model

## Baseline This Proposal Preserves

The following current implementation fundamentals still apply while this proposal expands the input shape:

- the evaluator remains claim-agnostic
- the evaluator still accepts one shared evidence input and one or more requested test invocations
- the evaluator still loads evidence before any test runs
- the evaluator still derives evaluator-owned metadata separately from caller-owned input
- the Python test still extracts facts from loaded evidence during execution
- the Python test still owns comparison logic and human-readable reasoning
- the evaluator still owns transport, execution blocking, messages, and summary behavior

The proposed V2 input work should therefore be read as a structured expansion of today's invocation input, not as a redesign of the evaluator's core role.

## External Terminology Basis

This proposal uses assurance-oriented terminology as substantiation for the newer input shape.

Relevant external references:

- IAASB publication page for ISAE 3000 (Revised):
  https://www.iaasb.org/publications/international-standard-assurance-engagements-isae-3000-revised-assurance-engagements-other-audits-or
- IAASB PDF for ISAE 3000 (Revised):
  https://www.iaasb.org/_flysystem/azure-private/publications/files/ISAE%203000%20Revised%20-%20for%20IAASB.pdf

Why these references matter:

- ISAE 3000 uses `criteria` as the benchmark used to measure or evaluate an underlying subject matter
- ISAE 3000 uses `subject matter information` for the outcome of applying criteria to an underlying subject matter
- that terminology is closer to `subject` plus `criteria` than to `expectation`

This proposal is not adopting the full standards wording literally.

Instead, it uses product-facing terms that stay close to assurance terminology while remaining readable for implementers:

- `evaluations`
- `subject`
- `criteria`

## Current Selected V2 Direction

This section is the current source of truth for the selected V2 input direction.

### Selected Decisions

- the outer caller-owned request shape is `test` + `evidence` + `evaluations`
- `test` and `evidence` remain plain string locators in the first pass
- `evaluations` is a caller-owned array of one or more evaluation items
- each `evaluations[*]` item contains:
  - one `subject`
  - one object-valued `criteria`
- that one `criteria` object may contain multiple compatible first-pass criteria keys
- `subject` and `criteria` are the selected contract names
- the first-pass `subject` object is limited to:
  - `name`
  - `data_type`
- `subject.name` is a normalized machine-readable string
- `subject.data_type` uses a bounded vocabulary
- first-pass `criteria` is object-only; scalar shorthand is not supported
- first-pass supported `criteria` keys are:
  - `minimum`
  - `maximum`
  - `equals`
  - `allowed_values`
  - `disallowed_values`
  - `required`
- evaluator-owned `metadata` remains outside the caller-owned request packet
- evaluator validation should reject malformed or incompatible input before test execution
- no-coercion rules are strict across transports, including CLI-originated input
- the outer result envelope should echo `test`, `evidence`, and the full accepted `evaluations` array

### Current Recommended Outer Request

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
  ]
}
```

## Meaning Of Each Top-Level Field

### Test

`test` is the caller-supplied locator for the test-of-detail to run.

First-pass direction:

- use a simple string locator
- do not introduce a structured test locator object yet

### Evidence

`evidence` is the caller-supplied locator for the evidence input to load.

First-pass direction:

- use a simple string locator
- do not introduce a structured evidence locator object yet

### Evaluations

`evaluations` is the caller-owned list of evaluation items to be applied during one requested test execution.

Each evaluation item declares:

- the `subject` being evaluated
- the `criteria` to apply to that subject

First-pass direction:

- keep the structure explicit and declarative
- do not collapse evaluation items into a looser free-form comparison object

### Metadata

`metadata` is evaluator-owned context and is not part of the caller-owned request.

First-pass direction:

- derive metadata inside the evaluator
- pass it separately into the test
- do not require the caller to provide it in the structured input contract

## Evaluation Item Model

Each `evaluations[*]` item has this first-pass shape:

```json
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
```

### Subject

The `subject` object identifies what the test is expected to extract and what type that extracted value should have.

First-pass fields:

- `name`
- `data_type`

Selected first-pass direction:

- do not add subject variants in the first pass beyond a single named typed subject object
- defer fields such as `unit`, `path_hint`, `description`, `required`, and collection-shape details unless they become necessary in a later V2 step

### Subject Name

`subject.name` is a normalized machine-readable string.

Selected working rule for this proposal revision:

- use lowercase `snake_case`
- allow ASCII letters, digits, and underscore
- begin with a letter
- end with an alphanumeric character
- require the caller to submit an already-normalized ASCII name
- reject non-conforming names instead of silently rewriting or transliterating them

Examples:

- `coverage`
- `branch_coverage`
- `build_age_days`

Invalid examples:

- `Coverage`
- `branch-coverage`
- `80_coverage`
- `branch coverage`
- `coverage_`
- `covérage`

### Subject Data Type

`subject.data_type` uses this bounded vocabulary:

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

Definitions and examples:

- `text`
  Definition:
  A string value whose meaning is textual rather than numeric, temporal, or structural.
  Examples:
  - `"approved"`
  - `"A-12345"`
  - `"coverage_exception"`
  Notes:
  - use `text` for identifiers, labels, codes, and free-form strings
  - do not use `text` for values that the test is expected to compare numerically or temporally

- `integer`
  Definition:
  A whole-number numeric value with no fractional component.
  Examples:
  - `0`
  - `3`
  - `42`
  Notes:
  - use `integer` when whole-number semantics matter
  - examples include counts, retry limits, or an exact number of days when fractional values are not valid

- `number`
  Definition:
  A numeric value that may include a fractional component.
  Examples:
  - `80`
  - `80.0`
  - `99.95`
  Notes:
  - use `number` when decimal or fractional values are allowed
  - `number` may also accept whole numbers, but its semantic difference from `integer` is that fractions are permitted
  Differentiation from `integer`:
  - `integer` means fractions are not valid
  - `number` means fractions are valid, even if a particular example happens to be whole
  Recommendation:
  - keep both `integer` and `number`; do not collapse them

- `boolean`
  Definition:
  A true/false value.
  Examples:
  - `true`
  - `false`
  Notes:
  - use `boolean` for binary conditions such as enabled/disabled, present/not present, or pass-through flags
  - do not substitute strings such as `"true"` or `"false"`

- `date`
  Definition:
  A calendar date without a time-of-day component.
  Examples:
  - `"2026-07-01"`
  - `"2026-12-31"`
  Notes:
  - use `date` when only the calendar date matters
  - recommended representation is ISO 8601 date format `YYYY-MM-DD`
  Differentiation from `datetime`:
  - `date` has no time-of-day or timezone semantics
  - `datetime` includes a specific point in time

- `datetime`
  Definition:
  A timestamp or point in time with date and time components.
  Examples:
  - `"2026-07-01T14:30:00Z"`
  - `"2026-07-01T10:30:00-04:00"`
  Notes:
  - use `datetime` when time-of-day or timezone matters
  - recommended representation is ISO 8601 datetime format
  Differentiation from `date`:
  - use `date` for calendar-only comparisons
  - use `datetime` for temporal precision beyond the calendar day

- `duration`
  Definition:
  A length of time rather than a calendar date or timestamp.
  Examples:
  - `"P30D"`
  - `"PT4H"`
  - `"P1DT12H"`
  Notes:
  - use `duration` for elapsed-time constraints such as retention periods, timeouts, or age windows
  - recommended representation is ISO 8601 duration format
  Differentiation from `integer` and `number`:
  - use `duration` when the value means elapsed time as a typed concept
  - use `integer` or `number` only when the value is a plain numeric quantity and any time unit is handled separately

- `array`
  Definition:
  An ordered list of JSON-compatible values.
  Examples:
  - `["complete", "approved"]`
  - `[80, 85, 90]`
  - `[{"name": "coverage"}, {"name": "branch_coverage"}]`
  Notes:
  - use `array` when multiplicity and order are relevant or when the subject naturally returns a list
  - element typing is not yet separately modeled in this first pass

- `object`
  Definition:
  A JSON object or mapping with named fields.
  Examples:
  - `{"line": 80, "branch": 70}`
  - `{"status": "approved", "owner": "security_team"}`
  Notes:
  - use `object` when the subject is a structured value with named properties
  - nested object shape is not yet separately modeled in this first pass
  Differentiation from `array`:
  - `object` is keyed by field names
  - `array` is an ordered list

- `null`
  Definition:
  An explicit null value.
  Examples:
  - `null`
  Notes:
  - use `null` only when the absence of a value is itself the value being evaluated
  - this should not be confused with a missing field or an extraction failure
  Differentiation from missing or invalid:
  - `null` means the subject value is explicitly present as null
  - missing means the subject was not present
  - invalid means the subject was present but unusable for the required type

Representation note:

- these definitions describe the intended semantic category of the extracted subject value
- domain semantics such as `percent`, `days`, `bytes`, or `uri` should be modeled separately from `data_type`

## Criteria Model

`criteria` is an object-valued packet that carries the caller-supplied evaluation benchmarks for one `subject`.

Selected first-pass direction:

- `criteria` is object-only
- scalar shorthand is not supported in the first pass
- if shorthand is ever added later, it should be transport sugar only after the canonical object model is stable

### Supported First-Pass Criteria Keys

- `minimum`
- `maximum`
- `equals`
- `allowed_values`
- `disallowed_values`
- `required`

Selected first-pass direction:

- allow multi-key `criteria` objects only for compatible combinations
- allow `allowed_values` and `disallowed_values` together only when they are non-contradictory
- comparison-oriented criteria such as `minimum`, `maximum`, `equals`, `allowed_values`, and `disallowed_values` implicitly require the subject to be present and usable
- `required: true` means the subject must be successfully extracted and present
- `required: true` does not by itself mean non-empty, non-null, or otherwise valid for deeper structural rules
- if `required: true` appears together with another comparison-oriented criterion, treat it as explicit but redundant rather than invalid
- use `equals: null` for “must be null”
- use `disallowed_values: [null]` for “must not be null”
- do not introduce a dedicated null criterion in the first pass

Examples:

```json
{
  "criteria": {
    "minimum": 80
  }
}
```

```json
{
  "criteria": {
    "minimum": 80,
    "maximum": 90
  }
}
```

```json
{
  "criteria": {
    "allowed_values": ["approved", "complete"],
    "disallowed_values": ["deprecated"]
  }
}
```

```json
{
  "criteria": {
    "equals": null
  }
}
```

### Deferred Criteria Variants

The following variants are intentionally not first-pass input criteria:

- `required_keys`
- `allowed_keys`
- `disallowed_keys`
- `contains_all`
- `contains_any`
- `contains_none`
- `allow_empty`
- `must_be_null`
- `must_be_non_null`
- compound boolean logic
- weighted scoring
- procedural operators
- custom evaluator expressions

Equivalence notes:

- `must_be_null`
  Clean first-pass equivalent:
  - use `equals: null`

- `must_be_non_null`
  Partial approximation:
  - for scalar-style subjects, use `disallowed_values: [null]`

- `contains_none`
  Partial approximation:
  - for a scalar subject, `disallowed_values` expresses the same intent

The remaining deferred variants do not have a clean first-pass equivalent.

## Recommended Test Call Boundary

This proposal now recommends that the test-of-detail receive:

```python
evaluate(evidence, evaluations, metadata)
```

Meaning:

- `evidence`
  The loaded evidence content provided by the evaluator
- `evaluations`
  The caller-owned `evaluations` array for this requested test execution
- `metadata`
  Evaluator-owned execution context

Example:

```python
loaded_evidence_content = ...  # loaded from the provided evidence input

evaluate(
    evidence=loaded_evidence_content,
    evaluations=[
        {
            "subject": {
                "name": "coverage",
                "data_type": "number",
            },
            "criteria": {
                "required": True,
                "minimum": 80,
            },
        }
    ],
    metadata={
        "evidence_type": "json",
        "schema_version": "2",
    },
)
```

Rationale:

- it aligns the test call boundary with the selected caller-owned `evaluations` model
- it keeps evaluator-owned metadata separate from caller-owned evaluation input
- it avoids silently collapsing a caller-provided evaluation array into some other ad hoc structure
- this test call boundary is now an approved direction for the V2 input proposal

## Validation And No-Coercion

The evaluator should validate the caller-owned request packet before calling the test.

This validation should be strict.

The evaluator should reject:

- malformed request structure
- malformed `subject` objects
- unsupported `subject.data_type` values
- malformed `criteria` objects
- unsupported `criteria` keys
- incompatible `subject.data_type` and `criteria` combinations
- ambiguous typed input that would require coercion

No-coercion examples:

- if `subject.data_type` is `number`, `"80"` should not silently coerce to `80`
- if `subject.data_type` is `boolean`, `"true"` should not silently coerce to `true`
- if `subject.data_type` is `date`, `"07/01/2026"` should not silently coerce to `"2026-07-01"`

## Type Invariants, Compatibility Rules, And Examples

This section consolidates:

- type invariants
- compatibility rules
- valid examples
- invalid examples

### Invariants

- `test` must be present
- `evidence` must be present
- `evaluations` must be present and must be an array
- each `evaluations[*]` item must contain exactly:
  - one `subject`
  - one `criteria`
- `subject.name` must be a normalized machine-readable string
- `subject.data_type` must be one of the bounded allowed values
- `criteria` must be an object
- `criteria` must contain at least one supported first-pass key
- multi-key `criteria` objects are allowed only for compatible combinations
- any comparison-oriented criterion implies that the fact must be present and usable, even when `required: true` is omitted

### Compatibility Matrix

| `subject.data_type` | Supported first-pass `criteria` variants |
| --- | --- |
| `text` | `equals`, `allowed_values`, `disallowed_values`, `required` |
| `integer` | `minimum`, `maximum`, `equals`, `allowed_values`, `disallowed_values`, `required` |
| `number` | `minimum`, `maximum`, `equals`, `allowed_values`, `disallowed_values`, `required` |
| `boolean` | `equals`, `allowed_values`, `disallowed_values`, `required` |
| `date` | `minimum`, `maximum`, `equals`, `allowed_values`, `disallowed_values`, `required` |
| `datetime` | `minimum`, `maximum`, `equals`, `allowed_values`, `disallowed_values`, `required` |
| `duration` | `minimum`, `maximum`, `equals`, `allowed_values`, `disallowed_values`, `required` |
| `array` | `equals`, `required` |
| `object` | `equals`, `required` |
| `null` | `equals`, `required` |

Conservative first-pass note:

- `array`, `object`, and `null` intentionally have a narrower first-pass compatibility surface than scalar types such as `text`, `integer`, and `number`
- this proposal does not yet support richer first-pass logic for:
  - array membership rules
  - object key rules
  - emptiness rules
  - structural shape validation
- this keeps the first-pass criteria model bounded and predictable
- for `null`, `required: true` should be read narrowly as “the subject must be successfully extracted and present, and may then be evaluated as null”
- use `required: true` with `null` carefully, because “present with value null” is different from “missing”

### Valid Examples

Numeric threshold:

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
  ]
}
```

Text inclusion:

```json
{
  "test": "./status_check.py",
  "evidence": "./release.json",
  "evaluations": [
    {
      "subject": {
        "name": "release_status",
        "data_type": "text"
      },
      "criteria": {
        "allowed_values": ["approved", "complete"]
      }
    }
  ]
}
```

Null requirement:

```json
{
  "test": "./owner_check.py",
  "evidence": "./release.json",
  "evaluations": [
    {
      "subject": {
        "name": "exception_owner",
        "data_type": "null"
      },
      "criteria": {
        "equals": null
      }
    }
  ]
}
```

### Invalid Examples

Scalar shorthand for `criteria`:

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
      "criteria": 80
    }
  ]
}
```

Invalid because:

- `criteria` must be an object

Unsupported `subject.name` shape:

```json
{
  "subject": {
    "name": "Branch Coverage",
    "data_type": "number"
  }
}
```

Invalid because:

- `subject.name` is not normalized machine-readable `snake_case`

Ambiguous typed input with coercion pressure:

```json
{
  "subject": {
    "name": "coverage",
    "data_type": "number"
  },
  "criteria": {
    "equals": "80"
  }
}
```

Invalid because:

- `"80"` is text, not a number
- the evaluator should reject this instead of silently coercing it

Incompatible criteria combination:

```json
{
  "criteria": {
    "equals": 80,
    "allowed_values": [70, 90]
  }
}
```

Invalid because:

- the criteria combination is contradictory

## Input/Output Alignment

The current V2 direction is that the outer result envelope should echo:

- `test`
- `evidence`
- the full accepted `evaluations` array

This is the current recommended traceability rule for the paired result proposal.

## Follow-Up Dependency On The Result Proposal

The input proposal is now far enough along to establish the caller-owned V2 request shape.

The paired result proposal still needs a follow-up revision to stay aligned on:

- how per-evaluation outcomes are represented when one test receives an `evaluations` array
- how `subject` and `criteria` are echoed or normalized in result packets
- how one test-level execution maps to one or more evaluation-level outcomes in the result model

This is a follow-up dependency, not a reason to keep the input proposal in its earlier `expectation`-based form.

## Remaining Follow-Up Points

The main remaining work after this revision is no longer basic input-shape discovery.

It is:

1. align the paired V2 result proposal to the selected `evaluations` / `subject` / `criteria` model
2. update any user or reference docs that still teach the earlier `expectation`-based proposal language
3. tighten validation details later, after items 1 and 2 above, if implementation-grade precision is needed:
   - exact rejection rules for contradictory multi-key `criteria`
   - whether `allowed_values` / `disallowed_values` element typing must exactly match `subject.data_type`
   - whether `equals` on `array` / `object` means exact structural equality only
4. update test authoring docs to teach `evaluate(evidence, evaluations, metadata)`
5. decide whether later V2 work should add:
   - structured test locators
   - structured evidence locators
   - manifest-style outer request containers
   - richer structural criteria variants

## Current Recommendation

The strongest current recommendation is:

- use `test` + `evidence` + `evaluations` as the V2 caller-owned request shape
- use `subject` and `criteria` as the contract names inside each evaluation item
- define each `evaluations[*]` item as one `subject` plus one object-valued `criteria` packet
- allow that one `criteria` object to contain multiple compatible first-pass criteria keys
- keep the first-pass `subject` object minimal
- keep `criteria` declarative, structured, and object-only rather than procedural
- keep `test` and `evidence` as plain string locators in the first pass
- validate `subject.data_type`, `criteria`, and their compatibility strictly before test execution
- keep evaluator-owned `metadata` outside the caller-owned request packet
- keep richer evaluation logic inside the Python test-of-detail implementation
