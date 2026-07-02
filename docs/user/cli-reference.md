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

Execution contract:

- exact standalone `--check-install` prints plain text and returns exit status `0`
- every other invocation returns exit status `0` and prints one JSON object to stdout
- if the CLI is invoked with no evaluator arguments, it returns a request-scoped JSON `error` response instead of printing usage to stderr and exiting non-zero

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
      "message_count": 0,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 0
    }
  }
}
```

For malformed invocation input, the outer shape stays the same and `results` can be empty. Example:

```json
{
  "results": [],
  "evaluator": {
    "messages": [
      {
        "scope": "request",
        "level": "error",
        "source": "evaluator",
        "code": "cli_argument_error",
        "message": "No evaluator invocation arguments were provided. Use --check-install, or provide --evidence with --invoke/--invoke-file, or use --request-file.",
        "evidence_file": null,
        "test_file": null,
        "affected_tests": [],
        "stack_trace": null
      }
    ],
    "summary": {
      "count": 0,
      "ran": 0,
      "true": 0,
      "false": 0,
      "inconclusive": 0,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 1
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
- `inconclusive`: count for all `inconclusive` results, including blocked evaluator-synthesized ones
- `message_count`: total distinct evaluator event count
- `message_info`: evaluator `info` message count
- `message_warning`: evaluator `warning` message count
- `message_error`: evaluator `error` message count

Interpretation rules:

- evaluator/runtime failures are reported in `evaluator.messages` and counted in `summary.message_error`
- if `summary.ran` is less than `summary.count`, at least `summary.count - summary.ran` requested tests were blocked from execution
- shared evidence-side notices are represented once as request-scoped messages with `affected_tests`

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
- blocked tests carry evaluator-synthesized structured `result`

Completed `result` contains:

- `conclusion`
- `facts`
- `reason`

Ownership rule:

- `result.reason` is test-owned reasoning when the test completed
- `result.reason` is evaluator-owned reasoning when the invocation was blocked
- `evaluator.messages[*].message` is evaluator-owned operational context

Expected completed-test conclusions are:

- `true`
- `false`
- `inconclusive`

If a test returns an invalid result contract, the evaluator:

- still counts that test in `summary.ran`
- normalizes the completed result to `conclusion: "inconclusive"`
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
- `results[*].result.conclusion: "inconclusive"`
- one or more evaluator `error` messages
- `summary.message_error > 0`

Evaluator-generated operational notices are returned in `evaluator.messages`.

Each message contains:

- `scope`
- `level`
- `source`
- `code`
- `message`
- `evidence_file`
- `test_file`
- `affected_tests`
- `stack_trace`

Read evaluator messages as operational context, not as the test's claim or reasoning.

For request-scoped malformed-invocation errors, `affected_tests` can legitimately be `[]` when the CLI could not establish an accepted requested-test set.

## Multi-Test Example

If one evidence file is evaluated by two requested tests, the top-level `summary` aggregates across both result rows.

If both tests complete successfully:

- `summary.count` is `2`
- `summary.ran` is `2`
- the `true` / `false` / `inconclusive` totals reflect the two result rows

If the evidence loader also emits one shared warning that applies to both tests, the current runtime emits one request-scoped warning event. In that case:

- `summary.message_warning` is `1`
- `summary.message_count` is `1`
- the warning uses:
  - `scope: "request"`
  - `affected_tests: [...]`

## Blocked-Test Example

When a requested test is blocked before `evaluate(...)` completes:

- `results[*].execution.executed` is `false`
- `results[*].execution.status` is `blocked`
- `results[*].result.conclusion` is `inconclusive`
- `results[*].result.reason` is evaluator-generated blocked-result reasoning
- the operational explanation is returned in `evaluator.messages`
- `summary.message_error` increases
