# Source Traceability

This reference maps documented evaluator behavior to source files.

## Traceability State

Current references in this document point to the active typed-evidence evaluator implementation.

Historical V1 behavior remains documented in `../product/v1-evaluator-baseline.md` for migration and comparison.

## Source Roots

| Source | Role |
| --- | --- |
| `main.py` | bootstrap entry point. |
| `src/nape_evaluator/application/io/cli.py` | CLI parsing, install check, argument validation, and stdout JSON emission. |
| `src/nape_evaluator/domain/use_cases.py` | evaluation orchestration and evaluator-level failure translation. |
| `src/nape_evaluator/domain/gateways.py` | domain-owned gateway seams and gateway-level failure type. |
| `src/nape_evaluator/application/driver/evidence_gateway.py` | concrete evidence loading, metadata creation, and loader-side warnings/errors. |
| `src/nape_evaluator/application/driver/test_of_detail_gateway.py` | concrete trusted test-of-detail loading implementation. |
| `src/nape_evaluator/application/io/output_contract.py` | output message and summary shaping. |
| `pyproject.toml` | package metadata, runtime dependencies, version, and `nape-eval` console script. |
| `Makefile` | local build, install, publish, and clean targets. |
| `tests/manual/` | current manual smoke entry point. |
| `tests/v1_baseline/` | historical V1 baseline smoke example. |
| `tests/` | automated loader and CLI validation plus shared fixtures. |

## Current Contract Source Map

| Behavior | Source |
| --- | --- |
| `--check-install` flag | `src/nape_evaluator/application/io/cli.py` |
| `--check-install` exclusivity with evaluation args | `src/nape_evaluator/application/io/cli.py` |
| `--evidence` argument | `src/nape_evaluator/application/io/cli.py` |
| `--test` argument | `src/nape_evaluator/application/io/cli.py` |
| no-argument usage and non-zero exit | `src/nape_evaluator/application/io/cli.py` |
| `--evidence` and `--test` paired validation | `src/nape_evaluator/application/io/cli.py` |
| repeated `--test` handling | `src/nape_evaluator/application/io/cli.py` |
| typed evidence loader by extension | `src/nape_evaluator/application/driver/evidence_gateway.py` |
| test-of-detail gateway seam | `src/nape_evaluator/domain/gateways.py` |
| dynamic test import implementation | `src/nape_evaluator/application/driver/test_of_detail_gateway.py` |
| `evaluate(evidence, metadata)` invocation | `src/nape_evaluator/domain/use_cases.py` |
| metadata contract creation | `src/nape_evaluator/application/driver/evidence_gateway.py` |
| stdout JSON serialization | `src/nape_evaluator/application/io/cli.py` |
| caught evaluator/runtime failures to `evaluator.messages` JSON output | `src/nape_evaluator/domain/use_cases.py` |
| package name `nape` | `pyproject.toml` |
| package version `2.0.0` | `pyproject.toml` |
| runtime dependencies `PyYAML` and `PyPDF2` | `pyproject.toml` |
| console script `nape-eval` | `pyproject.toml` |
| current manual smoke entry point | `tests/manual/author_test_2.sh` |
| manual JSON dict-based author example | `tests/json/test_of_detail/verify_author_complete.py` |
| historical V1 smoke entry point | `tests/v1_baseline/author_test.sh` |
| automated JSON CLI pass test | `tests/json/test_pass.py` |
| automated loader routing coverage | `tests/test_evidence_gateway_routing.py` |
| automated text loading coverage | `tests/test_text_evidence_loading.py` |
| automated structured loading coverage | `tests/test_structured_evidence_loading.py` |
| automated PDF loading coverage | `tests/test_pdf_evidence_loading.py` |
| automated unprocessable-format coverage | `tests/test_unprocessable_evidence.py` |

## Historical V1 Reference

Use `docs/product/v1-evaluator-baseline.md` when you need the old all-text evidence contract, historical examples, or the original V1-to-V2 compatibility analysis.

## Maintenance Rule

Keep permanent source references at file level unless a line number is unusually important. Line references go stale quickly in this small repository.
