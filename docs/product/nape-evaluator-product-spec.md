# NAPE Evaluator Product Specification

`nape-eval` is a command-line evaluator used by the NAPE CLI to apply a test-of-detail file against collected evidence.

## Product Role

NAPE CLI owns procedure orchestration, evidence collection, report generation, and report signing. NAPE Evaluator owns the action-level evaluation boundary:

1. Receive one evidence file path.
2. Receive one or more test-of-detail invocation inputs, each containing a test path and optional caller-supplied test parameters.
3. Load the evidence.
4. Build evaluation metadata.
5. Dynamically import each test file.
6. Call `evaluate(evidence, test_parameters, metadata)` for each test.
7. Print one JSON object containing `results` and nested `evaluator.messages` and `evaluator.summary`.

## Primary Users

- CLI users who need `nape-eval` installed so `nape collect report` can run.
- Test-of-detail authors who write Python `evaluate(evidence, test_parameters, metadata)` functions.
- NAPE maintainers who depend on the evaluator process contract.
- Release maintainers who package and publish the `nape` Python package.

## Current Capability

Current behavior:

- Provides the `nape-eval` console script from the `nape` Python package.
- Supports `--check-install`.
- Supports `--evidence <file>` and one or more `--test <python-file>` arguments together.
- Supports repeated `--test-parameters-file <json-file>` arguments matched by position to repeated `--test` arguments.
- Treats `--check-install` as mutually exclusive with `--evidence`, `--test`, and `--test-parameters-file`.
- Prints CLI usage and exits non-zero when invoked without arguments.
- Loads evidence by file extension.
- Builds minimal metadata for the test contract.
- Loads optional caller-supplied test parameters from JSON object files.
- Dynamically imports each test file.
- Calls `evaluate(evidence, test_parameters, metadata)` for each test.
- Prints one JSON object to stdout containing `results` and nested `evaluator` status data.
- Converts common execution failures into evaluator `error` messages rather than synthetic result items.

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

Current test-parameter behavior:

- `test_parameters` is always a dict at the test call boundary
- omitted parameter files become `{}`
- supplied parameter files must decode to a top-level JSON object
- parameter transport/setup failures block only the affected test invocation when possible

Current response behavior:

- `results`: one item per requested test invocation
- `results[*].evidence_file`: the evidence path attached to that invocation
- `results[*].test_parameters`: the decoded parameter dict passed to the test, or `null` when no valid dict was available
- `results[*].executed`: whether the test function actually completed
- `results[*].test_parameters_source`: the parameter-file path used for that test, or `null`
- `evaluator.messages`: evaluator-generated info, warning, and error notices
- `evaluator.messages[*].test_parameters_source`: the parameter-file path tied to that invocation, or `null`
- `evaluator.summary`: aggregate counts by result outcome and evaluator message level

Current summary behavior:

- `count`: requested test count
- `ran`: test count whose result items have `executed == true`
- `pass`, `fail`, `inconclusive`, `error`: counts from returned test outcomes only
- `message_count`, `message_info`, `message_warning`, `message_error`: counts from evaluator-generated notices

Interpretation rules:

- `evaluator.summary.error` means a test ran with `executed == true` and returned `"error"`.
- `evaluator.summary.message_error` means the evaluator/runtime reported an operational error.
- If `evaluator.summary.ran` is less than `evaluator.summary.count`, one or more requested tests were blocked before completing execution.

## Current Non-Goals

The current evaluator does not:

- Evaluate multiple evidence files in one invocation.
- Generate NAPE reports.
- Sign files.
- Upload output anywhere.
- Provide a formal plugin sandbox for test files.

## Future Enhancement Direction

The current batch boundary is one evidence file plus one or more explicit `--test` arguments.

Potential next expansions:

- a directory or manifest of test files
- multiple evidence files in one invocation
- aggregate or summary outcome policies across multiple test results
- richer manifest-based or inline parameter binding beyond repeated parameter files

Current exploration input for caller-supplied test parameters is recorded in `test-parameter-exploration.md`.

## V2 Policy Direction

Recommended V2 contract-direction decisions are recorded in `v2-policy-direction.md`.

The current recommended direction is:

- keep typed evidence loading as the canonical contract
- validate returned outcome vocabulary
- keep exit status `0` when valid evaluator JSON is produced
- keep trusted-code execution explicit unless a real sandbox is implemented

## Historical V1 Contrast

Historical V1 passed every evidence file as text lines into `evaluate(evidence)`. The current product changes that contract for structured evidence and therefore requires migration for older JSON-parsing tests.

## Product Risks

- Dynamic Python imports execute arbitrary test code.
- The evaluator stdout contract is small but critical to NAPE CLI report generation.
- Runtime dependency metadata must match imported libraries.
- Typed evidence loading can break existing tests that expect raw text lines.
- Returning evaluator `error` messages is different from returned test outcome `"error"`, and NAPE CLI behavior depends on this distinction.
