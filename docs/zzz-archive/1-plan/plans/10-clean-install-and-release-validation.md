> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 10: Clean-Install And Release Validation

## Goal

Define the pre-deployment release-validation work needed so the current V2 evaluator contract is verified in a clean install before wider rollout.

This plan is intentionally framed as pre-deployment validation work.

V2 has been selected and documented, but it has not yet been treated as already deployed.

## Why This Is Its Own Plan

The current evaluator contract now depends on more than base CLI startup:

- typed evidence loading
- runtime dependencies such as YAML and PDF support
- the V2 request packet contract
- the V2 result and message contract
- the zero-exit JSON evaluator invocation contract

`--check-install` still proves only that the CLI can start and that the entry point is present.

That is useful, but it is not enough to prove that a fresh installation can actually execute the current V2 evaluator contract across the supported evidence and request surfaces.

## Baseline

Read first:

1. `docs/1-plan/roadmap.md`
2. `docs/product/current-evaluator-reference.md`
3. `docs/product/nape-evaluator-product-spec.md`
4. `docs/product/v2-policy-direction.md`
5. `docs/product/v1-evaluator-baseline.md`
6. `docs/reference/evaluator-contract.md`
7. `docs/user/installation.md`
8. `docs/maintainers/local-development.md`
9. `pyproject.toml`
10. `scripts/docs_smoke.sh`

## Selected Starting Direction

Starting recommendation:

- keep `--check-install` as a narrow base-CLI health check for now
- do not redefine it as proof that all typed-loader/runtime paths are healthy
- create a separate clean-install validation surface for release confidence

This keeps operator expectations honest.

It avoids overloading `--check-install` with guarantees the current command does not actually provide.

## Primary Questions

This plan should answer:

1. What exact runtime behaviors must pass in a clean install before V2 is considered releasable?
2. Which supported evidence types must be verified explicitly?
3. Which request/response contract paths should be included in release validation?
4. Should release validation stay as maintainer procedure only, or should some of it become an automated smoke target?
5. Should `--check-install` remain unchanged, or should a later broader health-check command be added?

## Expected Scope

At minimum:

- define a clean-install verification matrix for:
  - `.txt`
  - `.json`
  - `.xml`
  - `.yaml` / `.yml`
  - `.pdf`
- verify runtime dependency-backed evidence paths in a fresh environment
- verify at least one normal V2 invocation path
- verify at least one blocked/error JSON path under the zero-exit contract
- document what `--check-install` does and does not guarantee
- update release/maintainer docs with the selected validation procedure

## Status

Complete.

This plan should not assume V2 has already been deployed.

It should be treated as release-readiness and install-validation work for the current V2 contract.

## Validation Matrix

The first-pass validation matrix for this plan is:

| Surface | Purpose | Expected outcome |
| --- | --- | --- |
| standalone `--check-install` | prove entry point starts | exit `0`, plain-text health message |
| direct mode with inline `--invoke` | prove core V2 evaluation path | exit `0`, stdout JSON, `summary.true == 1` |
| direct mode with `--invoke-file` | prove file-backed single-invocation transport | exit `0`, stdout JSON, `summary.true == 1` |
| full-request mode with `--request-file` | prove full outer packet transport | exit `0`, stdout JSON, `summary.true == 1` |
| `.txt` evidence | prove text-line loader path | exit `0`, stdout JSON, `summary.true == 1`, `metadata.evidence_type == "text"` as validated by the test |
| `.json` evidence | prove JSON loader path | exit `0`, stdout JSON, `summary.true == 1`, `metadata.evidence_type == "json"` as validated by the test |
| `.xml` evidence | prove XML loader path | exit `0`, stdout JSON, `summary.true == 1`, `metadata.evidence_type == "xml"` as validated by the test |
| `.yaml` evidence | prove YAML loader path and dependency availability | exit `0`, stdout JSON, `summary.true == 1`, `metadata.evidence_type == "yaml"` as validated by the test |
| `.pdf` evidence | prove PDF loader path and dependency availability | exit `0`, stdout JSON, `summary.true == 1`, `metadata.evidence_type == "pdf"` as validated by the test |
| malformed request JSON | prove request-boundary zero-exit JSON error behavior | exit `0`, stdout JSON, `results == []`, request-scoped evaluator `error` |
| missing evidence path | prove blocked evaluator-owned error behavior | exit `0`, stdout JSON, `summary.ran == 0`, blocked `inconclusive`, evaluator `message_error == 1` |

## Planned Durable Outputs

1. executable validation script
2. maintainer-facing release-validation procedure
3. install-doc clarification that `--check-install` is narrower than full typed-loader validation

## Implemented Outcome

This plan is now closed with these implemented results:

- `scripts/release_validation.sh` provides an executable validation matrix
- `docs/maintainers/release-validation.md` defines the maintainer/release procedure
- `docs/user/installation.md` now clarifies the narrow guarantee of `--check-install`
- the matrix passes in repository-runtime preflight mode through `python3 main.py`
- the matrix also passes from a fresh virtual-environment install using the packaged `nape-eval` command
- the work uncovered and fixed two release blockers:
  - `PyPDF2~=5.4.0` was not installable from the available package index surface, so it was corrected to a resolvable `PyPDF2~=3.0.1`
  - the console-script entry point targeted a non-packaged `main` module, so it was corrected to `nape_evaluator.main:main`
