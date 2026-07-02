> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 10: Clean-Install And Release Validation

## Purpose

Resume the future clean-install and release-validation workstream without re-deriving why it exists.

## Status

This workstream is complete.

The selected framing is:

- V2 is the current selected/runtime contract direction
- V2 should not be treated as already deployed
- this workstream is pre-deployment release-readiness validation

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/10-clean-install-and-release-validation.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/nape-evaluator-product-spec.md`
5. `docs/reference/evaluator-contract.md`
6. `docs/user/installation.md`
7. `docs/maintainers/local-development.md`
8. `pyproject.toml`
9. `scripts/docs_smoke.sh`

## Selected Starting Direction

- keep `--check-install` as a narrow base-CLI health check for now
- do not treat it as proof that typed evidence loaders and all runtime dependencies are healthy
- define a separate clean-install/release-validation procedure for the current V2 contract

## Completed Outputs

1. clean-install verification matrix
2. maintainer/release validation procedure
3. broader executable validation surface via `scripts/release_validation.sh`
4. packaging fixes required for fresh-environment install success:
   - resolvable `PyPDF2` dependency pin
   - working packaged console-script entry point
