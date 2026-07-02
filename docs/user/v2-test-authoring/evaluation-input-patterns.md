# Evaluation Input Patterns

This page is the pattern library for V2 caller-owned evaluation input.

The goal is not just to show a few JSON snippets.

The goal is to give test authors:

- a reusable vocabulary of input shapes
- a way to choose the simplest viable pattern
- executable fixture references for the canonical patterns
- clear boundaries around what is documented now versus what is actually supported in the current runtime

## Recommended Way To Document Patterns

Use a pattern-library approach:

- document-first catalog of pattern types
- executable canonical fixtures for the highest-value current patterns
- clear labels for:
  - canonical now
  - documented later
  - boundary examples

This avoids turning the repo into an uncurated pile of examples.

If you already understand the pattern vocabulary but need help scaling those patterns into more complex test design, use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)

## Pattern Axes

Think about evaluation-input patterns across four axes:

### 1. Comparison Shape

- exact equality
- threshold
- range
- membership
- exclusion
- presence only
- structural equality

### 2. Fact Topology

- one fact
- multiple independent facts
- multiple dependent facts
- derived fact

### 3. Decision Topology

- direct compare
- combined conjunction
- conditional policy
- lookup-table or tiered policy

For guidance on how those later decision topologies should stay test-owned instead of becoming transport complexity, use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)

### 4. Establishment Style

- fail fast
- fail slow

## Canonical Executable Patterns Now

These patterns have executable sample fixtures in `tests/json/test_of_detail/`.

| Pattern | What it demonstrates | Fixture |
| --- | --- | --- |
| text equals | one text fact plus one `equals` criterion | `verify_author_complete.py` |
| number minimum | one numeric fact plus one `minimum` criterion | `verify_component_coverage_minimum.py` |
| numeric range | one numeric fact plus `minimum` and `maximum` in one criteria object | `verify_component_coverage_range.py` |
| boolean equals | one boolean fact plus one `equals` criterion | `verify_feature_flag_enabled.py` |
| allowed values | one text fact plus one `allowed_values` criterion | `verify_release_status_allowed_values.py` |
| disallowed values | one text fact plus one `disallowed_values` criterion | `verify_release_status_disallowed_values.py` |
| object equals | one object fact plus one exact `equals` criterion | `verify_approver_profile_equals.py` |
| array equals | one array fact plus one exact `equals` criterion | `verify_reviewer_roles_equals.py` |
| null equals | one null fact plus one exact `equals` criterion | `verify_revocation_reason_null.py` |
| presence only | one text fact plus `required: true` | `verify_service_owner_required.py` |
| integer range | one integer fact plus `minimum` and `maximum` | `verify_build_age_days_range.py` |
| date range | one date fact plus `minimum` and `maximum` | `verify_review_date_range.py` |
| duration range | one duration fact plus `minimum` and `maximum` | `verify_restore_duration_range.py` |
| datetime minimum | one datetime fact plus one `minimum` criterion | `verify_last_review_timestamp_minimum.py` |
| datetime range | one datetime fact plus `minimum` and `maximum` | `verify_last_review_timestamp_range.py` |
| derived fact maximum | one derived numeric fact computed from two raw evidence facts plus one `maximum` criterion | `verify_coverage_gap_maximum.py` |
| multi-subject conjunction | two numeric facts, two criteria objects, one combined result | `verify_dual_coverage_thresholds.py` |
| multi-subject fail fast | two numeric facts, two criteria objects, and first-missing-fact establishment | `verify_dual_coverage_fail_fast.py` |

## Canonical Pattern Matrix

| Pattern | Subjects | Data type | Criteria keys | Decision topology | Establishment style |
| --- | --- | --- | --- | --- | --- |
| text equals | 1 | `text` | `equals` | direct compare | fail fast |
| number minimum | 1 | `number` | `minimum` | direct compare | fail fast |
| numeric range | 1 | `number` | `minimum`, `maximum` | direct compare | fail fast |
| boolean equals | 1 | `boolean` | `equals` | direct compare | fail fast |
| allowed values | 1 | `text` | `allowed_values` | direct compare | fail fast |
| disallowed values | 1 | `text` | `disallowed_values` | direct compare | fail fast |
| object equals | 1 | `object` | `equals` | direct compare | fail fast |
| array equals | 1 | `array` | `equals` | direct compare | fail fast |
| null equals | 1 | `null` | `equals` | direct compare | fail fast |
| presence only | 1 | `text` | `required` | presence check | fail fast |
| integer range | 1 | `integer` | `minimum`, `maximum` | direct compare | fail fast |
| date range | 1 | `date` | `minimum`, `maximum` | direct compare | fail fast |
| duration range | 1 | `duration` | `minimum`, `maximum` | direct compare | fail fast |
| datetime minimum | 1 | `datetime` | `minimum` | direct compare | fail fast |
| datetime range | 1 | `datetime` | `minimum`, `maximum` | direct compare | fail fast |
| derived fact maximum | 1 derived from 2 raw facts | `number` | `maximum` | direct compare | fail slow |
| multi-subject conjunction | 2 | `number`, `number` | `minimum`, `minimum` | combined conjunction | fail slow |
| multi-subject fail fast | 2 | `number`, `number` | `minimum`, `minimum` | combined conjunction | fail fast |

## Canonical Patterns

### 1. Text Equals

Use when one extracted text fact must match one expected text value.

```json
{
  "subject": {
    "name": "status",
    "data_type": "text"
  },
  "criteria": {
    "equals": "complete"
  }
}
```

Why it matters:

- simplest dynamic replacement for hardcoded expected text
- best starter pattern for showing that caller input changes the result without changing the Python test

### 2. Number Minimum

Use when one extracted numeric fact must meet one minimum threshold.

```json
{
  "subject": {
    "name": "coverage",
    "data_type": "number"
  },
  "criteria": {
    "minimum": 80
  }
}
```

Why it matters:

- simplest threshold pattern
- common for assurance thresholds, tolerance floors, and maturity gates

### 3. Numeric Range

Use when one numeric fact must fall inside an allowed interval.

```json
{
  "subject": {
    "name": "coverage",
    "data_type": "number"
  },
  "criteria": {
    "minimum": 80,
    "maximum": 90
  }
}
```

Why it matters:

- shows that one `criteria` object can carry multiple compatible first-pass keys
- good model for tolerance bands and age windows

### 4. Boolean Equals

Use when a fact is a binary condition such as enabled or disabled.

```json
{
  "subject": {
    "name": "feature_enabled",
    "data_type": "boolean"
  },
  "criteria": {
    "equals": true
  }
}
```

Why it matters:

- common for control-state checks
- easy for authors to understand and test

### 5. Allowed Values

Use when a text fact must be one of a caller-declared set.

```json
{
  "subject": {
    "name": "release_status",
    "data_type": "text"
  },
  "criteria": {
    "allowed_values": ["approved", "complete"]
  }
}
```

Why it matters:

- useful when acceptable states change over time
- better than hardcoding several string comparisons in the Python test

### 6. Presence Only

Use when the main question is whether a fact exists and is usable, not whether it matches a value.

```json
{
  "subject": {
    "name": "service_owner",
    "data_type": "text"
  },
  "criteria": {
    "required": true
  }
}
```

Why it matters:

- good first example of a fact-establishment check
- useful for owner, approver, timestamp, or identifier presence

### 7. Disallowed Values

Use when a text fact must not be one of a caller-declared set.

```json
{
  "subject": {
    "name": "release_status",
    "data_type": "text"
  },
  "criteria": {
    "disallowed_values": ["deprecated", "rejected"]
  }
}
```

Why it matters:

- useful for banned states, revoked states, or prohibited business statuses
- complements `allowed_values` with the inverse pattern

### 8. Datetime Minimum

Use when a timestamp fact must be at or after a caller-provided lower bound.

```json
{
  "subject": {
    "name": "last_review_timestamp",
    "data_type": "datetime"
  },
  "criteria": {
    "minimum": "2026-07-01T00:00:00Z"
  }
}
```

Why it matters:

- common for recency requirements
- good first temporal example without introducing more complex date math into the input model

### 9. Datetime Range

Use when a timestamp fact must fall inside an allowed window.

```json
{
  "subject": {
    "name": "last_review_timestamp",
    "data_type": "datetime"
  },
  "criteria": {
    "minimum": "2026-06-01T00:00:00Z",
    "maximum": "2026-06-30T23:59:59Z"
  }
}
```

Why it matters:

- completes the temporal family beyond the minimum-only example
- useful for approval windows, review windows, and freshness windows

### 10. Integer Range

Use when an integer fact must fall inside an allowed interval.

```json
{
  "subject": {
    "name": "build_age_days",
    "data_type": "integer"
  },
  "criteria": {
    "minimum": 0,
    "maximum": 30
  }
}
```

Why it matters:

- useful for age-in-days, count, or quantity bounds
- gives a cleaner integer example than reusing floating-point coverage metrics

### 11. Date Range

Use when a date fact must fall inside an allowed calendar window.

```json
{
  "subject": {
    "name": "review_date",
    "data_type": "date"
  },
  "criteria": {
    "minimum": "2026-06-01",
    "maximum": "2026-06-30"
  }
}
```

Why it matters:

- useful for review windows, approval dates, and cutoff dates
- shows that tests should parse and compare typed dates rather than assume string comparison is sufficient

### 12. Duration Range

Use when a duration fact must fall inside an allowed time span.

```json
{
  "subject": {
    "name": "restore_duration",
    "data_type": "duration"
  },
  "criteria": {
    "minimum": "PT10M",
    "maximum": "PT60M"
  }
}
```

Why it matters:

- useful for restore times, SLA windows, and completion-time checks
- shows that tests should parse and compare durations as durations, not as raw text

### 13. Object Equals

Use when a fact is a small structured object and the caller wants exact structural equality.

```json
{
  "subject": {
    "name": "approver_profile",
    "data_type": "object"
  },
  "criteria": {
    "equals": {
      "id": "manager-123",
      "department": "security"
    }
  }
}
```

Why it matters:

- useful for small nested records
- demonstrates that object equality is exact structural equality, not partial matching

### 14. Array Equals

Use when a fact is an ordered list and the caller wants exact list equality.

```json
{
  "subject": {
    "name": "reviewer_roles",
    "data_type": "array"
  },
  "criteria": {
    "equals": ["manager", "security"]
  }
}
```

Why it matters:

- useful for simple reviewer lists, role lists, or ordered steps
- demonstrates that array equality is exact rather than set-like

### 15. Null Equals

Use when the caller explicitly expects a fact to be present with a null value.

```json
{
  "subject": {
    "name": "revocation_reason",
    "data_type": "null"
  },
  "criteria": {
    "equals": null
  }
}
```

Why it matters:

- helps authors distinguish:
  - not found
  - found but invalid
  - found and explicitly null

### 16. Multi-Subject Conjunction

Use when one final conclusion depends on more than one extracted fact and each fact has its own criterion.

```json
[
  {
    "subject": {
      "name": "coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 80
    }
  },
  {
    "subject": {
      "name": "branch_coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 95
    }
  }
]
```

Why it matters:

- shows that one test can combine several caller-provided criteria values into one final result
- good first multi-fact pattern before moving into richer conditional policy logic

### 17. Multi-Subject Fail Fast

Use when one final conclusion depends on several facts, but you want the test to stop at the first fact-establishment failure.

Why it matters:

- gives a concrete contrast with the fail-slow multi-subject example
- helps authors choose the simpler establishment strategy first

### 18. Derived Fact Maximum

Use when the evaluated fact is not read directly from evidence, but is derived inside the test from other evidence facts and then compared against one caller-provided threshold.

```json
[
  {
    "subject": {
      "name": "coverage_gap",
      "data_type": "number"
    },
    "criteria": {
      "maximum": 15
    }
  }
]
```

Why it matters:

- shows that caller-owned input can still stay simple even when the evaluated fact is computed inside the Python test
- demonstrates that derived facts should be named explicitly instead of hiding the derivation inside an unnamed policy branch
- provides a canonical example of a fact topology that is richer than one directly extracted value but still simpler than conditional policy input

## Documented Later

These patterns are useful and should stay in the library, but they do not need to be executable first.

## Boundary And Non-Canonical Examples

These patterns are real possibilities, but they should be treated carefully because they either have a narrow compatibility surface or imply richer policy semantics.

### Conditional Coverage Policy

This is the kind of long-tail policy authors often want:

- if branch coverage is below a split, require a stricter coverage minimum
- otherwise allow a looser coverage minimum

This is a useful documentation pattern, but it is not a first executable canonical fixture in the current runtime because the current request-builder criteria surface is intentionally bounded to:

- `minimum`
- `maximum`
- `equals`
- `allowed_values`
- `disallowed_values`
- `required`

So for now:

- keep conditional policy in docs and planning guidance
- use multi-subject conjunction as the executable stepping stone

### Array, Object, And Null

These remain valid first-pass data types, but they should still be used conservatively:

- they depend on exact structural equality
- they do not yet carry richer element-shape semantics
- they are usually better as later-stage patterns rather than the first pattern an author copies

## Presence Rule

- comparison-oriented criteria such as `minimum`, `maximum`, `equals`, `allowed_values`, and `disallowed_values` already imply that the fact must be present and usable
- use `required: true` mainly for presence-only checks
- if `required: true` appears together with another comparison-oriented criterion, treat it as explicit but redundant rather than invalid

## Recommendation

If you are deciding what to build first:

1. start with `text equals`
2. then add `number minimum`
3. then add `presence only`
4. then add one multi-subject conjunction example
5. only then move into richer policy logic

That sequence gives authors a clear path from simple, hardcoded tests toward input-driven and defensive test-of-detail files.
