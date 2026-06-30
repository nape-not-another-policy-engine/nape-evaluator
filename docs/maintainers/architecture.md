# Architecture

`nape-eval` is intentionally small. It is a process boundary between NAPE CLI report generation and Python test-of-detail execution.

## Execution Flow

```text
nape-eval
  parse CLI args
  if --check-install:
    print health message
    exit
  require --evidence and --test together
  load evidence by extension
  dynamically import test file
  call evaluate(evidence)
  print {"outcome": ..., "reason": ...}
```

## Key Boundaries

CLI boundary:

- Implemented in `main.py`.
- Exposes `--check-install`, `--evidence`, and `--test`.

Evidence boundary:

- The evaluator loads evidence by file extension.
- Structured formats are parsed before `evaluate(evidence)` is called.

Test execution boundary:

- Test files are Python files loaded dynamically.
- Test files must define `evaluate(evidence)`.
- Test files execute in the local Python environment.

Output boundary:

- The only intended machine-readable output is JSON on stdout.
- NAPE CLI consumes `outcome` and `reason`.

## Error Model

The evaluator catches common failures and converts them to JSON `error` outcomes.

This means an evaluation problem can still produce process output that NAPE CLI treats as an action-level evaluator result.

Future releases can still revisit whether some failures should produce a non-zero process exit instead.

## Packaging

Package metadata lives in `pyproject.toml`.

The package name is `nape`; the console script is `nape-eval`.

Release targets live in `Makefile`.

## Historical Compatibility Risk

Typed evidence loading moved evidence parsing from test-of-detail files into evaluator core. That improves consistency but changes the authoring contract for older V1 tests that parsed JSON from text lines.
