# NAPE Evaluator Product Specification

`nape-eval` is a command-line evaluator used by the NAPE CLI to apply one or more test-of-detail files against collected evidence.

## Product Role

NAPE CLI owns procedure orchestration, evidence collection, report generation, and report signing. NAPE Evaluator owns the action-level evaluation boundary:

1. Receive one evidence file path.
2. Receive one or more requested test invocations.
3. Validate the caller-owned request shape.
4. Load the evidence.
5. Build evaluation metadata.
6. Dynamically import each test file.
7. Call `evaluate(evidence, evaluations, metadata)` for each executable test.
8. Print one JSON object containing `results` and nested `evaluator.messages` and `evaluator.summary`.

## Primary Users

- CLI users who need `nape-eval` installed so `nape collect report` can run.
- Test-of-detail authors who write Python `evaluate(evidence, evaluations, metadata)` functions.
- NAPE maintainers who depend on the evaluator process contract.
- Release maintainers who package and publish the `nape` Python package.

## Current Capability

Current behavior:

- Provides the `nape-eval` console script from the `nape` Python package.
- Supports `--check-install`.
- Supports direct mode with:
  - `--evidence <file>`
  - repeated `--invoke <json-object>`
  - repeated `--invoke-file <json-file>`
- Supports full-request mode with:
  - `--request-file <path-or->`
- Treats `--check-install` as mutually exclusive with evaluation arguments.
- Prints CLI usage and exits non-zero when invoked without arguments.
- Loads evidence by file extension.
- Builds minimal metadata for the test contract.
- Validates caller-owned `tests[*].evaluations[*]` input before test execution.
- Dynamically imports each test file.
- Calls `evaluate(evidence, evaluations, metadata)` for each executable test.
- Prints one JSON object to stdout containing `results` and nested `evaluator` status data.
- Converts common execution failures into evaluator `error` messages and blocked per-test result items.

Supported evidence behavior:

- `.txt` and unknown extensions: text lines
- `.json`: parsed JSON object
- `.xml`: XML root element
- `.yaml` and `.yml`: parsed YAML
- `.pdf`: extracted text lines

Known unprocessable extensions:

- common image formats such as `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`
- common archive formats such as `.zip`, `.gz`, `.tar`
- common media formats such as `.mp3`, `.mp4`, `.mov`, `.avi`
- executable or opaque binary formats such as `.exe`, `.bin`

Current metadata behavior:

- `evidence_type`: indicates the evaluator-selected evidence contract
- `schema_version`: indicates the evaluator input contract version

Current request behavior:

- the full outer request packet uses:
  - `evidence`
  - `tests`
- each requested test packet uses:
  - `test`
  - `evaluations`
- each evaluation item uses:
  - `subject`
  - `criteria`
- malformed caller-owned request packets are rejected before the use-case execution seam is crossed

Current completed-test behavior:

- a completed test returns one structured result object with:
  - `conclusion`
  - `facts`
  - `reason`
- accepted completed-test conclusions are:
  - `true`
  - `false`
  - `inconclusive`
  - `error`
- invalid completed-test result contracts are normalized to completed `error` results

Current response behavior:

- `results`: one item per requested test invocation
- `results[*].test`: the test file path
- `results[*].evidence`: the evidence path
- `results[*].evaluations`: the caller-owned accepted evaluation input for that invocation
- `results[*].execution`: evaluator-owned execution state
- `results[*].result`: completed test-owned result, or `null` when blocked
- `evaluator.messages`: evaluator-generated info, warning, and error notices
- `evaluator.summary`: aggregate counts by completed-test conclusion and evaluator message level

Current summary behavior:

- `count`: requested test count
- `ran`: test count whose result items have `execution.executed == true`
- `true`, `false`, `inconclusive`, `error`: counts from completed test conclusions only
- `message_count`, `message_info`, `message_warning`, `message_error`: counts from evaluator-generated notices

Interpretation rules:

- `evaluator.summary.error` means a test ran and returned `conclusion: "error"`.
- `evaluator.summary.message_error` means the evaluator/runtime reported an operational error.
- If `evaluator.summary.ran` is less than `evaluator.summary.count`, one or more requested tests were blocked before completing execution.

## Current Non-Goals

The current evaluator does not:

- evaluate multiple evidence files in one invocation
- generate NAPE reports
- sign files
- upload output anywhere
- provide a formal plugin sandbox for test files

## Current Direction

The V2 structured request/result model is now the active runtime direction rather than a future transport concept.

Current expansion points still include:

- a directory or manifest of test files
- multiple evidence files in one invocation
- aggregate or summary outcome policies across multiple test results
- richer typed fact/result conventions

Related docs:

- `current-evaluator-reference.md`
- `v2-structured-verification-input-proposal.md`
- `v2-structured-verification-result-proposal.md`
- `v2-policy-direction.md`

## Historical V1 Contrast

Historical V1 used `--test` transport and tuple-returning test contracts. The current product changes that boundary and therefore requires migration for older tests.

## Product Risks

- Dynamic Python imports execute arbitrary test code.
- The evaluator stdout contract is small but critical to NAPE CLI report generation.
- Runtime dependency metadata must match imported libraries.
- Typed evidence loading and the V2 request/result contract can break older tests written for V1 or early transitional shapes.
- Returning evaluator `error` messages is different from returning completed test `conclusion: "error"`, and downstream behavior depends on this distinction.
