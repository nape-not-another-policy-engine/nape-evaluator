# Architecture

`nape-eval` is intentionally small. It is a process boundary between NAPE CLI report generation and Python test-of-detail execution.

## V1 Execution Flow

```text
nape-eval
  parse CLI args
  if --check-install:
    print health message
    exit
  require --evidence and --test together
  read evidence as text lines
  dynamically import test file
  call evaluate(evidence_lines)
  print {"outcome": ..., "reason": ...}
```

## Key Boundaries

CLI boundary:

- Implemented in `main.py`.
- Exposes `--check-install`, `--evidence`, and `--test`.

Evidence boundary:

- V1 reads all evidence as text lines.
- V2 candidate work adds typed evidence loading by file extension.

Test execution boundary:

- Test files are Python files loaded dynamically.
- Test files must define `evaluate(evidence)`.
- Test files execute in the local Python environment.

Output boundary:

- The only intended machine-readable output is JSON on stdout.
- NAPE CLI consumes `outcome` and `reason`.

## Error Model

Committed V1 catches common failures and converts them to JSON `error` outcomes.

This means an evaluation problem can still produce process output that NAPE CLI treats as an action-level evaluator result.

V2 should decide whether any failure should produce a non-zero process exit instead.

## Packaging

Package metadata lives in `pyproject.toml`.

The package name is `nape`; the console script is `nape-eval`.

Release targets live in `Makefile`.

## V2 Candidate Architecture Change

Typed evidence loading moves evidence parsing from test-of-detail files into evaluator core. That improves consistency but changes the authoring contract.

Before accepting it, decide:

- Whether V1 text-line compatibility is required.
- Whether tests can request raw versus parsed evidence.
- Whether runtime dependencies are optional by file type or always installed.
- How docs expose the input type passed to `evaluate(evidence)`.
