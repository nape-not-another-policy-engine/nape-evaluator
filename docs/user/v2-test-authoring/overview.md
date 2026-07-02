# V2 Authoring Overview

This guide describes the current V2 authoring model for test-of-detail files.

## Current Boundary

The current test boundary is:

```python
def evaluate(evidence, evaluations, metadata):
    ...
```

The current test return shape is one combined structured result:

```python
{
    "conclusion": "true",
    "facts": [
        {
            "name": "coverage",
            "value": 85.0,
            "value_type": "number",
            "unit": "percent",
            "status": "found",
        }
    ],
    "reason": "Coverage is 85.0%, which meets the required threshold.",
}
```

## Responsibility Split

The current split is:

- Evaluator-owned defensive validation:
  - outer request shape
  - `evaluations[*]` structure
  - supported `subject.data_type`
  - supported `criteria` keys
  - basic compatibility and no-coercion rules
- Test-owned defensive validation:
  - expected `metadata["evidence_type"]`
  - expected schema/version assumptions
  - whether the evidence contains extractable facts
  - whether the extracted facts are usable for the test logic
  - final policy evaluation
  - final `inconclusive` / `true` / `false` reasoning

## Standard Fact Shape

Use one standard in-memory fact dict shape in examples and scaffolds:

```python
{
    "name": "coverage",
    "value": 85.0,
    "value_type": "number",
    "unit": "percent",
    "status": "found",
}
```

Required keys:

- `name`
- `value`
- `value_type`
- `status`

Optional keys:

- `unit`

Recommended fact statuses:

- `found`
- `not_found`
- `invalid`

## Recommended Internal Breakout

Keep one public `evaluate(...)` function, but break the work into private helpers.

Recommended shape:

- `_validate_metadata(...)`
- `_index_evaluations(...)`
- `_extract_facts(...)`
- `_find_missing_or_invalid_facts(...)`
- `_evaluate_policy(...)`
- `_build_inconclusive_result(...)`

This keeps the public entry point small and lets extraction and evaluation logic evolve independently.
