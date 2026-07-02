# Scaffold Guide

This page explains the recommended structure for a V2 test-of-detail file.

Use the template at:

- [templates/v2_test_of_detail_scaffold.py](templates/v2_test_of_detail_scaffold.py)

## Recommended Shape

Use:

- one public `evaluate(evidence, evaluations, metadata)` function
- a small number of private helpers
- a standard fact dict shape
- one combined returned `result`

## Recommended Flow

1. Validate the evaluator-owned metadata that your test depends on.
2. Index or normalize the caller-owned `evaluations` input into a lookup that your test can use.
3. Extract facts from the evidence.
4. Determine which facts are missing or invalid.
5. If the missing/invalid fact situation prevents evaluation, return `inconclusive`.
6. Otherwise, evaluate the policy logic using the extracted facts and caller-supplied criteria values.
7. Return one combined structured result object.

## Incremental Authoring Order

Do not try to write the final scaffolded test in one pass.

Write it in this order:

1. write the public `evaluate(evidence, evaluations, metadata)` function
2. add `_validate_metadata(...)`
3. add `_index_evaluations(...)`
4. add one extraction helper for one fact
5. add one policy check for one criterion
6. add missing/invalid fact handling
7. only then:
   - add a second subject
   - add typed parsing
   - add structural comparisons
   - add derived facts

This keeps the file understandable while it grows.

## Minimal Layered Shape

Use this as the Python writing order:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    facts = _extract_facts(evidence, evaluation_index)

    blocking_result = _handle_unestablished_facts(facts, evaluation_index)
    if blocking_result is not None:
        return blocking_result

    return _evaluate_policy(facts, evaluation_index)
```

Then grow the file one responsibility at a time instead of filling all helpers immediately.

## Why This Structure

- It keeps evaluator-owned validation separate from test-owned domain logic.
- It prevents a 200-line `evaluate(...)` function.
- It makes extraction, establishment, and evaluation easier to test in isolation.

## Default Scaffold Recommendation

If you are building a scaffold by default, include:

- metadata validation
- evaluation indexing
- fact extraction helper
- missing/invalid fact helper
- policy evaluation helper
- standard result builders

Do not hide all logic behind abstractions that make simple tests harder to read.

The goal is a readable default, not a framework.

If your test has outgrown the default one-subject or one-pattern shape and you need guidance on scaling logic rather than just structuring files, use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)
