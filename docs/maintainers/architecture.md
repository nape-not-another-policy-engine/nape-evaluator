# Architecture

`nape-eval` is intentionally small. It is a process boundary between NAPE CLI report generation and Python test-of-detail execution.

This document describes the current committed implementation architecture.

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
  reject --check-install with evaluation args
  if direct mode:
    require --evidence
    require one or more --invoke/--invoke-file packets
    decode invocation packets
  if full-request mode:
    decode one outer request packet from path or stdin
  build EvaluateEvidenceRequest through builder().try_build()
  load evidence and build metadata
  for each requested test invocation:
    dynamically import test file
    call evaluate(evidence, evaluations, metadata)
    collect completed result or evaluator message
  validate/normalize completed result shape
  print {"results": [...], "evaluator": {...}}
```

## Key Boundaries

CLI boundary:

- Implemented by `src/nape_evaluator/application/io/cli.py`.
- `main.py` is bootstrap-only and delegates to `run_cli()`.
- Exposes `--check-install`, `--evidence`, `--invoke`, `--invoke-file`, and `--request-file`.
- Rejects invalid flag combinations before use-case execution.
- Owns request-packet decoding and boundary transport rules.

Use-case boundary:

- Implemented by `src/nape_evaluator/domain/use_cases.py`.
- Uses request/result models from `src/nape_evaluator/domain/use_case_models.py`.
- Defines gateway seams in `src/nape_evaluator/domain/gateways.py` using Python `Protocol`s.
- Owns end-to-end evaluation orchestration for one evidence file and one or more test invocations.
- Treats each requested test as its own invocation context.
- Aggregates result records and evaluator messages into the final output object.

Request seam:

- Implemented by `EvaluateEvidenceRequest` and `EvaluateEvidenceRequestBuilder`.
- The builder validates caller-owned input before the use case runs.
- The built request is the accepted use-case boundary object.

Evidence boundary:

- Implemented by `src/nape_evaluator/application/driver/evidence_gateway.py`.
- The evaluator loads evidence by file extension.
- The evaluator builds metadata alongside the loaded evidence.
- Structured formats are parsed before `evaluate(evidence, evaluations, metadata)` is called.

Test execution boundary:

- Implemented through the test-of-detail gateway seam defined in `src/nape_evaluator/domain/gateways.py`.
- Concrete driver implementation lives in `src/nape_evaluator/application/driver/test_of_detail_gateway.py`.
- Test files are Python files loaded dynamically.
- Test files must define `evaluate(evidence, evaluations, metadata)`.
- Test files execute in the local Python environment.

Output boundary:

- Implemented by `src/nape_evaluator/application/io/output_contract.py`.
- The only intended machine-readable output is JSON on stdout.
- Output contains:
  - `results`
  - `evaluator.messages`
  - `evaluator.summary`
- The evaluator emits one result item per requested test invocation.
- Evaluator/runtime failures are reported through `evaluator.messages`.
- Result context includes `test`, `evidence`, `evaluations`, `execution`, and `result`.

## Error Model

The evaluator catches common failures and converts them to evaluator `error` messages.

Blocked/evaluator-synthesized `conclusion: "inconclusive"` and evaluator/runtime failure are intentionally distinct:

- blocked invocations still appear in `results` with `execution.executed == false`
- blocked invocations now carry structured `result` with `conclusion: "inconclusive"`
- evaluator/runtime failures increment `evaluator.summary.message_error`
- blocked tests can leave `evaluator.summary.ran` below `evaluator.summary.count`
- shared evidence-side notices are emitted once as request-scoped evaluator messages with `affected_tests`

This means an evaluation problem can still produce valid JSON output even when one or more requested tests never complete.

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
- `src/nape_evaluator/application/io/cli.py`: CLI parser construction, argument validation, request-packet decoding, and stdout contract emission
- `src/nape_evaluator/application/io/output_contract.py`: output message and summary shaping
- `src/nape_evaluator/application/driver/evidence_gateway.py`: concrete evidence gateway implementation
- `src/nape_evaluator/application/driver/test_of_detail_gateway.py`: concrete test-of-detail gateway implementation
- `src/nape_evaluator/domain/use_case_models.py`: bounded use-case request/result models and request/response validation
- `src/nape_evaluator/domain/use_cases.py`: evaluation orchestration
- `src/nape_evaluator/domain/gateways.py`: domain-owned gateway seams and domain-level gateway failure type

## Historical Compatibility Risk

Typed evidence loading moved evidence parsing from test-of-detail files into evaluator core. The V2 cutover also replaced older parameter-based transport and tuple-returning test contracts.

Tests written for V1 or early transitional shapes may need migration.
