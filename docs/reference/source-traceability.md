# Source Traceability

This reference maps documented evaluator behavior to source files.

## Traceability State

This document maps the current committed V2 implementation.

Historical V1 behavior remains documented in `../product/v1-evaluator-baseline.md` for migration and comparison.

## Source Roots

| Source | Role |
| --- | --- |
| `main.py` | bootstrap entry point. |
| `src/nape_evaluator/application/io/cli.py` | CLI parsing, install check, argument validation, request-packet decoding, and stdout JSON emission. |
| `src/nape_evaluator/domain/use_cases.py` | evaluation orchestration and evaluator-level failure translation. |
| `src/nape_evaluator/domain/use_case_models.py` | bounded request models, request builder, and evaluator response validation. |
| `src/nape_evaluator/domain/gateways.py` | domain-owned gateway seams and gateway-level failure type. |
| `src/nape_evaluator/application/driver/evidence_gateway.py` | concrete evidence loading, metadata creation, and loader-side warnings/errors. |
| `src/nape_evaluator/application/driver/test_of_detail_gateway.py` | concrete trusted test-of-detail loading implementation. |
| `src/nape_evaluator/application/io/output_contract.py` | output message and summary shaping. |
| `pyproject.toml` | package metadata, runtime dependencies, version, and `nape-eval` console script. |
| `Makefile` | local build, install, publish, and clean targets. |
| `tests/manual/` | manual smoke entry points. |
| `tests/v1_baseline/` | historical V1 baseline smoke example. |
| `tests/` | automated CLI, use-case, loader, and contract tests. |

## Current Contract Source Map

| Behavior | Source |
| --- | --- |
| `--check-install` flag | `src/nape_evaluator/application/io/cli.py` |
| `--check-install` exclusivity with evaluation args | `src/nape_evaluator/application/io/cli.py` |
| direct-mode `--evidence` argument | `src/nape_evaluator/application/io/cli.py` |
| repeated `--invoke` and `--invoke-file` arguments | `src/nape_evaluator/application/io/cli.py` |
| `--request-file` argument, file-path mode, and stdin mode via `-` | `src/nape_evaluator/application/io/cli.py` |
| no-argument zero-exit JSON request error | `src/nape_evaluator/application/io/cli.py` |
| direct-mode validation rules | `src/nape_evaluator/application/io/cli.py` |
| full-request decoding and top-level `tests` handling | `src/nape_evaluator/application/io/cli.py` |
| request-scoped CLI invocation error translation | `src/nape_evaluator/application/io/cli.py`, `src/nape_evaluator/application/io/output_contract.py`, `src/nape_evaluator/domain/use_case_models.py` |
| request builder seam and request validation | `src/nape_evaluator/domain/use_case_models.py` |
| supported `subject.data_type` vocabulary | `src/nape_evaluator/domain/use_case_models.py` |
| supported `criteria` vocabulary and compatibility rules | `src/nape_evaluator/domain/use_case_models.py` |
| typed evidence loader by extension | `src/nape_evaluator/application/driver/evidence_gateway.py` |
| test-of-detail gateway seam | `src/nape_evaluator/domain/gateways.py` |
| dynamic test import implementation | `src/nape_evaluator/application/driver/test_of_detail_gateway.py` |
| `evaluate(evidence, evaluations, metadata)` invocation | `src/nape_evaluator/domain/use_cases.py` |
| completed-result normalization and response validation | `src/nape_evaluator/domain/use_case_models.py`, `src/nape_evaluator/domain/use_cases.py` |
| outer result fields `test`, `evidence`, `evaluations`, `execution`, and `result` | `src/nape_evaluator/domain/use_cases.py` |
| evaluator message shaping and summary counts | `src/nape_evaluator/application/io/output_contract.py` |
| stdout JSON serialization | `src/nape_evaluator/application/io/cli.py` |
| caught evaluator/runtime failures to `evaluator.messages` JSON output | `src/nape_evaluator/domain/use_cases.py` |
| package name `nape` | `pyproject.toml` |
| package version `2.0.0` | `pyproject.toml` |
| runtime dependencies `PyYAML` and `PyPDF2` | `pyproject.toml` |
| console script `nape-eval` | `pyproject.toml` |
| current manual smoke entry point | `tests/manual/author_test_2.sh` |
| current sample V2 test-of-detail | `tests/json/test_of_detail/verify_author_complete.py` |
| historical V1 smoke entry point | `tests/v1_baseline/author_test.sh` |
| automated JSON CLI pass test | `tests/json/test_pass.py` |
| automated CLI transport coverage | `tests/test_cli_contract.py`, `tests/test_cli_adapter.py` |
| automated request-builder coverage | `tests/test_request_builder.py` |
| automated use-case orchestration coverage | `tests/test_evaluator_use_case.py` |
| automated loader routing coverage | `tests/test_evidence_gateway_routing.py` |
| automated text loading coverage | `tests/test_text_evidence_loading.py` |
| automated structured loading coverage | `tests/test_structured_evidence_loading.py` |
| automated PDF loading coverage | `tests/test_pdf_evidence_loading.py` |
| automated unprocessable-format coverage | `tests/test_unprocessable_evidence.py` |

## Historical V1 Reference

Use `docs/product/v1-evaluator-baseline.md` when you need the old all-text evidence contract, older transport examples, or the original V1-to-V2 compatibility analysis.

## Maintenance Rule

Keep permanent source references at file level unless a line number is unusually important. Line references go stale quickly in this small repository.
