# Evaluator Contract

This reference defines the evaluator boundary consumed by NAPE CLI.

## Process Contract

Install check:

```bash
nape-eval --check-install
```

Direct invocation mode:

```bash
nape-eval \
  --evidence <evidence-file> \
  --invoke '{"test":"./test.py","evaluations":[]}'
```

```bash
nape-eval \
  --evidence <evidence-file> \
  --invoke-file <invoke-a.json> \
  --invoke-file <invoke-b.json>
```

Full-request mode:

```bash
nape-eval --request-file <request.json>
nape-eval --request-file -
```

Rules:

- `--check-install` cannot be combined with evaluation arguments
- direct mode requires `--evidence` plus at least one `--invoke` or `--invoke-file`
- `--request-file` cannot be combined with `--evidence`, `--invoke`, or `--invoke-file`
- `--request-file -` reads the full outer request packet from stdin

## Security Boundary

The evaluator dynamically imports and executes the Python file supplied by each requested `test`.

Treat test-of-detail files as executable code:

- run only trusted test files
- review test files before publishing them in assurance procedure repositories
- do not run untrusted test files on a workstation or CI runner with sensitive credentials

## Request Contract

Direct invocation packets use:

```json
{
  "test": "./verify_author_complete.py",
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
  ]
}
```

Full outer request packets use:

```json
{
  "evidence": "./author_verification.json",
  "tests": [
    {
      "test": "./verify_author_complete.py",
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
      ]
    }
  ]
}
```

Request validation behavior:

- `evidence` must be a non-empty string
- `tests` must be a non-empty array
- each test item must contain exactly:
  - `test`
  - `evaluations`
- each evaluation item must contain exactly:
  - `subject`
  - `criteria`
- `subject.name` must be lowercase snake_case ASCII, start with a letter, and end with an alphanumeric
- `subject.data_type` must be one of the bounded supported values
- `criteria` must be a non-empty object with supported keys compatible with `subject.data_type`
- no hidden type coercion is performed

Malformed caller-owned request packets are rejected before the use-case execution seam is crossed.

## Test Call Contract

The evaluator calls:

```python
def evaluate(evidence, evaluations, metadata):
    ...
```

Argument ownership:

- `evidence`: evaluator-loaded evidence content
- `evaluations`: caller-owned accepted evaluation input
- `metadata`: evaluator-owned execution metadata

Current metadata keys:

- `evidence_type`
- `schema_version`

## Evidence Contract

The evaluator inspects the evidence file extension before calling `evaluate(...)`.

| Extension | Input to `evaluate(evidence, evaluations, metadata)` |
| --- | --- |
| `.txt` | text lines |
| `.json` | parsed JSON object |
| `.xml` | XML root element |
| `.yaml`, `.yml` | parsed YAML object |
| `.pdf` | extracted text lines |
| unknown | text lines |

Known unprocessable extensions are blocked before test execution.

## Return Contract

Completed tests must return:

```json
{
  "conclusion": "true",
  "facts": [],
  "reason": "Reason text"
}
```

Required result keys:

- `conclusion`
- `facts`
- `reason`

Rules:

- `conclusion` must be one of:
  - `true`
  - `false`
  - `inconclusive`
  - `error`
- `facts` must be an array
- `reason` must be a non-empty string

If a completed test returns an invalid result contract:

- the test is still counted as `ran`
- the evaluator normalizes the completed result to:
  - `conclusion: "error"`
  - `facts: []`
  - explanatory `reason`

## Output Contract

The evaluator prints one JSON object to stdout:

```json
{
  "results": [
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
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 1,
      "ran": 1,
      "true": 1,
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

Per-test results contain:

- `test`
- `evidence`
- `evaluations`
- `execution`
- `result`

`execution` contains:

- `executed`
- `status`

Rules:

- when `execution.executed == true`, `execution.status` must be `completed` and `result` must be present
- when `execution.executed == false`, `execution.status` must be `blocked` and `result` must be `null`

## Summary Contract

Summary contains:

- requested test `count`
- completed test `ran`
- result totals by completed-test conclusion:
  - `true`
  - `false`
  - `inconclusive`
  - `error`
- message totals by evaluator message level

Interpretation rules:

- the evaluator returns one result item per requested test
- `summary.ran` counts only result items where `execution.executed == true`
- `summary.error` counts only completed-test `error` conclusions
- evaluator/runtime failures are represented by `evaluator.messages` and counted in `summary.message_error`

## Failure Contract

The evaluator catches common failures and returns evaluator `error` messages.

Examples:

- missing evidence file
- unprocessable evidence type
- evidence load failure
- missing test file
- test import failure
- unhandled exception during test execution

Consumers should not infer success from exit status alone. For action evaluation, parse stdout JSON and inspect `results` and `evaluator`.

Do not conflate completed test `error` conclusions with evaluator execution failures:

- a completed test can return `conclusion: "error"` with `execution.executed == true`
- a blocked invocation still appears in `results` with `execution.executed == false`
- evaluator/runtime failures increment `summary.message_error`

## Historical Note

Older contracts used `--test`, `--test-parameters-file`, `test_parameters`, and flat `outcome` / `reason` rows.

That is no longer the current evaluator contract.
