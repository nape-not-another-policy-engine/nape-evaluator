> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 12: Evidence Format Authoring Guides And Examples

## Purpose

Extend the current V2 authoring guide set and executable example library so a reader can learn, copy, and test format-specific extraction patterns for JSON, XML, YAML, text, and PDF evidence.

This plan is intentionally not about changing the evaluator transport or evaluation model.

It is about making the existing typed-evidence model teachable and executable.

## Why This Exists

The current guide set explains:

- V2 request shape
- subject and criteria patterns
- general fact extraction and fact establishment
- executable JSON examples

The current guide set does not yet explain with the same completeness:

- how to write extraction helpers against XML evidence
- how to write extraction helpers against YAML evidence
- how to write extraction helpers against text-line evidence
- how to write extraction helpers against PDF-derived text-line evidence
- how the docs and example-fixture tree are structured so readers can move between general guidance and format-specific guidance predictably

## Guardrails

- keep the current V2 evaluator boundary unchanged:
  - `evaluate(evidence, evaluations, metadata)`
- keep the current evaluator-owned versus test-owned split explicit
- keep the guide model consistent with the existing `docs/user/v2-test-authoring/` reading paths
- do not let format examples silently drift into a second evaluation model
- keep public-interface end-to-end tests small; use focused lower-level tests where binary-format seams would otherwise create brittle noise

## Selected Direction

Use three aligned deliverables:

1. one permanent format-authoring guide in `docs/user/v2-test-authoring/`
2. one explicit guide-set / fixture-tree structure explanation so readers know how the authoring docs relate to the executable examples
3. one first-wave parallel fixture library spanning the supported evidence families:
   - JSON
   - XML
   - YAML
   - text
   - PDF

## Deliverables

### 1. Permanent format-authoring guide

Create:

- `docs/user/v2-test-authoring/evidence-format-authoring.md`

It should show, for each evidence family:

- what object shape the test receives
- how to defensively validate `metadata["evidence_type"]`
- how to extract one or two representative facts
- what common pitfalls exist
- which executable fixture to copy

### 2. Guide-set and fixture-tree model

Update current user docs so the structure is explicit rather than implied:

- what each main authoring doc is for
- when to move from the linear progression into format-specific guidance
- how the executable fixtures are organized by evidence family
- how to use the fixture library without confusing contract tests and copyable examples

### 3. First-wave parallel examples

Add format-specific examples that all remain within the selected V2 evaluation model.

Recommended first wave:

- JSON starter example
- XML starter example
- YAML starter example
- text starter example
- PDF starter example

The examples do not all need identical domain semantics, but they should be close enough that readers can compare extraction style rather than re-learn the whole evaluation model.

## Test Strategy

Keep test structure explicit:

- root `tests/test_*.py` remains evaluator contract and gateway coverage
- `tests/<format>/` directories hold format-specific authoring examples
- each format example directory should use the same sub-structure when practical:
  - `evidence/`
  - `test_of_detail/`
  - `test_pattern_library.py`

Keep public-interface tests bounded:

- use thin CLI-facing end-to-end tests where real files are cheap and stable
- use controlled in-process seams where binary-format support would otherwise require brittle artifact maintenance

## Work Steps

1. add the active plan and handoff
2. author the permanent format-authoring guide
3. update V2 authoring routing docs to explain the guide-set model and fixture-tree model
4. add the first-wave format-parallel fixtures and tests
5. update reference traceability where needed
6. run the targeted automated tests
7. closure-review whether any material gap remains after the first wave

## Open Questions

None at plan start.

The main design choice is already selected:

- clear and complete authoring guidance is preferred over brevity
- format-specific examples should be parallel where useful, not artificially identical

## Completion Snapshot

This plan is complete.

Landed outcomes:

- `docs/user/v2-test-authoring/evidence-format-authoring.md` now provides format-specific extraction guidance for JSON, XML, YAML, text, and PDF
- the V2 authoring reading paths now route readers into that guide at the correct point
- `tests/README.md` now explains the repo test-structure split between evaluator contract tests and copyable authoring examples
- executable first-wave format example trees now exist for:
  - XML
  - YAML
  - text
  - PDF
- the existing JSON example tree remains the baseline structured example library
- PDF authoring examples are intentionally proven through a controlled extraction seam rather than heavyweight checked-in binary artifacts

Validation completed:

- `python3 -m unittest tests.xml.test_pattern_library tests.yaml.test_pattern_library tests.text.test_pattern_library tests.pdf.test_pattern_library tests.json.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

Closure review result:

- no material first-wave gap remains for the selected goal
- deeper future expansion can add more domain-rich or negative-path format examples, but it is not required to make the current typed-evidence model teachable
