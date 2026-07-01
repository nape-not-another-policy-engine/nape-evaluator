# Test-Of-Detail Authoring

A test-of-detail file is a Python file loaded by `nape-eval`.

## Required Function

Define:

```python
def evaluate(evidence, test_parameters, metadata):
    return "pass", "Reason text"
```

The function must return two values:

- `outcome`
- `reason`

## Test Composition

A test-of-detail is usually composed of:

- optional imports needed by the test logic
- one `evaluate(evidence, test_parameters, metadata)` function
- evidence field extraction
- decision logic that maps evidence to `pass`, `fail`, `inconclusive`, or `error`
- one human-readable reason string returned with the outcome
- optional caller-owned parameter checks against `test_parameters`

Small example:

```python
def evaluate(evidence, test_parameters, metadata):
    if metadata.get("evidence_type") != "json":
        return "error", "The evidence metadata does not indicate JSON input."

    status = evidence.get("status")
    if status == "complete":
        return "pass", "The author has achieved the status of complete."
    if status in (None, ""):
        return "inconclusive", "The expected data field 'status' does not contain a value."
    return "fail", f"The author has not achieved the status of complete, their current status is '{status}'."
```

## Evidence Input

The evaluator passes evidence into `evaluate(evidence, test_parameters, metadata)` based on the evidence file extension:

- JSON: Python object from `json.load`
- XML: `xml.etree.ElementTree` root element
- YAML: Python object from `yaml.safe_load`
- PDF: extracted text lines
- TXT or unknown: text lines

Example JSON input:

```python
{
    "author": "Bill Bensing",
    "status": "complete",
}
```

If the evidence is JSON, read it directly as a Python object:

```python
def evaluate(evidence, test_parameters, metadata):
    if evidence.get("status") == "complete":
        return "pass", "Status is complete."
    return "fail", "Status is not complete."
```

The metadata object currently contains the third evaluator-supplied argument:

- `metadata["evidence_type"]`
- `metadata["schema_version"]`

## Test Parameters Input

The evaluator always passes `test_parameters` as a dict.

Current rules:

- if no caller-supplied parameters were provided, `test_parameters` is `{}`
- if caller-supplied parameters were provided, they come from a top-level JSON object
- direct CLI usage binds parameter files through repeated `--test-parameters-file` arguments matched by position to repeated `--test` arguments

Example parameter file:

```json
{
  "minCoverage": 80
}
```

Example test:

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

## Defensive Programming With Metadata

Use `metadata` to reject inputs your test was not written to evaluate.

Example:

```python
def evaluate(evidence, test_parameters, metadata):
    if metadata.get("evidence_type") != "json":
        return "error", "This test expects JSON evidence."

    if metadata.get("schema_version") != "2":
        return "error", "This test only supports evaluator schema version 2."

    status = evidence.get("status")
    if status == "complete":
        return "pass", "Status is complete."
    if status in (None, ""):
        return "inconclusive", "The expected data field 'status' does not contain a value."
    return "fail", f"Status is {status}."
```

This is the intended place to handle expected contract mismatches, such as:

- wrong evidence type
- unsupported schema version
- missing required fields
- evidence shape that the test knows how to recognize and reject

Use `test_parameters` the same way for caller-owned expectations:

- missing required parameter keys
- wrong parameter type for a known key
- known out-of-range or unsupported parameter values

Return result-level `error` when the test understands the mismatch and can explain it clearly.

## Exception Handling Guidance

Prefer returning `error` only for expected, domain-known failures that your test understands and wants to explain clearly.

Examples:

- unsupported `metadata["evidence_type"]`
- unsupported `metadata["schema_version"]`
- known missing structure in the evidence payload
- missing or malformed required `test_parameters`

Do not add broad `except Exception` wrappers unless you are converting a very specific failure into a better domain message.

The evaluator process boundary already catches unhandled exceptions and converts them into evaluator output:

- the failing invocation still produces a result item with `executed: false`
- the failure is reported in `evaluator.messages`
- the failure increments `evaluator.summary.message_error`

That means the CLI contract stays stable even when a test raises unexpectedly, but test authors should not assume every failure becomes a returned `("error", "reason")` tuple.

## Recommended Outcome Use

Use `pass` when the evidence satisfies the test.

Use `fail` when the evidence is present and valid but does not satisfy the test.

Use `inconclusive` when the evidence is missing expected fields or cannot support a decision.

Use `error` when the test itself cannot run as intended.

Use returned `error` for contract-aware, intentional test decisions such as:

- unsupported `metadata["evidence_type"]`
- unsupported `metadata["schema_version"]`
- evidence that is present but shaped in a way the test explicitly recognizes as unusable

If a test returns any unsupported outcome value, the evaluator converts that result to `error` and reports that the returned outcome was unsupported.

Do not rely on uncaught exceptions as a substitute for returned `error`, because the evaluator records those as operational failures rather than test result outcomes.

## Authoring Rules

- Keep tests deterministic.
- Return a concise human-readable reason.
- Do not print extra output from the test file.
- Do not depend on local machine state unless that state is part of the evidence.
- Handle missing fields explicitly.
- Use `metadata` for expected contract checks before deeper evidence access.
- Use `test_parameters` for explicit caller-owned validation before applying business rules.
- Let unexpected execution errors propagate unless you are intentionally converting a known failure into a clearer `error` reason.
- Treat test files as executable code; do not publish or run tests that perform unrelated filesystem, network, credential, or destructive operations.

## Historical Note

The V1 baseline passed every evidence file as text lines. Tests written for that older contract may need migration if they parse structured content inside `evaluate(...)`.

The current CLI runs one evidence file against one or more test-of-detail files per invocation, with optional repeated `--test-parameters-file` inputs for caller-owned parameterization.
