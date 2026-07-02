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

`--check-install` cannot be combined with `--evidence`, `--invoke`, `--invoke-file`, or `--request-file`.

### Direct Invocation Mode

Inline invocation packets:

```bash
nape-eval \
  --evidence <evidence-file> \
  --invoke '{"test":"./test.py","evaluations":[]}'
```

File-based invocation packets:

```bash
nape-eval \
  --evidence <evidence-file> \
  --invoke-file <invoke-a.json> \
  --invoke-file <invoke-b.json>
```

Rules:

- `--evidence` is required in direct mode
- use one or more `--invoke` and/or `--invoke-file`
- each repeated value represents exactly one test invocation packet
- each invocation packet contains both:
  - `test`
  - `evaluations`

### Full-Request Mode

```bash
nape-eval --request-file <request.json>
nape-eval --request-file -
```

Rules:

- `--request-file` accepts one full outer request packet
- `--request-file -` reads that full outer request packet from stdin
- `--request-file` cannot be combined with `--evidence`, `--invoke`, or `--invoke-file`

If the CLI is invoked with no arguments, it prints usage information to stderr and exits non-zero.

## Arguments

| Argument | Required | Description |
| --- | --- | --- |
| `--check-install` | No | Verifies the CLI can run. |
| `--evidence` | Yes in direct mode | Path to one evidence file. |
| `--invoke` | No | One JSON object containing `test` and `evaluations` for a single test invocation. Repeat as needed. |
| `--invoke-file` | No | Path to one JSON object file containing `test` and `evaluations` for a single test invocation. Repeat as needed. |
| `--request-file` | Yes in full-request mode | Path to one full JSON request packet, or `-` for stdin. |

## Request Shapes

Single invocation packet:

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

Full request packet:

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

## Output

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

Top-level fields:

- `results`
- `evaluator`

Summary fields:

- `count`: how many tests were requested
- `ran`: how many tests completed the `evaluate(...)` contract
- `true`: completed-test count for `conclusion: "true"`
- `false`: completed-test count for `conclusion: "false"`
- `inconclusive`: completed-test count for `conclusion: "inconclusive"`
- `error`: completed-test count for `conclusion: "error"`
- `message_count`: total evaluator message count
- `message_info`: evaluator `info` message count
- `message_warning`: evaluator `warning` message count
- `message_error`: evaluator `error` message count

Interpretation rules:

- `summary.error` is reserved for completed tests that returned `conclusion: "error"`
- evaluator/runtime failures are reported in `evaluator.messages` and counted in `summary.message_error`
- if `summary.ran` is less than `summary.count`, at least `summary.count - summary.ran` requested tests were blocked from execution

## Result Semantics

Each `results[*]` item contains:

- `test`
- `evidence`
- `evaluations`
- `execution`
- `result`

`execution` contains:

- `executed`
- `status`

Rules:

- `execution.status` is `completed` when `execution.executed` is `true`
- `execution.status` is `blocked` when `execution.executed` is `false`
- completed tests carry structured `result`
- blocked tests carry `result: null`

Completed `result` contains:

- `conclusion`
- `facts`
- `reason`

Expected completed-test conclusions are:

- `true`
- `false`
- `inconclusive`
- `error`

If a test returns an invalid result contract, the evaluator:

- still counts that test in `summary.ran`
- normalizes the completed result to `conclusion: "error"`
- returns an explanatory `reason`

## Error Output

Common evaluator-owned failures:

- missing evidence file
- unprocessable evidence type
- evidence parsing failure
- missing test file
- import failure
- exception raised while executing `evaluate(...)`

Blocked evaluations can legitimately produce:

- `results[*].execution.executed: false`
- `results[*].result: null`
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
