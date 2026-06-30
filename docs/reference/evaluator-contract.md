# Evaluator Contract

This reference defines the evaluator boundary consumed by NAPE CLI.

## Process Contract

Install check:

```bash
nape-eval --check-install
```

Action evaluation:

```bash
nape-eval --evidence <evidence-file> --test <test-file>
nape-eval --evidence <evidence-file> --test <test-a.py> --test <test-b.py>
```

`--evidence` and at least one `--test` must be provided together.

## Security Boundary

The evaluator dynamically imports and executes the Python file supplied by `--test`.

Treat test-of-detail files as executable code:

- Run only trusted test files.
- Review test files before publishing them in assurance procedure repositories.
- Do not run untrusted test files on a workstation or CI runner with sensitive credentials.
- Keep evidence parsing deterministic and local to the evidence file.

## Test Import Contract

The evaluator dynamically imports the file supplied by `--test`.

The file must define:

```python
def evaluate(evidence, metadata):
    ...
```

## Evidence Contract

The evaluator inspects the evidence file extension before calling `evaluate(...)`.

| Extension | Input to `evaluate(evidence, metadata)` |
| --- | --- |
| `.txt` | text lines |
| `.json` | parsed JSON object |
| `.xml` | XML root element |
| `.yaml`, `.yml` | parsed YAML object |
| `.pdf` | extracted text lines |
| unknown | text lines |

Metadata passed as the second argument currently contains:

- `evidence_type`
- `schema_version`

## Return Contract

`evaluate(...)` must return:

```python
outcome, reason
```

The evaluator serializes the result into one top-level object:

```json
{
  "results": [
    {
      "test": "test-a.py",
      "outcome": "pass",
      "reason": "Reason text"
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

Per-test results contain:

- `test`
- `outcome`
- `reason`

Evaluator-generated operational notices appear in `evaluator.messages`.

Summary contains:

- requested test `count`
- completed test `ran`
- result totals by outcome
- message totals by level

Summary interpretation rules:

- `summary.error` counts only result-level `"error"` outcomes returned by tests that actually completed `evaluate(...)`.
- Evaluator/runtime failures are represented by `evaluator.messages` and counted in `summary.message_error`.
- If `summary.ran < summary.count`, at least `summary.count - summary.ran` requested tests were blocked before completing the test contract.

## Outcome Vocabulary

The expected NAPE outcome vocabulary is:

- `pass`
- `fail`
- `inconclusive`
- `error`

The evaluator validates the returned outcome before serializing JSON.

If a test returns any other value:

- the test is still counted as `ran`
- the result is normalized to `outcome: "error"`
- the result `reason` explains that the test returned an unsupported outcome
- this is treated as a result-level contract error, not as an evaluator runtime failure

## Failure Contract

The evaluator catches these failures and returns evaluator `error` messages:

| Failure | Message code | Message prefix |
| --- | --- |
| `FileNotFoundError` | `evidence_file_not_found` or `test_file_not_found` | `Unable to find the file(s) for evaluation.` |
| test import failure | `test_import_error` | `Failed to import the necessary files.` |
| known unprocessable extension | `unprocessable_evidence_type` | `Evidence file extension '...' is not supported for evaluation.` |
| evidence load failure | `evidence_load_error` | `Error loading evidence:` |
| unhandled test exception | `test_execution_error` | `Failed to execute the evidence evaluation.` |
| Other exception | `evaluator_execution_error` | `Failed to execute the evidence evaluation.` |

Consumers should not infer success from exit status alone. For action evaluation, parse stdout JSON and inspect `results` and `evaluator`.

Do not conflate test-returned `error` outcomes with evaluator execution failures:

- a test can run and return `"error"`, which increments `summary.error`
- the evaluator can fail before or during execution, which increments `summary.message_error`
- a blocked execution can therefore have `summary.error == 0` while still containing evaluator `error` messages

Known unprocessable extensions do not attempt text fallback. Unknown extensions that are not on the unprocessable list still emit `unknown_extension_text_fallback` and may later emit `evidence_load_error` if the file cannot be decoded as text.

Example current behavior:

```bash
python main.py --evidence ./missing.json --test ./missing_test.py
echo $?
```

The evaluator can print JSON like this while still exiting successfully:

```json
{
  "results": [],
  "evaluator": {
    "messages": [
      {
        "level": "error",
        "source": "evaluator",
        "code": "evidence_file_not_found",
        "message": "Unable to find the file(s) for evaluation. ...",
        "evidence_file": "./missing.json",
        "test_file": "./verify_author_complete.py"
      }
    ],
    "summary": {
      "count": 1,
      "ran": 0,
      "pass": 0,
      "fail": 0,
      "inconclusive": 0,
      "error": 0,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 1
    }
  }
}
```

Treat this as the current evaluator behavior unless and until exit-status handling changes.

If a test-of-detail raises an unexpected exception, the evaluator still collapses that failure into structured evaluator JSON rather than returning arbitrary Python trace data as the process contract.

Evaluator messages now identify both sides of the execution context:

- `evidence_file`
- `test_file`

For evidence-level failures that happen before any test completes, the evaluator associates the message with each requested `test_file`.

## NAPE CLI Dependency

NAPE CLI report generation depends on:

- `nape-eval --check-install` succeeding.
- action evaluation printing valid JSON.
- JSON containing `results` and `evaluator`.

If the evaluator process exits non-zero or prints malformed JSON, NAPE CLI report generation can fail before writing a report.
