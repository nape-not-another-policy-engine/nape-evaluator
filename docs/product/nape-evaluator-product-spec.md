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

## Current V1 Capability

Committed V1 behavior:

- Provides the `nape-eval` console script from the `nape` Python package.
- Supports `--check-install`.
- Supports `--evidence <file>` and `--test <python-file>` together.
- Reads evidence as text lines.
- Dynamically imports the test file.
- Calls `evaluate(evidence_lines)`.
- Prints one JSON object to stdout with `outcome` and `reason`.
- Converts common execution failures into JSON `error` outcomes.

## V1 Non-Goals

V1 does not:

- Evaluate multiple evidence files in one invocation.
- Evaluate multiple tests in one invocation.
- Validate outcome values against the NAPE kernel.
- Generate NAPE reports.
- Sign files.
- Upload output anywhere.
- Provide a formal plugin sandbox for test files.

## V2 Candidate Direction

The current worktree contains uncommitted V2 candidate behavior for typed evidence loading:

- `.txt` and unknown extensions as text lines.
- `.json` as parsed JSON.
- `.xml` as an XML root element.
- `.yaml` and `.yml` as parsed YAML.
- `.pdf` as extracted text lines.

This is a contract change because `evaluate(evidence)` may receive different Python object types. Treat this as candidate behavior until reviewed and released.

## Product Risks

- Dynamic Python imports execute arbitrary test code.
- The evaluator stdout contract is small but critical to NAPE CLI report generation.
- Runtime dependency metadata must match imported libraries.
- Typed evidence loading can break existing tests that expect raw text lines.
- Returning JSON `error` is different from failing the process, and NAPE CLI behavior depends on this distinction.
