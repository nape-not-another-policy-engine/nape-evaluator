# Evidence Format Authoring

This guide shows how to write V2 tests against the evidence families the evaluator currently supports.

Use it when your next question is not "what is the V2 contract?" but instead:

- how do I actually extract facts from XML?
- how should I treat YAML differently from JSON?
- what does a text-line test look like?
- how should I approach PDF evidence when the evaluator only passes extracted text lines?

## Where This Page Fits

Use the V2 authoring guide set in this order:

- use [Authoring Progression](authoring-progression.md) if you need the full beginner-to-hardened teaching path
- use [Scaffold Guide](scaffold.md) if you want the recommended Python file shape
- use [Fact Extraction](fact-extraction.md) for the format-agnostic fact model
- use this page when you need format-specific extraction patterns
- use [Authoring Examples Index](authoring-examples-index.md) when you are ready to copy a fixture

## Document And Fixture Model

The authoring docs and executable examples intentionally use different roles.

The docs under `docs/user/v2-test-authoring/` explain:

- the V2 contract
- the recommended Python structure
- the evaluation-input model
- the format-specific extraction patterns

The executable examples under `tests/` show working copies of those ideas.

The example tree now uses this model:

- `tests/json/`
- `tests/xml/`
- `tests/yaml/`
- `tests/text/`
- `tests/pdf/`

Each format family uses the same basic structure when practical:

- `evidence/`
- `test_of_detail/`
- `test_pattern_library.py`

That split keeps "how the evaluator works" separate from "how an author should copy a test".

## Cross-Format Invariants

The evidence format changes how you extract facts.

It does not change:

- the public test boundary:

```python
def evaluate(evidence, evaluations, metadata):
    ...
```

- the returned result shape:

```python
{
    "conclusion": "true",
    "facts": [],
    "reason": "Reason text",
}
```

- the fact-record shape:

```python
{
    "name": "status",
    "value": "complete",
    "value_type": "text",
    "status": "found",
}
```

- the caller-owned `evaluations[*].subject` / `criteria` model

Across every format, keep the same discipline:

1. validate `metadata["evidence_type"]`
2. validate the runtime evidence shape your test expects
3. extract facts from the evidence
4. determine whether the facts are usable
5. apply caller-owned criteria
6. return `true`, `false`, or `inconclusive`

## JSON

### Runtime Shape

The evaluator passes a parsed Python object from `json.load(...)`.

Most JSON authoring examples use a dictionary root.

### Recommended Extraction Style

Use normal Python dictionary and list access, but keep the nested lookup inside small helpers.

Example:

```python
def _extract_status_fact(evidence):
    status = evidence.get("status")
    return {
        "name": "status",
        "value": status,
        "value_type": "text",
        "status": "found" if status not in (None, "") else "not_found",
    }
```

### Defensive Checks

Start with:

```python
def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "json":
        return _build_inconclusive_result(
            "The evidence metadata does not indicate JSON input."
        )
    if not isinstance(evidence, dict):
        return _build_inconclusive_result(
            "The evidence file is not in the expected JSON format (dictionary)."
        )
    return None
```

### Common Pitfalls

- assuming keys always exist
- mixing raw nested lookups into policy logic
- silently coercing strings into numbers without an explicit parse step

### Copy First

- `tests/json/test_of_detail/verify_author_complete.py`
- `tests/json/test_of_detail/verify_component_coverage_minimum.py`

## XML

### Runtime Shape

The evaluator passes an `xml.etree.ElementTree` root element.

That means your test is working against an element tree, not a Python dictionary.

### Recommended Extraction Style

Keep element navigation inside helpers and return normal fact dictionaries.

Example:

```python
def _extract_status_fact(evidence):
    status_text = evidence.findtext("status")
    status = status_text.strip() if isinstance(status_text, str) else None
    return {
        "name": "status",
        "value": status,
        "value_type": "text",
        "status": "found" if status not in (None, "") else "not_found",
    }
```

### Defensive Checks

Start with:

```python
def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "xml":
        return _build_inconclusive_result("This test expects XML evidence.")
    if getattr(evidence, "tag", None) is None:
        return _build_inconclusive_result(
            "This test expects an XML root element."
        )
    return None
```

### Common Pitfalls

- forgetting that `findtext(...)` can return `None`
- comparing raw whitespace-padded text without trimming it
- assuming namespaces do not exist when your real XML evidence may include them

If your XML uses namespaces, normalize that in one helper instead of scattering namespace literals across the file.

### Copy First

- `tests/xml/test_of_detail/verify_author_complete.py`

### Next Negative / Richer Pattern

Use this next when your XML evidence includes namespaces:

- `tests/xml/test_of_detail/verify_author_complete_namespaced.py`

That example shows one important discipline:

- isolate namespace handling in one helper-level constant instead of scattering namespace literals across the file

## YAML

### Runtime Shape

The evaluator passes the Python object returned by `yaml.safe_load(...)`.

In practice, many YAML examples will feel similar to JSON because the loaded object is often a nested dictionary/list structure.

### Recommended Extraction Style

Use the same helper style you would use for JSON, but remember that YAML can carry implicit scalar typing.

Example:

```python
def _extract_measure_fact(evidence, metric_name):
    measures = evidence.get("component", {}).get("measures", [])
    for measure in measures:
        if measure.get("metric") != metric_name:
            continue
        value = measure.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return {
                "name": metric_name,
                "value": None,
                "value_type": "number",
                "unit": "percent",
                "status": "invalid",
            }
        return {
            "name": metric_name,
            "value": float(value),
            "value_type": "number",
            "unit": "percent",
            "status": "found",
        }
```

### Defensive Checks

Start with:

```python
def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "yaml":
        return _build_inconclusive_result("This test expects YAML evidence.")
    if not isinstance(evidence, dict):
        return _build_inconclusive_result(
            "This test expects YAML evidence as a dictionary."
        )
    return None
```

### Common Pitfalls

- forgetting that YAML may already convert some scalar values for you
- treating booleans as numbers
- assuming every YAML file has the same dictionary root shape

### Copy First

- `tests/yaml/test_of_detail/verify_component_coverage_minimum.py`

### Next Negative / Richer Pattern

Use this next when YAML parsing gives you a present value that is still unusable for the subject data type you need:

- `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`

That example shows:

- a value can be present in evidence and still yield `inconclusive`
- YAML scalar typing does not remove the need for explicit typed-fact validation

## Text

### Runtime Shape

The evaluator passes a list of text lines.

This is used for:

- `.txt`
- files without a recognized extension
- unknown extensions that fall back to text

### Recommended Extraction Style

Search the lines deliberately and keep parsing rules explicit.

Example:

```python
def _extract_status_fact(evidence):
    for line in evidence:
        label, value = _split_label_value(line)
        if label == "status":
            return {
                "name": "status",
                "value": value,
                "value_type": "text",
                "status": "found" if value else "not_found",
            }
    return {
        "name": "status",
        "value": None,
        "value_type": "text",
        "status": "not_found",
    }
```

### Defensive Checks

Start with:

```python
def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "text":
        return _build_inconclusive_result("This test expects text evidence.")
    if not isinstance(evidence, list):
        return _build_inconclusive_result(
            "This test expects text evidence as a list of lines."
        )
    return None
```

### Common Pitfalls

- relying on exact capitalization without normalizing labels
- assuming every line contains a delimiter
- writing one giant parser instead of one helper per pattern

### Copy First

- `tests/text/test_of_detail/verify_author_complete.py`

### Next Negative / Richer Pattern

Use this next when a line-oriented parser finds multiple competing candidate values:

- `tests/text/test_of_detail/verify_author_complete_ambiguous.py`

That example shows:

- ambiguity should usually be treated as failure to establish the fact
- the right result is often `inconclusive`, not `false`

## PDF

### Runtime Shape

The evaluator passes a list of extracted text lines.

The test does not receive a structured PDF object.

From the test author's perspective, PDF is much closer to text than to JSON or XML.

### Recommended Extraction Style

Write the same kind of text-line helpers you would use for `.txt`, but be more defensive about ambiguity.

Example:

```python
def _extract_status_fact(evidence):
    for line in evidence:
        label, value = _split_label_value(line)
        if label == "status":
            return {
                "name": "status",
                "value": value,
                "value_type": "text",
                "status": "found" if value else "not_found",
            }
    return {
        "name": "status",
        "value": None,
        "value_type": "text",
        "status": "not_found",
    }
```

### Defensive Checks

Start with:

```python
def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "pdf":
        return _build_inconclusive_result("This test expects PDF evidence.")
    if not isinstance(evidence, list):
        return _build_inconclusive_result(
            "This test expects PDF evidence as extracted text lines."
        )
    return None
```

### Common Pitfalls

- assuming the PDF text layout will be perfectly stable
- assuming table structure survives text extraction cleanly
- treating missing text as proof that a fact is false instead of proof that the fact could not be established

For PDF-backed tests, default toward `inconclusive` when the needed text cannot be established cleanly.

### Copy First

- `tests/pdf/test_of_detail/verify_author_complete.py`

### Next Negative / Richer Pattern

Use this next when extracted PDF text produces multiple competing candidate values:

- `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`

That example shows:

- PDF-backed tests should be even more conservative than plain text when extraction is ambiguous
- an extracted-text conflict should generally lead to `inconclusive`

### Why The PDF Example Uses A Controlled Test Seam

The evaluator still supports real PDF loading in production.

In the example-suite tests, the PDF pattern example is validated through a controlled extraction seam rather than a heavy binary artifact.

That keeps the public contract stable while avoiding brittle example maintenance dominated by PDF-generation mechanics instead of test authoring.

## External Reference Material

If you need lower-level library details while writing a test, use:

- Python `xml.etree.ElementTree`: https://docs.python.org/3/library/xml.etree.elementtree.html
- PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation
- PyPDF2 text extraction: https://pypdf2.readthedocs.io/en/3.x/user/extract-text.html

## Recommended Next Reading

- [Authoring Examples Index](authoring-examples-index.md)
- [Fact Extraction](fact-extraction.md)
- [Scaffold Guide](scaffold.md)
