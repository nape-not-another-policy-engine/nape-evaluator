# Source Traceability

This reference maps documented evaluator behavior to source files.

## Traceability State

V1 references in this document refer to committed `HEAD` behavior at the time of this documentation pass.

V2 candidate references refer to observed uncommitted worktree behavior at the time of this documentation pass.

After the current WIP is committed, reverted, or moved to a branch, update this document so it points to the new source-of-truth state rather than a generic dirty worktree.

## Source Roots

| Source | Role |
| --- | --- |
| `HEAD:main.py` | V1 CLI parsing, install check, text-line evidence loading, dynamic import, `evaluate(...)` invocation, JSON output, error handling. |
| dirty worktree `main.py` | V2 candidate typed-evidence loading and related error handling. |
| `HEAD:pyproject.toml` | V1 package metadata and `nape-eval` console script. |
| dirty worktree `pyproject.toml` | V2 candidate package version and dependency metadata changes. |
| `Makefile` | local build, install, publish, and clean targets. |
| `test/` | legacy manual examples. |
| `tests/` | candidate test package scaffolding in current worktree. |

## V1 Contract Source Map

| Behavior | Source |
| --- | --- |
| `--check-install` flag | `HEAD:main.py` |
| `--evidence` argument | `HEAD:main.py` |
| `--test` argument | `HEAD:main.py` |
| `--evidence` and `--test` paired validation | `HEAD:main.py` |
| evidence read as text lines | `HEAD:main.py` |
| dynamic test import | `HEAD:main.py` |
| `evaluate(evidence)` invocation | `HEAD:main.py` |
| stdout JSON serialization | `HEAD:main.py` |
| caught error to JSON `error` output | `HEAD:main.py` |
| package name `nape` | `HEAD:pyproject.toml` |
| console script `nape-eval` | `HEAD:pyproject.toml` |
| V1 manual author example | `test/verify_author_complete.py` |

## V2 Candidate Source Map

| Candidate behavior | Source |
| --- | --- |
| typed evidence loader by extension | observed dirty worktree `main.py` |
| JSON evidence parsed with `json.load` | observed dirty worktree `main.py` |
| XML evidence parsed with `xml.etree.ElementTree` | observed dirty worktree `main.py` |
| YAML evidence parsed with `yaml.safe_load` | observed dirty worktree `main.py` |
| PDF evidence parsed with `PyPDF2.PdfReader` | observed dirty worktree `main.py` |
| package version changed to `2.0.0` | dirty worktree `pyproject.toml` |
| typed JSON test example | dirty worktree `tests/json/test_of_detail/verify_author_complete.py` |

## Maintenance Rule

Keep permanent source references at file level unless a line number is unusually important. Line references go stale quickly in this small repository.
