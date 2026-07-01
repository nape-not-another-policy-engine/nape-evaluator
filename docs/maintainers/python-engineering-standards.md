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
- safe to evolve toward V2

The source inspiration for this document is the Attestify engineering-standards repository, but the rules below are the local standards for this repository.

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
2. evidence-loading seam
3. dynamic test-of-detail execution seam
4. evaluator output seam
5. package/install seam
6. documentation and review seam

These seams are more important than imposing artificial internal layers.

## V2 Structural Direction

The current repository is compact, but V2 work should prefer explicit internal roles once complexity justifies them.

For this repository, the preferred future roles are:

- CLI or IO adapter
- evaluator orchestration use case
- evidence-loading support surfaces
- test-module loading and execution support surfaces
- output serialization support surfaces
- explicit gateways only where external dependency seams need to be isolated

These are review and refactor targets, not a claim that the current repo already implements each role cleanly.

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
- typed evidence-loading behavior
- metadata and caller-owned parameters passed into `evaluate(evidence, test_parameters, metadata)`
- structured JSON output shape
- evaluator/runtime failure representation
- packaging expectations for supported file types

Public behavior must not be left implicit if callers, test authors, or future V2 work depend on it.

## Seam Rule

Bounded seams must remain explicit and reviewable.

Current seams include:

- command-line inputs into the evaluator process
- file-extension-based evidence translation into Python objects
- trusted test-of-detail execution through `evaluate(evidence, test_parameters, metadata)`
- evaluator output through stdout JSON

New features should preserve seam clarity rather than collapse behavior into hidden side effects or convenience shortcuts.

## Use Case Rule

When evaluator behavior becomes orchestration-heavy, it should be expressed as an explicit use case rather than left embedded in transport parsing.

For this repository, the main use case candidate is:

- evaluate one evidence file against one or more test-of-detail files and emit the bounded evaluator output

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

Do not force Java-style builders into Python.

Use explicit construction helpers only when they materially improve:

- validation clarity
- bounded request construction
- normalization behavior
- contract readability

Acceptable Python equivalents include:

- validating factory functions
- explicit request dataclasses
- construction helpers that finalize bounded input objects before execution

Construction support surfaces should remain subordinate to the owned seam or use case, not become free-floating abstractions.

## Failure Behavior Rule

Failure behavior is part of the contract.

Expected evaluator/runtime failures should:

- be bounded
- be explainable
- be serializable into the documented output contract
- remain distinguishable from returned test outcomes

Current meaning must remain explicit:

- returned test outcome `"error"` is a test result
- evaluator/runtime failure is an evaluator message
- blocked execution is visible through `count`, `ran`, and evaluator messages

Raw Python tracebacks are not the intended contract for expected evaluator-boundary failures.

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

- the evaluator dynamically imports and executes Python files supplied by `--test`
- these files are not sandboxed
- untrusted test files should not be run in sensitive environments

Future hardening may change execution controls, but the current trust model must stay explicit.

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

Split a Python module when one or more of these become true:

- the module owns more than one bounded responsibility
- meaningful logical paths for unrelated concerns are mixed together
- tests must indirectly cover unrelated behavior because no narrower unit exists
- documentation has to explain several separate seams in one file
- a reviewer can no longer explain the module’s owned behavior in one short statement

Line count may be a smell, but it is not the primary rule.

For this repository, a large file is acceptable only if its behavior is still bounded and reviewable as one responsibility.

## Test Organization Rule

Tests should be organized by bounded behavior surface, not just by convenience or file type.

Preferred grouping direction for this repository is:

- CLI contract behavior
- evidence-loading behavior
- execution-flow behavior
- output-contract behavior

Fixtures should remain separate from behavioral assertions where practical.

As the repository grows, test modules should reflect seam ownership clearly enough that a reviewer can tell what contract surface each test file verifies.

## Meaningful Logical Path Rule

Testing should cover meaningful logical paths, not just happy paths or syntactic branch counts.

For `nape-evaluator`, meaningful logical paths include:

- valid CLI install check
- invalid CLI invocation
- single-test success
- multi-test success
- one-test-fails-and-others-continue
- missing evidence
- missing test file
- import failure
- test execution failure
- supported structured evidence loading
- text fallback behavior
- known unprocessable extension behavior

Behaviorally distinct paths should be explicit in tests or deliberately documented as deferred.

Test growth should also remain bounded. Avoid adding noisy, repetitive tests that do not increase confidence in a distinct logical path or contract surface.

## Determinism Rule

The evaluator should behave deterministically for the same:

- CLI arguments
- evidence content
- test-of-detail implementation
- runtime dependency availability assumptions

If non-deterministic behavior is introduced later, it must be intentional and documented.

## AI-Assisted Development Rule

AI-generated or AI-modified output in this repository must:

- preserve the evaluator contract
- preserve seam clarity
- preserve failure semantics
- preserve or improve meaningful logical-path coverage
- preserve docs/code alignment

AI-generated output must not:

- invent undocumented behavior
- silently weaken contracts
- optimize for brevity over correctness
- replace repository standards with generic defaults

## When To Add New Maintainer Docs

Add or expand permanent maintainer docs when:

- a new public seam is introduced
- a new supported evidence format is added
- output shape changes
- install/runtime dependency expectations change
- a new review surface becomes necessary for V2 work

## Review Link

Use [software-review.md](software-review.md) as the repo-specific review checklist derived from these standards.
