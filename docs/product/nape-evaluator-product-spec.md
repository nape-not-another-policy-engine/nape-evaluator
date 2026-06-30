# NAPE Evaluator Product Specification

`nape-eval` is a command-line evaluator used by the NAPE CLI to apply a test-of-detail file against collected evidence.

## Product Role

NAPE CLI owns procedure orchestration, evidence collection, report generation, and report signing. NAPE Evaluator owns the action-level evaluation boundary:

1. Receive one evidence file path.
2. Receive one test-of-detail Python file path.
3. Load the evidence.
4. Dynamically import the test file.
5. Call `evaluate(evidence)`.
6. Print JSON containing `outcome` and `reason`.

## Primary Users

- CLI users who need `nape-eval` installed so `nape collect report` can run.
- Test-of-detail authors who write Python `evaluate(evidence)` functions.
- NAPE maintainers who depend on the evaluator process contract.
- Release maintainers who package and publish the `nape` Python package.

## Current Capability

Current behavior:

- Provides the `nape-eval` console script from the `nape` Python package.
- Supports `--check-install`.
- Supports `--evidence <file>` and `--test <python-file>` together.
- Loads evidence by file extension.
- Dynamically imports the test file.
- Calls `evaluate(evidence)`.
- Prints one JSON object to stdout with `outcome` and `reason`.
- Converts common execution failures into JSON `error` outcomes.

Supported evidence behavior:

- `.txt` and unknown extensions: text lines
- `.json`: parsed JSON object
- `.xml`: XML root element
- `.yaml` and `.yml`: parsed YAML
- `.pdf`: extracted text lines

## V1 Non-Goals

V1 does not:

- Evaluate multiple evidence files in one invocation.
- Evaluate multiple tests in one invocation.
- Validate outcome values against the NAPE kernel.
- Generate NAPE reports.
- Sign files.
- Upload output anywhere.
- Provide a formal plugin sandbox for test files.

## Historical V1 Contrast

Historical V1 passed every evidence file as text lines into `evaluate(evidence)`. The current product changes that contract for structured evidence and therefore requires migration for older JSON-parsing tests.

## Product Risks

- Dynamic Python imports execute arbitrary test code.
- The evaluator stdout contract is small but critical to NAPE CLI report generation.
- Runtime dependency metadata must match imported libraries.
- Typed evidence loading can break existing tests that expect raw text lines.
- Returning JSON `error` is different from failing the process, and NAPE CLI behavior depends on this distinction.
