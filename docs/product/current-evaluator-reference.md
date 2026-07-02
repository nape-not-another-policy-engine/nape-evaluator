# Current Evaluator Reference

This document records what `nape-evaluator` does today in committed code.

## Purpose

Use this document to:

- show the current evaluator flow as implemented
- anchor user, reference, and maintainer docs to the active runtime contract
- separate current runtime behavior from older historical contract material

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
- `tests/test_request_builder.py`

## Current Evaluator Model

The current evaluator model is:

1. accept one evidence path
2. accept one or more requested test packets
3. validate caller-owned request structure before execution
4. load the evidence once
5. derive evaluator-owned metadata once
6. load and execute each requested test independently
7. emit one outer result item per requested test
8. emit evaluator-owned messages and summary data alongside those result items

## Current CLI Transport

Current supported CLI inputs:

- `--check-install`
- direct invocation mode:
  - `--evidence <file>`
  - repeated `--invoke <json-object>`
  - repeated `--invoke-file <json-file>`
- full-request mode:
  - `--request-file <path-or->`

Current CLI examples:

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke '{"test":"./verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

```bash
nape-eval --request-file ./request.json
```

```bash
cat request.json | nape-eval --request-file -
```

Current CLI validation rules:

- `--check-install` cannot be combined with evaluation arguments
- direct invocation mode requires `--evidence`
- direct invocation mode requires at least one `--invoke` or `--invoke-file`
- `--request-file` cannot be combined with `--evidence`, `--invoke`, or `--invoke-file`
- `--request-file -` means read the full request packet from stdin

## Current Request Model

The evaluator now uses a verified builder-only request seam:

```python
request = (
    EvaluateEvidenceRequest.builder()
    .evidence_path("./author_verification.json")
    .raw_tests(
        [
            {
                "test": "./verify_author_complete.py",
                "evaluations": [
                    {
                        "subject": {"name": "status", "data_type": "text"},
                        "criteria": {"equals": "complete"},
                    }
                ],
            }
        ]
    )
    .try_build()
)
```

Important current behavior:

- request validation happens before the use-case execution seam is crossed
- malformed caller-owned request packets are rejected by request-builder validation
- top-level full-request packets use:
  - `evidence`
  - `tests`
- each requested test packet uses:
  - `test`
  - `evaluations`

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

## Current Test Call Boundary

After evidence loading, the evaluator imports each requested Python test file and calls:

```python
evaluate(evidence, evaluations, metadata)
```

Current argument ownership:

- `evidence`: evaluator-loaded evidence content
- `evaluations`: caller-owned evaluation input
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
- the Python test applies its own reasoning against caller-owned `evaluations`
- the Python test returns one structured result object

## Current Test Result Contract

Completed tests must return:

```json
{
  "conclusion": "true",
  "facts": [],
  "reason": "Reason text"
}
```

Current accepted completed-test conclusions:

- `true`
- `false`
- `inconclusive`
- `error`

If a completed test returns an invalid result contract, the evaluator normalizes that completed invocation to:

- `result.conclusion = "error"`
- `result.facts = []`
- `result.reason = "...invalid result contract..."`

That is treated as a completed test-level contract error, not as an evaluator execution failure.

## Current Outer Result Item

Today the evaluator emits one result item per requested test.

Current completed shape:

```json
{
  "test": "./verify_author_complete.py",
  "evidence": "./author_verification.json",
  "evaluations": [
    {
      "subject": {
        "name": "status",
        "data_type": "text"
      },
      "criteria": {
        "equals": "complete"
      }
    }
  ],
  "execution": {
    "executed": true,
    "status": "completed"
  },
  "result": {
    "conclusion": "true",
    "facts": [
      {
        "name": "status",
        "value": "complete",
        "value_type": "text",
        "status": "found"
      }
    ],
    "reason": "The author has achieved the status of complete."
  }
}
```

Current blocked shape:

```json
{
  "test": "./verify_author_complete.py",
  "evidence": "./missing.json",
  "evaluations": [
    {
      "subject": {
        "name": "status",
        "data_type": "text"
      },
      "criteria": {
        "equals": "complete"
      }
    }
  ],
  "execution": {
    "executed": false,
    "status": "blocked"
  },
  "result": null
}
```

Important current semantics:

- every requested test gets a `results[*]` row
- `execution.executed` tells whether the Python test completed
- `execution.status` is:
  - `completed`
  - `blocked`
- completed tests always carry structured `result`
- blocked tests always carry `result: null`

## Current Evaluator Output Envelope

Today the evaluator prints:

```json
{
  "results": [],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 0,
      "ran": 0,
      "true": 0,
      "false": 0,
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

- `count`: number of requested tests
- `ran`: number of result items with `execution.executed == true`
- `true`, `false`, `inconclusive`, `error`: counts from completed test results only
- `message_count`, `message_info`, `message_warning`, `message_error`: counts from evaluator-generated notices only

Important current distinction:

- `evaluator.summary.error` means a completed test returned conclusion `error`
- `evaluator.summary.message_error` means the evaluator/runtime reported an operational problem

If `ran < count`, one or more requested tests were blocked before successful execution.

## Current Failure Ownership

Today the evaluator distinguishes between:

- test-owned completed conclusions
- evaluator-owned operational failures

Evaluator-owned failures still produce:

- a blocked outer result item for each affected requested test
- one or more evaluator messages describing the operational problem

Examples of current evaluator-owned failures:

- evidence file not found
- unprocessable evidence type
- evidence load error
- test file not found
- test import error
- unexpected exception during test execution

## Historical Note

Older evaluator contracts used:

- repeated `--test`
- repeated `--test-parameters-file`
- `evaluate(evidence, test_parameters, metadata)`
- flat `outcome` / `reason` result rows

That contract is no longer the current runtime behavior.
