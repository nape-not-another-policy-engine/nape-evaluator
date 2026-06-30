# V2 Policy Direction

This document records the recommended V2 policy direction for `nape-evaluator`.

These items are product and contract decisions for the next major version. They are not claims that the current implementation already behaves this way.

## Purpose

Use this document to:

- turn open V1-to-V2 questions into explicit policy direction
- give maintainers a stable basis for V2 implementation planning
- distinguish current behavior from recommended next behavior

## Recommended V2 Decisions

### 1. Keep typed evidence loading as the canonical contract

Status:

- Implemented

Decision:

- keep typed evidence loading as the default evaluator behavior
- do not restore raw text-lines behavior as the default contract

Rationale:

- typed loading is already the active documented behavior
- it produces a clearer test-of-detail authoring contract
- it keeps evidence translation inside the evaluator rather than duplicating parsing logic across tests

Tradeoffs:

- pro:
  - more consistent test inputs
  - less repeated parsing logic in test-of-detail files
  - clearer maintainership and traceability
- con:
  - older V1 tests that parsed JSON from text lines require migration

Compatibility direction:

- if legacy compatibility is needed later, prefer an explicit opt-in compatibility mode rather than silent default fallback

### 2. Validate returned outcome vocabulary in V2

Status:

- Implemented

Decision:

- V2 should validate returned outcomes against:
  - `pass`
  - `fail`
  - `inconclusive`
  - `error`

Recommended handling:

- if a test returns an invalid outcome, treat the test as completed
- convert that contract violation into a result-level `error`
- preserve `ran` accounting for that test

Rationale:

- invalid outcome values are test contract violations, not evaluator transport failures
- keeping them as result-level errors preserves the distinction between:
  - test behavior problems
  - evaluator/runtime operational failures

Tradeoffs:

- pro:
  - tighter contract safety
  - clearer downstream interpretation
  - no ambiguity around unsupported custom status values
- con:
  - older tests that returned ad hoc values will break under V2 rules

### 3. Keep zero exit status when valid evaluator JSON is produced

Status:

- Direction chosen and documented

Decision:

- for evaluation invocations, keep exit status `0` whenever the evaluator successfully emits valid contract JSON
- reserve non-zero exit status for cases where the process cannot provide a valid evaluator contract reliably

Examples that should remain exit `0`:

- missing evidence represented as evaluator messages
- blocked test execution represented as evaluator messages
- evidence parsing failures collapsed into evaluator messages
- test import or execution failures collapsed into evaluator messages

Examples that may justify non-zero exit:

- invalid CLI invocation
- bootstrap/import failure before the evaluator contract is available
- stdout contract corruption or serialization failure

Rationale:

- NAPE CLI depends on the evaluator JSON contract more than on Unix exit semantics for action evaluation
- this preserves machine-readable failure interpretation instead of forcing callers to infer too much from process status

Tradeoffs:

- pro:
  - stable downstream parsing contract
  - clearer separation between contract-level failures and process failures
- con:
  - some shell users may expect any evaluation failure to return non-zero

### 4. Keep trusted-code execution explicit; do not promise a sandbox in V2 unless implemented

Status:

- Direction chosen and documented

Decision:

- continue to treat test-of-detail Python files as trusted executable code until a real sandbox exists
- do not imply stronger isolation than the product actually provides

Rationale:

- the current evaluator intentionally imports and executes local Python files
- documenting a trust boundary honestly is better than suggesting security properties that are not implemented

Tradeoffs:

- pro:
  - accurate operator expectations
  - no false security assumptions
- con:
  - limits safe usage for untrusted procedures or shared environments

Future trigger:

- revisit this only when the product is ready to implement a real execution-control boundary

## Recommended Implementation Order

1. add outcome validation
2. keep exit-status policy stable unless bootstrap failure handling changes
3. decide whether an explicit legacy compatibility flag is worth building
4. revisit sandboxing only if the trust model becomes a product requirement

## Relationship To Current Docs

- current behavior remains documented in:
  - `README.md`
  - `docs/reference/evaluator-contract.md`
  - `docs/user/cli-reference.md`
  - `docs/product/v1-evaluator-baseline.md`
- this document records recommended V2 direction, not current contract truth
