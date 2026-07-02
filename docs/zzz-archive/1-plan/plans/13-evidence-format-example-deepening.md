> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 13: Evidence Format Example Deepening

## Purpose

Deepen the format-specific example library so it teaches not only happy-path extraction, but also the bounded failure and ambiguity paths authors will face in real evidence.

This plan builds directly on the landed first-wave format guidance and examples.

## Why This Exists

The current format guide set now shows:

- what runtime shape each supported evidence family receives
- how to validate `metadata["evidence_type"]`
- how to extract representative facts
- one first-wave executable example for JSON, XML, YAML, text, and PDF

What it does not yet show with enough depth is:

- XML namespace handling
- YAML scalar-typing surprises and invalid typed-fact handling
- text parsing ambiguity and the line between `false` and `inconclusive`
- PDF extraction ambiguity and when to stop claiming a fact can be established
- domain-richer patterns that feel closer to real assurance evidence

## Guardrails

- keep the current V2 evaluator boundary unchanged
- keep the current `evaluations[*].subject` / `criteria` model unchanged
- keep examples focused on fact verification, not transport-side policy expansion
- prefer explicit `inconclusive` reasoning when evidence cannot establish the fact cleanly
- keep tests readable; avoid giant public-interface tests that mix many concerns

## Selected Direction

Add a second wave of examples and guidance centered on five areas:

1. XML namespace-aware extraction
2. YAML type-surprise and invalid typed-fact handling
3. text parsing ambiguity handling
4. PDF ambiguity handling
5. a small domain index that ties the examples back to assurance-style use cases

## Proposed Deliverables

### 1. XML namespace example

Add:

- namespace-aware XML evidence
- one test-of-detail fixture that normalizes namespace usage in one helper
- one proving test that confirms caller-owned input still drives the outcome

### 2. YAML typed negative path

Add:

- YAML evidence that causes one extracted fact to be present but invalid for the selected subject data type
- one fixture that returns `inconclusive` with explicit fact status and reasoning
- one proving test for that path

### 3. Text ambiguity example

Add:

- text evidence where the parser finds competing or ambiguous candidate values
- one fixture that treats ambiguity as inability to establish the fact
- one proving test that confirms the result is `inconclusive`, not `false`

### 4. PDF ambiguity example

Add:

- a PDF-backed controlled extraction example that simulates ambiguous extracted lines
- one fixture or fixture extension that shows the correct defensive response
- one focused proving test around that ambiguity

### 5. Domain index / routing update

Update the user docs so readers can find examples by:

- evidence format
- failure mode
- assurance-style domain feel

## Test Strategy

Use the same structure selected in Plan 12:

- format-specific example directories stay under `tests/<format>/`
- each example proves that caller-owned `evaluations` are actually consumed
- negative-path examples should stay small and isolated

Prefer:

- one proving test per new example pattern
- shared helpers only where they improve clarity

## Work Steps

1. add the active plan and handoff
2. audit the current format example library for the most natural insertion points
3. add XML namespace example
4. add YAML typed negative-path example
5. add text ambiguity example
6. add PDF ambiguity example
7. update the authoring docs and example index
8. run targeted tests, full unit tests, and docs smoke
9. closure-review whether the example library now covers the key real-world ambiguity paths

## Open Questions

None are blocking at plan start.

The selected direction is already constrained enough to execute without reopening the evaluator contract.

## Completion Snapshot

This plan is complete.

Landed outcomes:

- XML now has a namespace-aware example:
  - `tests/xml/test_of_detail/verify_author_complete_namespaced.py`
- YAML now has an invalid typed-fact example that returns `inconclusive`:
  - `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`
- text now has an ambiguity example that returns `inconclusive` when two competing values appear:
  - `tests/text/test_of_detail/verify_author_complete_ambiguous.py`
- PDF now has a matching ambiguity example proven through the controlled extraction seam:
  - `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`
- the format-authoring guide and example index now route readers by:
  - format
  - failure mode
  - domain feel

Validation completed:

- `python3 -m unittest tests.xml.test_pattern_library tests.yaml.test_pattern_library tests.text.test_pattern_library tests.pdf.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

Closure review result:

- no material gap remains inside the selected second-wave scope
- the example library now shows both happy-path and ambiguity / invalid-fact handling across the supported evidence families
