# Source Traceability

This reference maps documented evaluator behavior to source files.

## Traceability State

Current references in this document point to the active typed-evidence evaluator implementation.

Historical V1 behavior remains documented in `../product/v1-evaluator-baseline.md` for migration and comparison.

## Source Roots

| Source | Role |
| --- | --- |
| `main.py` | CLI parsing, install check, typed evidence loading, dynamic import, `evaluate(...)` invocation, JSON output, and error handling. |
| `pyproject.toml` | package metadata, runtime dependencies, version, and `nape-eval` console script. |
| `Makefile` | local build, install, publish, and clean targets. |
| `test/` | manual smoke examples, including the JSON dict-based V2 author example. |
| `tests/` | automated loader and CLI validation. |

## Current Contract Source Map

| Behavior | Source |
| --- | --- |
| `--check-install` flag | `main.py` |
| `--evidence` argument | `main.py` |
| `--test` argument | `main.py` |
| `--evidence` and `--test` paired validation | `main.py` |
| typed evidence loader by extension | `main.py` |
| dynamic test import | `main.py` |
| `evaluate(evidence)` invocation | `main.py` |
| stdout JSON serialization | `main.py` |
| caught error to JSON `error` output | `main.py` |
| package name `nape` | `pyproject.toml` |
| package version `2.0.0` | `pyproject.toml` |
| runtime dependencies `PyYAML` and `PyPDF2` | `pyproject.toml` |
| console script `nape-eval` | `pyproject.toml` |
| manual JSON dict-based author example | `test/verify_author_complete_2.py` |
| automated JSON CLI pass test | `tests/json/test_pass.py` |
| automated loader coverage | `tests/test_load_evidence.py` |

## Historical V1 Reference

Use `docs/product/v1-evaluator-baseline.md` when you need the old all-text evidence contract, historical examples, or the original V1-to-V2 compatibility analysis.

## Maintenance Rule

Keep permanent source references at file level unless a line number is unusually important. Line references go stale quickly in this small repository.
