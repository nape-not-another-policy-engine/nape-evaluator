# CLI Reference

`nape-eval` evaluates one evidence file against one or more Python test-of-detail files.

## Commands

### `--check-install`

```bash
nape-eval --check-install
```

Prints:

```text
NAPE Evaluator CLI is installed and working.
```

`--check-install` cannot be combined with `--evidence` or `--test`.

### `--evidence` And `--test`

```bash
nape-eval --evidence <evidence-file> --test <test-of-detail-python-file>
```

Repeat `--test` to evaluate multiple tests against the same evidence file:

```bash
nape-eval --evidence <evidence-file> --test <test-a.py> --test <test-b.py>
```

`--evidence` and at least one `--test` must be provided together.

If the CLI is invoked with no arguments, it prints usage information to stderr and exits non-zero.

## Arguments

| Argument | Required | Description |
| --- | --- | --- |
| `--check-install` | No | Verifies the CLI can run. |
| `--evidence` | Yes for evaluation | Path to one evidence file. |
| `--test` | Yes for evaluation | Path to one Python file with an `evaluate(evidence, metadata)` function. Repeat to run multiple tests. |

## Output

The evaluator prints one JSON object to stdout:

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

For multiple tests, the evaluator prints:

```json
{
  "results": [
    {
      "test": "test-a.py",
      "outcome": "pass",
      "reason": "Reason text"
    },
    {
      "test": "test-b.py",
      "outcome": "fail",
      "reason": "Reason text"
    }
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 2,
      "ran": 2,
      "pass": 1,
      "fail": 1,
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

Top-level fields:

- `results`
- `evaluator`

Summary fields:

- `count`: how many tests were requested
- `ran`: how many tests actually completed the `evaluate(...)` contract
- `pass`: result count for tests that returned `pass`
- `fail`: result count for tests that returned `fail`
- `inconclusive`: result count for tests that returned `inconclusive`
- `error`: result count for tests that returned `error`
- `message_count`: total evaluator message count
- `message_info`: evaluator `info` message count
- `message_warning`: evaluator `warning` message count
- `message_error`: evaluator `error` message count

Interpretation rules:

- `summary.error` is reserved for result-level `"error"` outcomes returned by tests that actually ran.
- Evaluator/runtime failures are reported in `evaluator.messages` and counted in `summary.message_error`.
- If `summary.ran` is less than `summary.count`, at least `summary.count - summary.ran` requested tests were blocked from execution.

## Outcomes

The evaluator prints whatever outcome the test-of-detail function returns.

Expected NAPE outcome values are:

- `pass`
- `fail`
- `inconclusive`
- `error`

The evaluator validates this list before printing output.

If a test returns any other value, the evaluator:

- keeps the test in `summary.ran`
- normalizes the result to `outcome: "error"`
- returns a reason explaining that the outcome was unsupported

## Error Output

When the evaluator catches a process-level failure, it prints:

```json
{
  "results": [],
  "evaluator": {
    "messages": [
      {
        "level": "error",
        "source": "evaluator",
        "code": "evidence_load_error",
        "message": "...",
        "evidence_file": "./evidence.json",
        "test_file": "./test-a.py"
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

Common failures:

- missing evidence file
- missing test file
- known unprocessable evidence type
- evidence parsing failure
- import failure
- exception raised while executing `evaluate(...)`

When multiple tests are supplied, import or execution failure in one test is associated with that `test_file` in `evaluator.messages` and does not stop the remaining tests from running.

This means a blocked evaluation can legitimately produce:

- `results: []`
- `summary.error: 0`
- one or more evaluator `error` messages
- `summary.message_error > 0`

Evaluator-generated operational notices are returned in `evaluator.messages`.

Each message contains:

- `level`
- `source`
- `code`
- `message`
- `evidence_file`
- `test_file`

Warning example for a file with no extension:

```json
{
  "results": [
    {
      "test": "text_test.py",
      "outcome": "pass",
      "reason": "Text evaluated."
    }
  ],
  "evaluator": {
    "messages": [
      {
        "level": "warning",
        "source": "evaluator",
        "code": "missing_extension_text_fallback",
        "message": "Evidence file had no extension and was evaluated as text.",
        "evidence_file": "./evidence",
        "test_file": "./text_test.py"
      }
    ],
    "summary": {
      "count": 1,
      "ran": 1,
      "pass": 1,
      "fail": 0,
      "inconclusive": 0,
      "error": 0,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 1,
      "message_error": 0
    }
  }
}
```

Error example for a known unprocessable extension such as `.png`:

```json
{
  "results": [],
  "evaluator": {
    "messages": [
      {
        "level": "error",
        "source": "evaluator",
        "code": "unprocessable_evidence_type",
        "message": "Evidence file extension '.png' is not supported for evaluation.",
        "evidence_file": "./image.png",
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

Known unprocessable extensions currently include common image, archive, media, and executable formats. Unknown extensions that are not on that denylist still use the warning-plus-text-fallback path.

If evaluation stops before any test completes, the evaluator still associates each message with the requested `test_file` so callers can see which requested runs were blocked.

The evaluator may still exit successfully after printing JSON output that includes evaluator `error` messages. Consumers should inspect `results` and `evaluator` instead of relying on process exit status alone.

## NAPE CLI Integration

NAPE CLI invokes:

```bash
nape-eval --check-install
nape-eval --evidence <evidence-file> --test <test-file>
nape-eval --evidence <evidence-file> --test <test-a.py> --test <test-b.py>
```

NAPE CLI expects valid JSON on stdout for action evaluation.
