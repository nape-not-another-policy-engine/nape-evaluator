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

Current CLI execution contract:

- exact standalone `--check-install` prints a plain-text health message and returns exit status `0`
- every non-`--check-install` invocation returns exit status `0`
- every non-`--check-install` invocation prints one JSON object to stdout
- malformed caller-owned invocation input is represented as request-scoped evaluator `error` message output rather than stderr-only parser termination

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
- malformed caller-owned request packets are rejected by request-builder validation before use-case execution
- when that rejection happens through the CLI, the CLI still emits the normal outer JSON envelope with:
  - `results: []`
  - request-scoped evaluator `error` messages
- top-level full-request packets use:
  - `evidence`
  - `tests`
- each requested test packet uses:
  - `test`
  - `evaluations`
- duplicate `subject.name` values within one requested test packet are rejected rather than silently shadowing one another

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

If a completed test returns an invalid result contract, the evaluator normalizes that completed invocation to:

- `result.conclusion = "inconclusive"`
- `result.facts = []`
- `result.reason = "...invalid result contract..."`

That is treated as a completed test-level contract violation normalized to `inconclusive`, not as an evaluator execution failure.

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
  "result": {
    "conclusion": "inconclusive",
    "facts": [],
    "reason": "The test could not be completed, so the conclusion is inconclusive. The evaluator could not load the evidence file because it was not found."
  }
}
```

Important current semantics:

- every requested test gets a `results[*]` row
- `execution.executed` tells whether the Python test completed
- `execution.status` is:
  - `completed`
  - `blocked`
- completed tests always carry structured `result`
- blocked tests always carry evaluator-synthesized structured `result`

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
- `true`, `false`, `inconclusive`: counts from result conclusions
- `message_count`, `message_info`, `message_warning`, `message_error`: counts from distinct emitted evaluator events only

Important current distinction:

- `evaluator.summary.inconclusive` includes both:
  - completed tests that returned `inconclusive`
  - blocked invocations represented as evaluator-synthesized `inconclusive` results
- `evaluator.summary.message_error` means the evaluator/runtime reported an operational problem

If `ran < count`, one or more requested tests were blocked before successful execution.

Current `evaluator.messages` purpose:

- `evaluator.messages` is the evaluator-owned operational notice stream
- it is used for evaluator-generated `info`, `warning`, and `error` notices
- it is not the place where a completed test explains its domain reasoning

Current `result.reason` purpose:

- `results[*].result.reason` is dual-source
- when `execution.executed == true`, it is test-owned reasoning from a completed test
- when `execution.executed == false`, it is evaluator-owned reasoning explaining why the blocked invocation is `inconclusive`

Current multi-test message semantics:

- shared evidence-side notices are emitted as distinct request-scoped events
- request-scoped messages identify impacted tests through `affected_tests`
- request-scoped malformed-request messages can use `affected_tests == []` when no accepted requested-test set existed yet
- test-scoped messages identify one affected test through `test_file`
- `message_count` is therefore a count of distinct emitted evaluator events

Example interpretation:

- if two tests run successfully against one evidence file and no evaluator notices occur:
  - `summary.count == 2`
  - `summary.ran == 2`
  - `summary.message_count == 0`
- if one evidence-side warning applies to both requested tests:
  - `summary.count == 2`
  - `summary.ran == 2`
  - `summary.message_warning == 1`
  - the warning row uses:
    - `scope == "request"`
    - `affected_tests == ["./test-a.py", "./test-b.py"]`
- if one requested test is blocked before execution:
  - `results[*].execution.executed == false`
  - `results[*].result.conclusion == "inconclusive"`
  - the blocked result row contains evaluator-owned `reason`
  - the operational explanation also appears in `evaluator.messages`

## Current Failure Ownership

Today the evaluator distinguishes between:

- test-owned completed conclusions
- evaluator-owned operational failures

Evaluator-owned failures still produce:

- a blocked outer result item for each affected requested test
- one or more evaluator messages describing the operational problem
- `evaluator.messages[*].stack_trace` when traceback detail exists

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
