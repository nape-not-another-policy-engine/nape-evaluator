# Software Review

This document defines the review checklist for `nape-evaluator`.

It adapts the Attestify architectural-review and software-quality approach to a small Python CLI/evaluator repository.

Use this document for:

- code review
- refactor review
- contract-change review
- docs hardening review
- pre-release quality review
- AI-generated change review

## Review Outcome Model

Each review item should be assessed as:

- `pass`
- `fail`
- `inconclusive`
- `not applicable`

If a review is inconclusive, record what evidence is missing.

## 1. Responsibility And Boundaries

- Is the bounded responsibility of the changed code explicit?
- Does the code belong in this repository rather than in a separate runtime, adapter, or larger NAPE CLI concern?
- Does the change preserve the evaluator’s explicit seams:
  - CLI invocation
  - request validation
  - evidence loading
  - dynamic test execution
  - structured JSON output
- Does the change avoid hiding behavior behind incidental helpers or uncontrolled side effects?
- If orchestration complexity grew, should an explicit use case now own that behavior?
- If an external dependency seam became important, should a gateway now exist?
- If construction/validation complexity grew, should an explicit construction helper or bounded request object now exist?

## 2. Contract Safety

- Does the change preserve or intentionally update the documented CLI contract?
- Does the change preserve or intentionally update the documented evaluator output contract?
- Are `results` behavior and `evaluator.messages` behavior still clearly distinct?
- If the contract changes, were the product, user, reference, and maintainer docs all reviewed together?
- Are examples and tests updated to match the contract?

## 3. Failure Behavior

- Are expected failures bounded and explainable?
- Are expected evaluator/runtime failures represented through the documented evaluator output contract?
- Does the change preserve the distinction between:
  - completed test `conclusion: "inconclusive"` caused by a test-owned contract violation
  - evaluator/runtime operational error
- Are blocked executions still visible through the summary counts and evaluator messages?
- Does the change avoid introducing raw traceback behavior as the intended contract for expected failures?

## 4. Dependency And Packaging Safety

- Does the change add any new runtime dependency?
- If yes, is it declared in `pyproject.toml`?
- If a format or behavior is documented as supported, does the install path actually provide the needed dependency?
- Does the change avoid introducing silent fallback behavior that weakens the documented contract?
- If the install or dependency story changed, were installation and maintainer docs updated?

## 5. Determinism And Behavioral Scope

- For the same input and dependency assumptions, does the evaluator still behave deterministically?
- Does the change add non-deterministic behavior?
- If yes, is it explicit, bounded, and documented?
- Has the change introduced a disproportionate amount of branching or hidden coordination for a small repo?
- Does any single module now own more than one bounded responsibility?
- Would splitting the module reduce verification or review complexity materially?

## 6. Test Coverage Review

- Are all newly introduced meaningful logical paths tested?
- Are test cases focused on bounded behavior rather than incidental implementation trivia?
- Are sad paths tested where failure semantics are part of the contract?
- Are multi-test continuation behaviors tested if touched?
- Are evidence-loader paths tested if touched?
- Are CLI invalid-invocation paths tested if touched?
- Are request-builder validation paths tested if touched?
- Are tests deterministic and free of unnecessary infrastructure assumptions?
- Is test organization still clear by seam or behavior surface?
- Are fixtures and assertions separated cleanly enough to keep review understandable?

## 7. Documentation Review

- Do docs describe only behavior actually supported by the implementation?
- Do quickstart and examples still match the active output contract?
- Do maintainer docs still match actual runtime and testing behavior?
- Do reference docs still map behavior precisely to code and tests?
- If new behavior was added, is its authoritative location in docs obvious?

## 8. Trusted-Code Execution Review

- Does the change preserve the explicit trust model for test-of-detail files?
- If execution semantics changed, do docs still clearly warn that requested test paths execute trusted Python code?
- Does the change accidentally broaden the execution surface without documentation?

## 9. Logging And Output Discipline

- Does the change keep stdout reserved for the documented JSON evaluator contract?
- If logging or diagnostics were added, do they avoid corrupting stdout?
- Are operational diagnostics kept separate from business or test-result meaning?
- Does the change avoid leaking secrets or unnecessary sensitive context?

## 10. AI-Assisted Change Review

- If the change was AI-assisted, does it still conform to repository standards?
- Does the patch show signs of generic boilerplate rather than repository-specific reasoning?
- Were standards, contract docs, and existing tests treated as the source of truth?
- Did the change preserve explicit seam and failure semantics?

## 11. Review Notes

Record:

- key risks found
- assumptions made
- missing evidence
- follow-up tasks
- whether the review result is acceptable for merge, staging, or only planning

## Suggested Review Rhythm

For small changes:

1. contract check
2. failure-behavior check
3. test check
4. docs check

For larger changes:

1. responsibility and seam check
2. contract and failure review
3. dependency/packaging review
4. test review
5. documentation review
6. final risk summary
