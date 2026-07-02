> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 07: Evaluator Software Integration Guide

## Goal

Define and author a clear, complete guide set for software that wraps `nape-evaluator` as a component.

The guide must teach integrators how to invoke the evaluator safely, build request packets correctly, interpret output deterministically, and harden the wrapper behavior for production use.

## Why This Is Its Own Plan

The current docs already cover:

- direct CLI use
- test-of-detail authoring
- maintainer-facing implementation details

What is still missing is a dedicated guide for downstream software authors who want to:

- call the evaluator from another program
- treat it as one step in a larger workflow
- consume the evaluator JSON contract programmatically
- distinguish evaluator-owned operational problems from test-owned conclusions

That audience is adjacent to both CLI users and maintainers, but it is not the same audience as either one.

If this guidance is left spread across the current docs, integrators must reconstruct the boundary from several documents and may infer a support surface that is not actually promised.

## Baseline

Read first:

1. `docs/1-plan/roadmap.md`
2. `docs/product/current-evaluator-reference.md`
3. `docs/reference/evaluator-contract.md`
4. `docs/user/cli-reference.md`
5. `docs/product/nape-evaluator-product-spec.md`
6. `../../specifications/engineering-standards/6-requirements/21-use-case-documentation-requirements.md`

## Research Findings

Based on the current runtime and the documentation standards, the guide should be grounded in these facts:

1. the current supported integration surface is the evaluator process boundary
2. the current stable machine-readable contract is packet-in JSON and JSON-out through the CLI
3. the current guide should not imply that importing evaluator internals as a supported library API is the preferred or stable downstream integration path
4. integrators need both:
   - a fast “how do I call this correctly” path
   - a deeper “how do I build a robust wrapper around this” path
5. the material is broad enough that one flat page would become a mixed quickstart, contract reference, and production-operations guide

## Recommended Documentation Format

Recommendation:

- create a dedicated guide set under:
  - `docs/user/software-integration/`

Recommended file set:

1. `docs/user/software-integration/README.md`
   - entry point
   - audience definition
   - current supported integration model
   - reading paths by need
2. `docs/user/software-integration/integration-model.md`
   - what the evaluator is and is not as a component
   - supported boundary
   - trust and execution model
   - ownership split between caller, evaluator, and test-of-detail
3. `docs/user/software-integration/request-and-invocation.md`
   - request packet shapes
   - when to use `--invoke`, `--invoke-file`, and `--request-file`
   - subprocess invocation flow
   - stdout/stderr and exit-status expectations
4. `docs/user/software-integration/response-handling.md`
   - how to parse output
   - how to interpret `results[*]`, `execution`, `result`, `evaluator.messages`, and `evaluator.summary`
   - how to distinguish blocked invocations, completed `inconclusive`, and evaluator operational errors
5. `docs/user/software-integration/production-hardening.md`
   - timeouts
   - temp-file and stdin/file tradeoffs
   - trusted-code implications
   - logging, traceability, and failure classification
   - versioning and change-control guidance for wrappers
6. `docs/user/software-integration/worked-examples.md`
   - one minimal wrapper flow
   - one more defensive production-style wrapper flow
   - examples should stay process-boundary oriented rather than teaching internal imports as the primary pattern

## Recommended Reader Flow

The guide should teach integrators in this order:

1. understand the component boundary
   - the evaluator is currently wrapped as a subprocess/CLI component
   - the stable boundary is request packet in, JSON result out
2. understand trust and ownership
   - caller owns evidence path and test invocation request packets
   - evaluator owns request validation, evidence loading, orchestration, messages, and summary
   - the test-of-detail owns comparison logic and completed-test reasoning
3. choose one invocation shape
   - repeated `--invoke`
   - repeated `--invoke-file`
   - full `--request-file`
4. build the request correctly
   - packet shape
   - validation expectations
   - no hidden type coercion
5. invoke the evaluator deterministically
   - subprocess model
   - stdout JSON as the primary machine-readable output
   - exit status is secondary to contract availability
6. parse and classify the response correctly
   - completed `true` / `false` / `inconclusive`
   - blocked `inconclusive`
   - evaluator `messages`
   - summary semantics
7. harden the wrapper behavior
   - timeouts
   - artifact retention
   - logging
   - failure routing
   - trusted-code guardrails

## Recommended Authoring Flow

Do not start by writing language-specific wrapper examples.

Recommended authoring order:

1. write the integration boundary and support-position page first
   - avoid promising a non-existent public library API
2. write the request/invocation page second
   - show the exact packet and process shapes
3. write the response-handling page third
   - this is the highest-risk interpretation surface for wrappers
4. write the production-hardening page fourth
   - make operational expectations explicit
5. write worked examples last
   - keep them aligned to the boundary already established in the earlier pages

## Selected Documentation Direction

Selected recommendation:

- use a multi-page guide set, not one single long page

Rationale:

- integrators need both tutorial flow and reference-like lookup
- boundary explanation, invocation mechanics, response semantics, and hardening concerns are distinct enough to deserve separate pages
- a guide set makes future language-specific examples easier to add without bloating one page beyond usefulness

## Non-Goals

This workstream should not, by default:

- define a new supported non-CLI public API
- imply that importing `src/nape_evaluator/...` directly is the preferred downstream integration model
- redesign the evaluator contract
- duplicate the full CLI reference inside the guide set
- teach test authorship in detail beyond what integration readers need to understand the trust boundary

## Initial Milestones

1. record the selected guide shape and reading flow
2. create the guide-set skeleton under `docs/user/software-integration/`
3. author the core pages:
   - boundary
   - request/invocation
   - response handling
   - production hardening
4. add worked examples and route readers to the new guide set from existing user docs

## Current Status

Active.

The guide-set skeleton and the first substantive pages are now landed:

- `README.md`
- `integration-model.md`
- `request-and-invocation.md`
- `response-handling.md`
- `production-hardening.md`
- `worked-examples.md`

The red-team review tasks that had to be addressed before closure were:

1. tighten the “defensive Rust-oriented wrapper” example so it actually demonstrates the behaviors it claims to add:
   - explicit timeout handling
   - request artifact retention
   - evaluator-message inspection
2. fix the reader path in `docs/user/software-integration/README.md` so the “fastest path” does not skip `response-handling.md`
3. improve the minimal worked example so it does not collapse every non-`completed_true` case into one opaque catch-all outcome

Those three items are now addressed.

The next task is closure review of the guide set as a whole and a final decision about whether any further depth is still needed before archiving the workstream.

## Closure Review Findings And Recommended Resolutions

The latest closure review found three remaining guide-set issues.

These are documented here as recommended execution steps pending approval.

### 1. Completed-row `result.reason` ownership is stated too absolutely

Finding:

- `docs/user/software-integration/response-handling.md` currently says that when `execution.executed == true`, `result.reason` is test-owned reasoning
- that is too absolute for the current runtime
- if a test completes but returns an invalid result contract, the evaluator normalizes that completed row to `conclusion == "inconclusive"` and emits evaluator-authored explanatory `reason` text

Recommendation:

- tighten the wording so the guide says:
  - completed rows usually carry test-authored reasoning
  - but completed rows normalized from invalid test result contracts carry evaluator-authored explanatory reasoning
  - wrappers should therefore treat `result.reason` primarily as completed-row reasoning, and use surrounding row context to determine whether it is ordinary test reasoning or evaluator normalization text

Rationale:

- this keeps the guide aligned with the actual runtime normalization path
- it prevents wrapper authors from incorrectly attributing every completed-row `reason` to the test
- it preserves the more important distinction:
  - blocked-row reasoning is evaluator-owned because the test did not complete
  - completed-row reasoning is usually test-owned, except for completed-result normalization

Tradeoff:

- the simpler rule, “completed means test-owned,” is easier to teach
- but it is materially inaccurate against current behavior, so accuracy should win here

### 2. Request-retention guidance currently presents two different defaults

Finding:

- `request-and-invocation.md` recommends retaining request packets for unusual outcomes
- `production-hardening.md` recommends retaining all request packets at first if volume allows
- both positions are defensible, but the guide currently leaves the reader with two competing defaults

Recommendation:

- establish one baseline default across the guide set:
  - production-hardening should remain the stronger normative default:
    - retain all request packets at first if volume allows
  - request-and-invocation should be reframed as the lighter minimum:
    - at minimum, retain request packets for unusual outcomes such as blocked rows, completed `inconclusive`, evaluator `message_error`, timeout, and stdout parse failure

Rationale:

- this creates a clear progression instead of a contradiction:
  - minimum acceptable retention
  - stronger recommended production default
- it keeps the practical, cost-aware advice while still giving integrators one clear recommended starting point
- it matches the broader guide philosophy of favoring diagnosability early, then tightening cost later with evidence

Tradeoff:

- “retain everything first” is heavier operationally
- but it is the safer default for early integrations, especially while wrappers are still learning their own failure patterns

### 3. One page shortens the `subject.name` rule below the actual boundary

Finding:

- `request-and-invocation.md` currently summarizes `subject.name` as lowercase snake_case ASCII
- the actual contract is narrower:
  - lowercase snake_case ASCII
  - must start with a letter
  - must end with an alphanumeric

Recommendation:

- update the integration guide wording to match the contract exactly
- preferably use the full rule in the validation section:
  - `subject.name` must be lowercase snake_case ASCII, start with a letter, and end with an alphanumeric

Rationale:

- request-building guidance must not be looser than the real request boundary
- wrapper authors may implement their own preflight validation from this page alone
- keeping the wording exact avoids preventable wrapper/evaluator mismatch

Tradeoff:

- the shorter wording is quicker to read
- but it is incomplete in a place that directly affects boundary validation, so precision matters more than brevity

## Latest Execution Status

The three closure-review recommendations above are now implemented in the guide pages:

1. `response-handling.md`
   - completed-row `result.reason` ownership wording now reflects the evaluator normalization exception for invalid completed result contracts
2. `request-and-invocation.md`
   - `subject.name` wording now matches the live boundary exactly
   - request retention guidance now distinguishes minimum baseline from stronger production default
3. `production-hardening.md`
   - retention guidance now explicitly states that it is the stronger preferred production default, not a competing minimum

The next task is a fresh closure review to determine whether any material guide gaps still remain before Plan 07 can close.

## Fresh Closure Review Findings And Recommended Fixes

The fresh closure review found two remaining material issues and one low-severity stale wording issue.

These are recorded here as recommended fixes pending approval.

### 1. Example 5 currently shows an invalid response shape

Finding:

- `docs/user/software-integration/worked-examples.md` Example 5 omits fields required by the current output contract
- each `results[*]` row must include:
  - `evaluations`
  - `execution`
  - `result`
- each completed `result` must include:
  - `conclusion`
  - `facts`
  - `reason`
- the current example omits:
  - `evaluations`
  - `facts`

Recommendation:

- patch Example 5 so it becomes a fully contract-valid response example
- add explicit `evaluations` arrays to both result rows
- add explicit `facts` arrays to both completed `result` objects
- keep the example’s real teaching point the same:
  - one shared request-scoped warning across two otherwise completed rows

Rationale:

- worked examples must not teach an invalid contract shape
- software integrators may lift example payloads into tests, fixtures, or mental models directly
- because this is an example page, contract-validity matters more than brevity

Tradeoff:

- the JSON example becomes longer
- but complete and valid is the right tradeoff for this guide set

### 2. The minimum request-retention floor is still inconsistent across pages

Finding:

- `request-and-invocation.md` minimum baseline currently includes:
  - blocked results
  - `inconclusive`
  - evaluator `message_error`
- `production-hardening.md` recommended minimum includes those plus:
  - timeout
  - stdout parse failure
- that leaves the guide with two different “minimum” floors

Recommendation:

- align the minimum baseline in `request-and-invocation.md` with `production-hardening.md`
- the minimum retained-request floor should include:
  - blocked results
  - completed `inconclusive`
  - evaluator `message_error`
  - timeout
  - stdout parse failure
- keep `production-hardening.md` as the stronger preferred default that says:
  - retain all request packets at first if volume allows

Rationale:

- timeout and stdout parse failure are exactly the kinds of diagnosability-critical cases that minimum retention should cover
- readers should not have to infer that one page is more complete than the other for the same minimum policy
- this preserves the clear progression:
  - minimum diagnostic floor
  - stronger early-production default

Tradeoff:

- the minimum floor becomes slightly broader
- but those added cases are high-value diagnostic failures and fit the stated hardening posture

### 3. One stale future-tense reference remains

Finding:

- `response-handling.md` still says to use worked examples “once those are authored”
- the worked examples already exist

Recommendation:

- update that sentence to present tense

Rationale:

- low severity, but stale wording weakens trust in doc freshness during closure review

## Final Closure Review Result

The approved fixes above are now implemented.

Final closure review result:

- no remaining material guide gaps were found in the software-integration guide set
- the guide pages are now aligned with the current request contract, output contract, summary/message semantics, and the selected wrapper-side retention and interpretation guidance

Residual non-blocking note:

- the worked examples intentionally remain pedagogical examples and pseudocode, not executable wrapper artifacts
- that is acceptable for this plan because the guide set explicitly frames them as teaching examples rather than a shipped SDK or copy-paste integration library

Plan 07 is closed and archived.
