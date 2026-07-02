# V2 Policy Direction

This document records the selected V2 policy direction for `nape-evaluator`.

These items now reflect implemented or selected product and contract decisions for the active V2 runtime.

## Purpose

Use this document to:

- keep major V2 contract decisions explicit
- give maintainers a stable basis for follow-on implementation and review
- distinguish settled V2 policy from older V1 historical behavior

## Selected V2 Decisions

### 1. Keep typed evidence loading as the canonical contract

Status:

- Implemented

Decision:

- keep typed evidence loading as the default evaluator behavior
- do not restore raw text-lines behavior as the default contract

Rationale:

- typed loading is the active documented behavior
- it produces a clearer test-of-detail authoring contract
- it keeps evidence translation inside the evaluator rather than duplicating parsing logic across tests

### 2. Validate returned completed-test conclusion vocabulary

Status:

- Implemented

Decision:

- validate returned completed-test conclusions against:
  - `true`
  - `false`
  - `inconclusive`
  - `error`

Handling:

- if a test returns an invalid result contract, treat the test as completed
- normalize that contract violation into a completed `error` result
- preserve `ran` accounting for that test

Rationale:

- invalid result shapes are test contract violations, not evaluator transport failures
- keeping them as completed `error` results preserves the distinction between:
  - test behavior problems
  - evaluator/runtime operational failures

### 3. Keep zero exit status when valid evaluator JSON is produced

Status:

- Selected

Decision:

- for evaluation invocations, keep exit status `0` whenever the evaluator successfully emits valid contract JSON
- reserve non-zero exit status for cases where the process cannot provide a valid evaluator contract reliably

### 4. Keep trusted-code execution explicit; do not promise a sandbox unless implemented

Status:

- Selected

Decision:

- continue to treat test-of-detail Python files as trusted executable code until a real sandbox exists
- do not imply stronger isolation than the product actually provides

## Relationship To Current Docs

Current runtime behavior remains documented in:

- `README.md`
- `docs/product/current-evaluator-reference.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/cli-reference.md`

Historical V1 behavior remains documented in:

- `docs/product/v1-evaluator-baseline.md`
