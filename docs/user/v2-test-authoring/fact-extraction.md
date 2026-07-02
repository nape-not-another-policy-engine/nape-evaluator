# Fact Extraction

Fact extraction is the step where the Python test reads the already-loaded evidence and produces the fact records it will later use for evaluation.

This page defines the format-agnostic fact model.

If you need the concrete extraction style for JSON, XML, YAML, text, or PDF evidence, use [Evidence Format Authoring](evidence-format-authoring.md) alongside this page.

## Extraction Goal

The goal is not to decide `true` or `false` immediately.

The goal is to establish a fact record for each subject the test cares about, including whether the fact was:

- found
- not found
- present but invalid for the required type

## Recommended Extraction Output

Use a dictionary keyed by fact name while extracting:

```python
{
    "coverage": {
        "name": "coverage",
        "value": 85.0,
        "value_type": "number",
        "unit": "percent",
        "status": "found",
    }
}
```

This makes it easy to:

- look up facts by subject name
- report which facts were not established
- build a final ordered `facts` array for the returned result

## Recommended Extraction Rules

- extract facts from `evidence`, not from caller-owned `evaluations`
- use `evaluations` to determine what subjects and criteria matter
- build one fact record per subject that the test is responsible for
- do not silently coerce extracted values into a different semantic type

## Example: Numeric Fact

```python
def _extract_coverage_fact(evidence):
    measures = evidence.get("component", {}).get("measures", [])
    for measure in measures:
        if measure.get("metric") == "coverage":
            raw_value = measure.get("value")
            if not isinstance(raw_value, (int, float, str)):
                return {
                    "name": "coverage",
                    "value": None,
                    "value_type": "number",
                    "unit": "percent",
                    "status": "invalid",
                }

            try:
                numeric_value = float(raw_value)
            except (TypeError, ValueError):
                return {
                    "name": "coverage",
                    "value": None,
                    "value_type": "number",
                    "unit": "percent",
                    "status": "invalid",
                }

            return {
                "name": "coverage",
                "value": numeric_value,
                "value_type": "number",
                "unit": "percent",
                "status": "found",
            }

    return {
        "name": "coverage",
        "value": None,
        "value_type": "number",
        "unit": "percent",
        "status": "not_found",
    }
```

## Extraction Guidance

- prefer explicit extraction helpers over inline nested lookups everywhere
- if a fact has nontrivial parsing rules, give it its own helper
- if multiple facts depend on the same evidence region, factor that region lookup once

## Format Reminder

The fact shape stays the same across evidence families.

What changes by format is the extraction helper implementation:

- JSON and YAML usually extract from dictionary/list structures
- XML extracts from an element tree
- text and PDF extract from line-oriented text

Use one helper layer to absorb that difference so your later evaluation logic stays stable.

## Ordering Guidance

When returning the final `facts` array:

- keep the order stable
- prefer the same order as the caller-owned `evaluations` array unless there is a strong reason not to
