# Architecture

`nape-eval` is intentionally small. It is a process boundary between NAPE CLI report generation and Python test-of-detail execution.

## Execution Flow

```text
nape-eval
  parse CLI args
  if no args:
    print usage
    exit non-zero
  if --check-install:
    print health message
    exit
  reject --check-install with --evidence, --test, or --test-parameters-file
  require --evidence and --test together
  validate repeated --test-parameters-file count when present
  load parameter files into per-test invocation requests
  resolve loader strategy by extension
  load evidence and build metadata
  for each requested test invocation:
    dynamically import test file
    call evaluate(evidence, test_parameters, metadata)
    collect result or evaluator message
  print {"results": [...], "evaluator": {...}}
```

## Key Boundaries

CLI boundary:

- Implemented by `src/nape_evaluator/application/io/cli.py`.
- `main.py` is bootstrap-only and delegates to `run_cli()`.
- Exposes `--check-install`, `--evidence`, `--test`, and `--test-parameters-file`.
- Rejects `--check-install` if combined with evaluation arguments.
- Prints usage and exits non-zero when invoked without arguments.
- Owns direct CLI parameter-file decoding and per-test invocation construction.

Use-case boundary:

- Implemented by `src/nape_evaluator/domain/use_cases.py`.
- Uses request/result models from `src/nape_evaluator/domain/use_case_models.py`.
- Defines gateway seams in `src/nape_evaluator/domain/gateways.py` using Python `Protocol`s.
- Owns end-to-end evaluation orchestration for one evidence file and one or more test files.
- Treats each requested test as its own invocation context with optional caller-owned parameters.
- Aggregates result records and evaluator messages into the final output object.

Evidence boundary:

- Implemented by `src/nape_evaluator/application/driver/evidence_gateway.py`.
- The evaluator loads evidence by file extension.
- The evaluator builds metadata alongside the loaded evidence.
- Structured formats are parsed before `evaluate(evidence, test_parameters, metadata)` is called.

Test execution boundary:

- Implemented through the test-of-detail gateway seam defined in `src/nape_evaluator/domain/gateways.py`.
- Concrete driver implementation lives in `src/nape_evaluator/application/driver/test_of_detail_gateway.py`.
- Test files are Python files loaded dynamically.
- Test files must define `evaluate(evidence, test_parameters, metadata)`.
- Test files execute in the local Python environment.
- One evidence file can be evaluated against one or more repeated `--test` arguments in a single invocation.
- Each test can also receive caller-owned parameters through a matched `--test-parameters-file`.

Output boundary:

- Implemented by `src/nape_evaluator/application/io/output_contract.py`.
- The only intended machine-readable output is JSON on stdout.
- Output contains:
  - `results`
  - `evaluator.messages`
  - `evaluator.summary`
- The evaluator emits one result item per requested test invocation.
- Evaluator/runtime failures are reported through `evaluator.messages`.
- Result context includes `evidence_file`, `test_parameters`, `test_parameters_source`, and `executed`.
- Message context includes `test_parameters_source`.

## Error Model

The evaluator catches common failures and converts them to evaluator `error` messages.

Returned test outcome `"error"` and evaluator/runtime failure are intentionally distinct:

- returned `"error"` with `executed == true` increments `evaluator.summary.error`
- blocked invocations still appear in `results` with `executed == false`
- evaluator/runtime failures increment `evaluator.summary.message_error`
- blocked tests can leave `evaluator.summary.ran` below `evaluator.summary.count`

This means an evaluation problem can still produce JSON output even when one or more requested tests never complete.

Future releases can still revisit whether some failures should produce a non-zero process exit instead.

## Packaging

Package metadata lives in `pyproject.toml`.

The package name is `nape`; the console script is `nape-eval`.

Release targets live in `Makefile`.

The repository uses a `src/` layout. Importable package code lives under `src/nape_evaluator/`.

Root repository layout is intentionally stabilized as:

- `docs/`
- `src/`
- `tests/`

## Current Module Ownership

- `main.py`: bootstrap entry point only
- `src/nape_evaluator/application/io/cli.py`: CLI parser construction, argument validation, parameter-file decoding, and stdout contract emission
- `src/nape_evaluator/application/io/output_contract.py`: output message and summary shaping
- `src/nape_evaluator/application/driver/evidence_gateway.py`: concrete evidence gateway implementation
- `src/nape_evaluator/application/driver/test_of_detail_gateway.py`: concrete test-of-detail gateway implementation
- `src/nape_evaluator/domain/use_case_models.py`: bounded use-case request/result models
- `src/nape_evaluator/domain/use_cases.py`: evaluation orchestration
- `src/nape_evaluator/domain/gateways.py`: domain-owned gateway seams and domain-level gateway failure type

## Historical Compatibility Risk

Typed evidence loading moved evidence parsing from test-of-detail files into evaluator core. That improves consistency but changes the authoring contract for older V1 tests that parsed JSON from text lines.

The current parameter feature also changes the test signature from two arguments to three: `evaluate(evidence, test_parameters, metadata)`.
