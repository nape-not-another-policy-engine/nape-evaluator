# CLI Reference

`nape-eval` evaluates one evidence file against one Python test-of-detail file.

## Commands

### `--check-install`

```bash
nape-eval --check-install
```

Prints:

```text
NAPE Evaluator CLI is installed and working.
```

### `--evidence` And `--test`

```bash
nape-eval --evidence <evidence-file> --test <test-of-detail-python-file>
```

Both arguments must be provided together.

## Arguments

| Argument | Required | Description |
| --- | --- | --- |
| `--check-install` | No | Verifies the CLI can run. |
| `--evidence` | Yes for evaluation | Path to one evidence file. |
| `--test` | Yes for evaluation | Path to one Python file with an `evaluate(evidence)` function. |

## Output

The evaluator prints JSON to stdout:

```json
{"outcome": "pass", "reason": "Reason text"}
```

Expected fields:

- `outcome`
- `reason`

## Outcomes

The evaluator prints whatever outcome the test-of-detail function returns.

Expected NAPE outcome values are:

- `pass`
- `fail`
- `inconclusive`
- `error`

V1 does not validate this list before printing output.

## Error Output

When V1 catches a failure, it prints:

```json
{"outcome": "error", "reason": "..."}
```

Common failures:

- missing evidence file
- missing test file
- import failure
- exception raised while executing `evaluate(...)`

Committed V1 may still exit successfully after printing JSON `error` output. Consumers should inspect the JSON `outcome` field instead of relying on process exit status alone.

## NAPE CLI Integration

NAPE CLI invokes:

```bash
nape-eval --check-install
nape-eval --evidence <evidence-file> --test <test-file>
```

NAPE CLI expects valid JSON on stdout for action evaluation.
