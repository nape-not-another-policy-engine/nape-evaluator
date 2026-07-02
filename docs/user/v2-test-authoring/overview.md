# V2 Authoring Overview

This guide describes the current V2 authoring model for test-of-detail files.

Use this page to orient yourself before choosing the deeper authoring docs.

## Quick Routes

Use this folder based on the question you are trying to answer:

| If your question is... | Go here |
| --- | --- |
| how do I get a first working test written, step by step? | [Authoring Progression](authoring-progression.md) |
| what Python shape should I scaffold around? | [Scaffold Guide](scaffold.md) |
| how should I extract facts from evidence? | [Fact Extraction](fact-extraction.md) |
| how do I write extraction helpers for JSON, XML, YAML, text, or PDF evidence? | [Evidence Format Authoring](evidence-format-authoring.md) |
| should I fail fast or fail slow when facts cannot be established? | [Fact Establishment Patterns](fact-establishment-patterns.md) |
| what `subject` / `criteria` input shape should I use? | [Evaluation Input Patterns](evaluation-input-patterns.md) |
| which executable fixture should I copy first? | [Authoring Examples Index](authoring-examples-index.md) |
| how do I scale into typed, structural, multi-subject, or derived-fact tests? | [Advanced Authoring Patterns](advanced-authoring-patterns.md) |
| what assurance domains are good starter anchors? | [Domain Examples](domain-examples.md) |

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

If you want the tutorial path rather than the summary, continue with:

- [Authoring Progression](authoring-progression.md)

If you already understand the public boundary and now need format-specific extraction guidance, continue with:

- [Evidence Format Authoring](evidence-format-authoring.md)
