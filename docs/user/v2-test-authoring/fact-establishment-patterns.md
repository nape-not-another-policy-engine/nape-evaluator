# Fact Establishment Patterns

After extraction, the test has to decide whether enough usable facts exist to perform the evaluation.

This page compares two common patterns:

- fail fast
- fail slow

Neither pattern is universally correct.

## Fail Fast

Fail fast means:

- stop as soon as one required fact cannot be established
- return `inconclusive` immediately

Example shape:

```python
coverage_fact = _extract_coverage_fact(evidence)
if coverage_fact["status"] != "found":
    return _build_inconclusive_result(
        facts=[coverage_fact],
        reason="Unable to evaluate because the coverage fact could not be established.",
    )
```

Use fail fast when:

- the policy is simple
- one missing fact already makes the rest of the work irrelevant
- you want the easiest starting implementation
- the extraction steps are expensive or deeply dependent on one prerequisite fact

Tradeoffs:

- simpler control flow
- less diagnostic detail when several facts are missing

## Fail Slow

Fail slow means:

- attempt to establish all relevant facts first
- then decide whether enough usable facts exist to evaluate
- if not, return `inconclusive` with the full set of established and unestablished facts

Example shape:

```python
facts = {
    "coverage": _extract_coverage_fact(evidence),
    "branch_coverage": _extract_branch_coverage_fact(evidence),
}

missing_or_invalid = [
    fact for fact in facts.values()
    if fact["status"] != "found"
]

if missing_or_invalid:
    return _build_inconclusive_result(
        facts=list(facts.values()),
        reason="Unable to evaluate because one or more required facts could not be established.",
    )
```

Use fail slow when:

- better diagnostics matter
- the policy depends on several facts
- you want to show which facts were found and which were not
- one missing fact does not prevent you from extracting others cleanly

Tradeoffs:

- better `inconclusive` explanations
- slightly more code and more state to manage

## Recommendation

Do not force one universal default.

Instead:

- discuss both patterns in docs and scaffolds
- let authors choose based on the policy shape

Practical starting advice:

If you are unsure where to start, or you need to get started simply, start fail fast first, then grow your way into fail slow.
