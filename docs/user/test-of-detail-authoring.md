# Test-Of-Detail Authoring

A test-of-detail file is a trusted Python file loaded by `nape-eval`.

This guide describes the current committed V2 authoring contract.

## Required Function

Define:

```python
def evaluate(evidence, evaluations, metadata):
    return {
        "conclusion": "true",
        "facts": [],
        "reason": "Reason text",
    }
```

The function must return one object with:

- `conclusion`
- `facts`
- `reason`

Accepted `conclusion` values are:

- `true`
- `false`
- `inconclusive`

## Authoring Model

A test-of-detail usually includes:

- optional imports needed by the test logic
- one public `evaluate(evidence, evaluations, metadata)` function
- evidence-field extraction
- fact establishment
- policy logic that uses caller-owned `evaluations`
- one combined returned result object

Small example:

```python
def evaluate(evidence, evaluations, metadata):
    if metadata.get("evidence_type") != "json":
        return {
            "conclusion": "inconclusive",
            "facts": [],
            "reason": "This test expects JSON evidence.",
        }

    evaluation_by_name = {
        item["subject"]["name"]: item
        for item in evaluations
    }
    status_rules = evaluation_by_name["status"]["criteria"]
    expected_status = status_rules["equals"]

    status = evidence.get("status")
    fact = {
        "name": "status",
        "value": status,
        "value_type": "text",
        "status": "found" if status not in (None, "") else "not_found",
    }

    if fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [fact],
            "reason": "The expected data field 'status' does not contain a value.",
        }

    if status == expected_status:
        return {
            "conclusion": "true",
            "facts": [fact],
            "reason": "Status matches the expected value.",
        }

    return {
        "conclusion": "false",
        "facts": [fact],
        "reason": f"Status is '{status}', not '{expected_status}'.",
    }
```

## Evidence Input

The evaluator passes evidence into `evaluate(evidence, evaluations, metadata)` based on file extension:

- JSON: Python object from `json.load`
- XML: `xml.etree.ElementTree` root element
- YAML: Python object from `yaml.safe_load`
- PDF: extracted text lines
- TXT or unknown: text lines

The metadata object currently includes:

- `metadata["evidence_type"]`
- `metadata["schema_version"]`

Use `metadata` to reject inputs your test was not written to evaluate.

## Evaluation Input

The evaluator validates the outer request before test execution and then passes `evaluations` as an array of accepted caller-owned evaluation items.

Example:

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
  }
]
```

Current first-pass `subject.data_type` values are:

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

Current first-pass `criteria` keys are:

- `minimum`
- `maximum`
- `equals`
- `allowed_values`
- `disallowed_values`
- `required`

The evaluator rejects unsupported shapes and incompatible type/criteria combinations before your test runs.

## Fact Records

Use a stable fact shape in returned results:

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

Recommended statuses:

- `found`
- `not_found`
- `invalid`

## Defensive Programming

Evaluator-owned validation already checks:

- top-level request shape
- each invocation `test` plus `evaluations`
- `subject.name`
- `subject.data_type`
- `criteria` object shape
- basic type compatibility and no-coercion rules

Your test should still validate:

- expected `metadata["evidence_type"]`
- expected `metadata["schema_version"]`
- whether the evidence contains extractable facts
- whether extracted facts are usable for the test logic

Use `inconclusive` when:

- you cannot establish the facts needed to reach a decision
- the test cannot complete its own intended evaluation path cleanly
- you need to explain a test-known problem without claiming `true` or `false`

## Exception Handling

Prefer returning structured `inconclusive` for expected test-known failures.

Do not add broad `except Exception` wrappers unless you are intentionally converting a specific failure into a better domain message.

If your test raises unexpectedly:

- the evaluator blocks that invocation
- `results[*].execution.executed` becomes `false`
- `results[*].result.conclusion` becomes `inconclusive`
- `results[*].result.reason` is evaluator-generated blocked-result reasoning
- the failure is reported through `evaluator.messages`

That is different from returning `{"conclusion": "inconclusive", ...}` from a completed test you intentionally handled yourself.

## Authoring Rules

- Keep tests deterministic.
- Return a concise human-readable `reason`.
- Do not print extra output from the test file.
- Do not depend on local machine state unless that state is part of the evidence.
- Handle missing facts explicitly.
- Keep evaluator-owned validation concerns separate from test-owned extraction and policy logic.
- Treat test files as executable code; do not publish or run tests that perform unrelated filesystem, network, credential, or destructive operations.

## Recommended Next Reading

Continue in [V2 Test Authoring](v2-test-authoring/README.md).

Use this route based on what you need next:

- for the step-by-step beginner path, go to [Authoring Progression](v2-test-authoring/authoring-progression.md)
- for the recommended Python structure, go to [Scaffold Guide](v2-test-authoring/scaffold.md)
- for format-specific extraction against JSON, XML, YAML, text, or PDF evidence, go to [Evidence Format Authoring](v2-test-authoring/evidence-format-authoring.md)
- for fixture selection by difficulty or domain, go to [Authoring Examples Index](v2-test-authoring/authoring-examples-index.md)
- for fact extraction and establishment guidance, go to [Fact Extraction](v2-test-authoring/fact-extraction.md) and [Fact Establishment Patterns](v2-test-authoring/fact-establishment-patterns.md)
- for richer typed, structural, multi-subject, or derived-fact logic, go to [Advanced Authoring Patterns](v2-test-authoring/advanced-authoring-patterns.md)

## Historical Note

The V1 baseline used tuple-returning `evaluate(...)` functions and older `--test` transport. Use `../product/v1-evaluator-baseline.md` only for migration comparison.
