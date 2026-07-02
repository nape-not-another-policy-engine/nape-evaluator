# Python Engineering Standards

This document adapts the transferable Attestify engineering standards to the `nape-evaluator` Python repository.

It is intentionally Python-specific and repository-specific. It does not attempt to force the full Attestify Rust architecture model onto a small evaluator CLI.

## Purpose

These standards exist to keep `nape-evaluator`:

- bounded
- explainable
- verifiable
- reviewable
- documentation-led
- safe to evolve

## Scope

These standards apply to:

- `main.py`
- test-of-detail execution behavior
- evidence-loading behavior
- CLI and JSON output contracts
- packaging and dependency behavior
- tests and docs that define or verify evaluator behavior

## Core Model

`nape-evaluator` is a small process-boundary tool. Its main governed seams are:

1. CLI invocation seam
2. request validation seam
3. evidence-loading seam
4. dynamic test-of-detail execution seam
5. evaluator output seam
6. package/install seam
7. documentation and review seam

These seams are more important than imposing artificial internal layers.

## Source Of Truth Rule

The source of truth for repository behavior is:

- implemented code
- verified tests
- maintained contract and maintainer docs

Examples, generated summaries, and AI output must conform to those sources rather than redefine them.

## Contract Rule

Every public evaluator behavior should have an explicit contract.

For this repository, that includes at minimum:

- CLI argument behavior
- request packet behavior
- typed evidence-loading behavior
- metadata and caller-owned `evaluations` passed into `evaluate(evidence, evaluations, metadata)`
- structured JSON output shape
- evaluator/runtime failure representation
- packaging expectations for supported file types

Public behavior must not be left implicit if callers, test authors, or future work depend on it.

## Seam Rule

Bounded seams must remain explicit and reviewable.

Current seams include:

- command-line inputs into the evaluator process
- request-builder validation before use-case execution
- file-extension-based evidence translation into Python objects
- trusted test-of-detail execution through `evaluate(evidence, evaluations, metadata)`
- evaluator output through stdout JSON

New features should preserve seam clarity rather than collapse behavior into hidden side effects or convenience shortcuts.

## Use Case Rule

When evaluator behavior becomes orchestration-heavy, it should be expressed as an explicit use case rather than left embedded in transport parsing.

For this repository, the main use case is:

- evaluate one evidence file against one or more test-of-detail invocations and emit the bounded evaluator output

An evaluator use case should own:

- orchestration order
- meaningful branching across execution paths
- coordination of evidence input, test execution, and output shaping

An evaluator use case should not own:

- CLI parsing details
- stdout/stderr transport mechanics
- low-level parser library details
- unrelated packaging concerns

## Gateway Rule

Do not introduce gateways by default.

Introduce a gateway only when a dependency or infrastructure concern needs an explicit replaceable seam for clarity, testing, or contract safety.

Likely gateway candidates in this repository include:

- filesystem access if file interaction becomes more complex or needs isolation
- dynamic module loading if execution rules become richer
- format-specific parser boundaries if they need explicit dependency ownership or translation rules

Do not create fake gateways around trivial local behavior merely to mirror a larger architecture.

## Builder And Construction Rule

Use explicit construction helpers when they materially improve:

- validation clarity
- bounded request construction
- normalization behavior
- contract readability

In this repository, `EvaluateEvidenceRequest.builder().try_build()` is the owned request-seam construction path for caller-owned evaluation input.

Construction support surfaces should remain subordinate to the owned seam or use case, not become free-floating abstractions.

## Failure Behavior Rule

Failure behavior is part of the contract.

Expected evaluator/runtime failures should:

- be bounded
- be explainable
- be serializable into the documented output contract
- remain distinguishable from completed test conclusions

Current meaning must remain explicit:

- completed test `conclusion: "inconclusive"` can be a test-owned contract-violation result
- evaluator/runtime failure is an evaluator message
- blocked execution is visible through `count`, `ran`, and evaluator messages

Malformed caller-owned `evaluations` input should be rejected at the evaluator boundary rather than left to ad hoc test-level failure handling.

Missing or unusable extracted facts remain test-owned evaluation concerns that may lead to `inconclusive`.

## Python Error-Handling Rule

Python code in this repository should not rely on crash-first behavior for expected evaluator paths.

Preferred behavior:

- validate inputs at the seam
- translate expected failures into the documented evaluator output contract
- allow truly unexpected failures to be collapsed at the process boundary into structured evaluator messages

Avoid:

- hidden process crashes for expected user or file conditions
- broad internal exception swallowing that destroys useful bounded meaning
- undocumented exception-to-contract changes

## Dependency Rule

Runtime dependencies must be explicit in package metadata and consistent with documented supported behavior.

If a format is documented as supported in the shipped product, the required dependency must be part of the supported install path.

This repository should not rely on:

- undeclared transitive dependencies
- silent fallback behavior that changes the contract materially
- docs that imply support wider than the packaged runtime actually provides

If an external dependency is added behind a gateway seam in the future, the gateway must still translate that dependency into a bounded evaluator-facing contract.

## Logging Rule

Logging is an operational concern, not the evaluator’s public contract.

If logging is introduced later:

- stdout JSON remains the only intended machine-readable evaluator output
- logs must not replace `results` or `evaluator.messages`
- logs should go to stderr or another explicit sink
- logs must not leak secrets or sensitive data

## Test-Of-Detail Trust Rule

Test-of-detail files are trusted executable Python code.

Repository docs and reviews must continue to state that:

- the evaluator dynamically imports and executes Python files supplied through requested `test` paths
- these files are not sandboxed
- untrusted test files should not be run in sensitive environments

## Documentation Governance Rule

Documentation is not just explanatory. It is part of repository governance.

At minimum, docs must keep these surfaces aligned:

- product behavior
- user-facing CLI behavior
- maintainer architecture and local validation behavior
- reference contract details
- examples

When one surface changes, linked contract docs must be reviewed together.

## Quality Rule

Quality claims must be reviewable as evidence, not style impressions.

For this repository, each meaningful bounded behavior should be reviewable in terms of:

- responsibility
- input classes
- output classes
- failure behavior
- determinism assumptions
- meaningful logical paths
- test evidence
- documentation traceability

## Module Size And Decomposition Rule

Module size is governed primarily by bounded responsibility, not raw line count.
