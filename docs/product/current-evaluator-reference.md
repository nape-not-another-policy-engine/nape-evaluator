# Current Evaluator Reference

This document records what `nape-evaluator` does today in committed code.

Use it as the current-behavior baseline when reviewing V2 input/output expansion proposals. It is not a proposal document.

## Purpose

Use this document to:

- show the current evaluator flow as implemented
- separate current behavior from V2 proposal work
- anchor V2 input/output changes to the existing evaluator model rather than a clean-sheet redesign

## Source Of Truth

This reference is grounded in:

- `src/nape_evaluator/application/io/cli.py`
- `src/nape_evaluator/domain/use_cases.py`
- `src/nape_evaluator/domain/use_case_models.py`
- `src/nape_evaluator/application/driver/evidence_gateway.py`
- `src/nape_evaluator/application/driver/test_of_detail_gateway.py`
- `src/nape_evaluator/application/io/output_contract.py`
- `tests/test_cli_contract.py`
- `tests/test_evaluator_use_case.py`
- `tests/test_output_contract.py`

## Current Evaluator Model

The current evaluator model is:

1. accept one evidence path
2. accept one or more requested test invocations
3. optionally accept one parameter file per requested test invocation
4. load the evidence once
5. derive evaluator-owned metadata once
6. load and execute each requested test invocation independently
7. emit one outer result item per requested test invocation
8. emit evaluator-owned messages and summary data alongside those result items

This means the evaluator already has a stable outer execution model. The current V2 input/output work is an expansion of that model, not a replacement of it.

## Current CLI Transport

Current supported CLI inputs:

- `--check-install`
- `--evidence <file>`
- repeated `--test <python-file>`
- repeated `--test-parameters-file <json-file>` matched by position to repeated `--test`

Current CLI example:

```bash
nape-eval \
  --evidence ./sonar_metrics.json \
  --test ./code_cover_80.py \
  --test-parameters-file ./code_cover_80.parameters.json \
  --test ./coverage_floor.py \
  --test-parameters-file ./coverage_floor.parameters.json
```

Current CLI validation rules:

- `--check-install` cannot be combined with evaluation arguments
- `--evidence` and `--test` must be provided together
- `--test-parameters-file` cannot be used without both `--evidence` and `--test`
- if parameter files are supplied, they must be repeated once per `--test`

## Current Request Model

The CLI builds:

- one `EvaluateEvidenceRequest`
- one `TestInvocationRequest` per requested `--test`

Today the request model is still path-oriented:

```python
EvaluateEvidenceRequest(
    evidence_path="./sonar_metrics.json",
    test_invocations=[
        TestInvocationRequest.ready(
            test_path="./code_cover_80.py",
            test_parameters={"minCoverage": 80},
            test_parameters_source="./code_cover_80.parameters.json",
        )
    ],
)
```

Important current behavior:

- omitted parameter files become `{}` for that invocation
- parameter-file load or decode failures block only the affected invocation when possible
- blocked parameter-file invocations keep the requested test path but may carry `test_parameters=None`

## Current Evidence Loading

The evaluator loads evidence by filename extension before calling any test.

Current evidence loading behavior:

- `.txt`: text lines
- `.json`: parsed JSON via `json.load`
- `.xml`: XML root element via `xml.etree.ElementTree`
- `.yaml` and `.yml`: parsed YAML via `yaml.safe_load`
- `.pdf`: extracted text lines via `PyPDF2`
- no extension: text lines plus evaluator warning `missing_extension_text_fallback`
- unknown extension: text lines plus evaluator warning `unknown_extension_text_fallback`

Current known unprocessable extensions are blocked before test execution:

- common image formats such as `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`
- common archive formats such as `.zip`, `.gz`, `.tar`
- common media formats such as `.mp3`, `.mp4`, `.mov`, `.avi`
- executable or opaque binary formats such as `.exe`, `.bin`

When an unprocessable extension is detected, the evaluator emits message code `unprocessable_evidence_type` and requested invocations become blocked.

## Current Test Call Boundary

After evidence loading, the evaluator imports each requested Python test file and calls:

```python
evaluate(evidence, test_parameters, metadata)
```

Current argument ownership:

- `evidence`: evaluator-loaded evidence content
- `test_parameters`: caller-owned parameter dict
- `metadata`: evaluator-owned execution metadata

Current metadata keys:

```json
{
  "evidence_type": "json",
  "schema_version": "2"
}
```

Current evaluator assumptions:

- the evaluator is claim-agnostic
- the evaluator does not own comparison logic
- the Python test extracts the needed facts from `evidence`
- the Python test applies its own comparison logic against `test_parameters`
- the Python test returns a two-item tuple `(outcome, reason)`

Current accepted returned outcomes:

- `pass`
- `fail`
- `inconclusive`
- `error`

If the test returns any other outcome, the evaluator converts that returned value to result-level `error` with an explanatory reason.

## Current Outer Result Item

Today the evaluator emits one result item per requested test invocation.

Current successful shape:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./sonar_metrics.json",
  "test_parameters": {
    "minCoverage": 80
  },
  "test_parameters_source": "./code_cover_80.parameters.json",
  "executed": true,
  "outcome": "pass",
  "reason": "Coverage is 85.0%, which meets the required 80%."
}
```

Current blocked-execution shape:

```json
{
  "test": "./code_cover_80.py",
  "evidence_file": "./image.png",
  "test_parameters": {
    "minCoverage": 80
  },
  "test_parameters_source": "./code_cover_80.parameters.json",
  "executed": false,
  "outcome": "error",
  "reason": "Evidence file extension '.png' is not supported for evaluation."
}
```

Important current semantics:

- every requested test invocation gets a `results[*]` row
- `executed` tells whether the test actually ran to completion
- `outcome` is still a flat string returned by the current contract
- `reason` is the current human-readable explanation field

## Current Evaluator Output Envelope

Today the evaluator prints:

```json
{
  "results": [
    {
      "test": "./code_cover_80.py",
      "evidence_file": "./sonar_metrics.json",
      "test_parameters": {
        "minCoverage": 80
      },
      "test_parameters_source": "./code_cover_80.parameters.json",
      "executed": true,
      "outcome": "pass",
      "reason": "Coverage is 85.0%, which meets the required 80%."
    }
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 1,
      "ran": 1,
      "pass": 1,
      "fail": 0,
      "inconclusive": 0,
      "error": 0,
      "message_count": 0,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 0
    }
  }
}
```

## Current Execution And Message Semantics

Current summary behavior:

- `count`: number of requested test invocations
- `ran`: number of result items with `executed == true`
- `pass`, `fail`, `inconclusive`, `error`: counts from executed result outcomes only
- `message_count`, `message_info`, `message_warning`, `message_error`: counts from evaluator-generated notices only

Important current distinction:

- `evaluator.summary.error` means a test ran and returned outcome `error`
- `evaluator.summary.message_error` means the evaluator/runtime reported an operational problem

If `ran < count`, one or more requested invocations were blocked before successful execution.

## Current Failure Ownership

Today the evaluator distinguishes between:

- test-owned returned outcomes
- evaluator-owned operational failures

Evaluator-owned failures still produce:

- a blocked outer result item for each affected requested invocation
- one or more evaluator messages describing the operational problem

Examples of current evaluator-owned failures:

- evidence file not found
- unprocessable evidence type
- evidence load error
- test file not found
- test import error
- unexpected exception during test execution
- parameter-file load or decode failure

## What Still Applies While Expanding V2 Input/Output

The following current fundamentals still apply unless explicitly changed later:

- the evaluator remains claim-agnostic
- the evaluator still executes one shared evidence input against one or more requested tests
- evidence is still loaded by the evaluator before test execution
- evaluator-owned metadata remains separate from caller-owned comparison input
- the Python test still owns fact extraction, comparison logic, and human-readable reasoning
- the evaluator still owns transport, invocation execution status, messages, and summary data
- per-test output is still anchored around one outer result item per requested invocation

That means current V2 input/output work should be read as an expansion of the existing request/result model, not as a redesign of the evaluator's core responsibility.
