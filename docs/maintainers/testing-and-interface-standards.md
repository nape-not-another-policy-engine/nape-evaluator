# Testing And Interface Standards

This document defines the repository-specific standards for test coverage and public interface documentation in `nape-evaluator`.

It adapts the Attestify software-quality, use-case, and slice-documentation guidance to this Python CLI repository.

## Related Documents

- `docs/maintainers/python-engineering-standards.md`
- `docs/maintainers/software-review.md`
- `docs/maintainers/architecture.md`
- `docs/reference/evaluator-contract.md`
- `docs/reference/evidence-formats.md`
- `docs/reference/source-traceability.md`
- `docs/user/cli-reference.md`
- `docs/user/test-of-detail-authoring.md`

## Purpose

These standards exist so that:

- meaningful logical paths are tested rather than assumed
- public evaluator behavior remains explicit and reviewable
- docs stay aligned across README, user docs, reference docs, and maintainer docs
- V1 historical material remains clearly separated from the current V2 contract

## Test Layout Standard

Tests are organized by bounded behavior surface:

- `tests/test_cli_contract.py`
  verifies end-to-end CLI behavior through `main.py`
- `tests/test_cli_adapter.py`
  verifies parser and transport behavior in `src/nape_evaluator/application/io/cli.py`
- `tests/test_request_builder.py`
  verifies request-builder validation in `src/nape_evaluator/domain/use_case_models.py`
- `tests/test_evaluator_use_case.py`
  verifies orchestration behavior in `src/nape_evaluator/domain/use_cases.py`
- `tests/test_evidence_gateway_routing.py`
  verifies evidence-loader routing and metadata behavior
- `tests/test_text_evidence_loading.py`
  verifies text loading and text-fallback behavior
- `tests/test_structured_evidence_loading.py`
  verifies JSON, XML, and YAML loading behavior
- `tests/test_pdf_evidence_loading.py`
  verifies PDF loading behavior
- `tests/test_unprocessable_evidence.py`
  verifies blocked binary-format behavior
- `tests/test_test_execution.py`
  verifies test-of-detail gateway behavior in `src/nape_evaluator/application/driver/test_of_detail_gateway.py`
- `tests/test_output_contract.py`
  verifies output shaping in `src/nape_evaluator/application/io/output_contract.py`

Supporting fixtures live under:

- `tests/json/`
- `tests/manual/`
- `tests/v1_baseline/`
- `tests/fixtures/`

Manual smoke examples belong under `tests/`, not a separate root-level `test/` tree.

## Logical Path Coverage Standard

Tests must cover meaningful logical paths for each bounded module. For this repository, that means:

| Surface | Required logical paths | Canonical tests |
| --- | --- | --- |
| CLI contract | install check, no-arg failure, direct-mode validation, `--request-file` behavior, JSON stdout contract | `tests/test_cli_contract.py`, `tests/test_cli_adapter.py` |
| Request builder | evidence validation, top-level `tests` validation, subject/data-type/criteria validation, compatibility validation | `tests/test_request_builder.py` |
| Evidence gateway | routing and metadata | `tests/test_evidence_gateway_routing.py` |
| Evidence gateway | text loading and text fallback | `tests/test_text_evidence_loading.py` |
| Evidence gateway | JSON, XML, and YAML behavior | `tests/test_structured_evidence_loading.py` |
| Evidence gateway | PDF behavior | `tests/test_pdf_evidence_loading.py` |
| Evidence gateway | known unprocessable extensions | `tests/test_unprocessable_evidence.py` |
| Test-of-detail gateway | dynamic module load success, missing file, import-spec failure | `tests/test_test_execution.py` |
| Use case orchestration | single-test success, multi-test success, completed-result normalization to `inconclusive`, evidence load failure, missing test file, import failure, evaluator execution failure, blocked synthesized `inconclusive`, request-scoped shared-message shaping, stack-trace capture | `tests/test_evaluator_use_case.py` |
| Output contract | completed versus blocked summary counts, distinct-event evaluator message counting, request-scoped versus test-scoped message shape, final JSON nesting | `tests/test_output_contract.py` |

Current logical-path documentation for the summary/message contract:

- `tests/test_output_contract.py`
  - full public message shape
  - blocked `inconclusive` counting
  - distinct request-scoped event counting
  - final CLI nesting
- `tests/test_evaluator_use_case.py`
  - completed-result normalization to `inconclusive`
  - request-scoped evidence warning affecting multiple tests
  - blocked evidence-load `inconclusive`
  - blocked test-execution `inconclusive`
  - stack-trace population on execution failure
- `tests/test_cli_contract.py`
  - blocked CLI-visible `inconclusive` result
  - request-scoped shared warning surfaced once in JSON output

Behaviorally distinct paths should not be left implicit in integration-only coverage if a bounded unit test can verify them directly.

## Public Interface Documentation Standard

Every public seam must have one clear documentation owner:

| Public seam | Primary documentation owner |
| --- | --- |
| install and entry-point overview | `README.md` and `docs/user/installation.md` |
| CLI flags and invocation rules | `docs/user/cli-reference.md` |
| test-of-detail author contract | `docs/user/test-of-detail-authoring.md` |
| evidence type and metadata contract | `docs/reference/evidence-formats.md` |
| result, message, and summary JSON contract | `docs/reference/evaluator-contract.md` |
| implementation ownership and runtime flow | `docs/maintainers/architecture.md` |
| source/file traceability | `docs/reference/source-traceability.md` |

Public behavior is not considered documented if it appears only in:

- tests
- inline comments
- temporary planning docs
- commit messages

## Documentation Update Rule

When any of these surfaces change, update the matching permanent docs in the same change:

- CLI flags or argument rules
- request packet shapes
- supported evidence types or fallback behavior
- metadata or caller-owned fields passed into `evaluate(evidence, evaluations, metadata)`
- output JSON shape
- trusted-code execution semantics
- install path or runtime dependencies
- historical baseline examples used for migration comparison

At minimum, a public contract change should review:

- `README.md`
- the relevant `docs/user/*` page
- the relevant `docs/reference/*` page
- `docs/maintainers/architecture.md`
- `docs/reference/source-traceability.md`

## Review Standard

Reviewers should be able to answer these questions quickly:

- What bounded behavior changed?
- Which logical path or paths prove it now works?
- Which permanent docs define the changed public behavior?
- Which examples or manual smoke artifacts illustrate the behavior?
- Is the V1 baseline impact explicit if compatibility changed?

If those answers are not obvious, the change is under-documented or under-tested.
