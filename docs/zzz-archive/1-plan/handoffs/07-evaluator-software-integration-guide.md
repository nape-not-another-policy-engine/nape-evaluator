> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 07: Evaluator Software Integration Guide

## Purpose

Resume the new integration-guide workstream without re-deriving why it exists or what documentation shape was selected.

## Status

This workstream is complete.

The core guide-set pages are authored, reviewed, and routed into the current user docs.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/07-evaluator-software-integration-guide.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/reference/evaluator-contract.md`
5. `docs/user/cli-reference.md`
6. `docs/product/nape-evaluator-product-spec.md`

## Selected Direction

- the guide is for downstream software authors, not test authors and not evaluator maintainers
- the guide should be grounded in the current supported process boundary:
  - CLI invocation
  - JSON request packets
  - JSON output parsing
- the guide should not imply that evaluator internals are a supported public library API
- the selected documentation shape is a multi-page guide set under:
  - `docs/user/software-integration/`

## Selected Guide Shape

Recommended pages:

1. `README.md`
2. `integration-model.md`
3. `request-and-invocation.md`
4. `response-handling.md`
5. `production-hardening.md`
6. `worked-examples.md`

## Immediate Objectives

1. perform closure review of the current guide set
2. decide whether any page still needs materially deeper treatment before closure
3. keep routing docs aligned with the new guide set

## Guardrails

- do not invent a new supported evaluator API surface by implication
- keep the distinction between caller-owned, evaluator-owned, and test-owned concerns explicit
- keep the guide aligned with `current-evaluator-reference.md` and `evaluator-contract.md`
- prefer clear, complete explanation over brevity when the two conflict

## Expected Near-Term Outputs

- closure review of the new `docs/user/software-integration/` guide set now that the three red-team findings have been addressed
- any final routing or depth adjustments needed before the workstream can close

## Latest Closure Review Recommendations

The latest closure review found three remaining issues to patch before closure.

Recommended resolutions:

1. tighten completed-row `result.reason` wording
   - do not say every completed row reason is test-owned
   - selected recommendation:
     - say completed rows usually carry test-authored reasoning
     - but invalid completed result contracts are normalized into completed `inconclusive` rows with evaluator-authored explanatory `reason` text
     - wrappers should read completed `reason` as completed-row reasoning first, then use row context to distinguish ordinary test reasoning from evaluator normalization text
2. unify request-retention defaults across the guide set
   - selected recommendation:
     - keep `production-hardening.md` as the stronger default:
       - retain all request packets at first if volume allows
     - reframe `request-and-invocation.md` as the minimum baseline:
       - at minimum, retain unusual outcomes only
3. make `subject.name` wording exactly match the live boundary
   - selected recommendation:
     - use the full rule:
       - lowercase snake_case ASCII
       - start with a letter
       - end with an alphanumeric

Why these are the recommended direction:

- they close actual contract/guide mismatches rather than stylistic issues
- they preserve clear reader guidance while matching the current runtime
- they leave the guide with one consistent operational posture instead of competing defaults

## Updated Status

Those three recommended fixes are now implemented in the guide pages.

Current immediate objective:

1. perform one fresh closure review of the software-integration guide set
2. decide whether any remaining gap is material enough to keep Plan 07 open

## Latest Recommended Fixes From Fresh Closure Review

The fresh closure review found the following recommended fixes:

1. fix Example 5 in `worked-examples.md`
   - selected recommendation:
     - make the example fully contract-valid by restoring required `evaluations` and `facts` fields
     - preserve the example’s purpose as a shared request-scoped warning scenario
2. align the minimum request-retention floor across guide pages
   - selected recommendation:
     - minimum retained-request cases should include:
       - blocked results
       - completed `inconclusive`
       - evaluator `message_error`
       - timeout
       - stdout parse failure
     - keep `production-hardening.md` as the stronger preferred default:
       - retain all request packets at first if volume allows
3. remove one stale future-tense line in `response-handling.md`
   - selected recommendation:
     - switch “once those are authored” to present-tense wording

Why these are the recommended direction:

- they close the last remaining material correctness issues found in the guide set
- they keep the examples aligned with the actual contract
- they remove the last remaining policy inconsistency in request-retention guidance

## Final Closure Review Status

Those recommended fixes are now implemented.

Latest review result:

- no remaining material guide gaps were found
- Plan 07 is closed and archived

Residual non-blocking note:

- worked examples remain intentionally pedagogical rather than executable integration artifacts
