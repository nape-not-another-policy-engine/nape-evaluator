> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 03: Structured Verification V2 Implementation Planning

## Completion Outcome

This plan is now complete.

Selected closure decision:

- the V2 runtime cutover is complete
- the builder-only request seam, packet-based CLI transport, structured result envelope, and completed-test conclusion vocabulary are implemented
- permanent product, reference, user, and maintainer docs are aligned closely enough with the runtime to stop this workstream
- the residual legacy cleanup pass is complete
- the last implementation-grade validation gap found during closure review, duplicate `subject.name` within one invocation, has been fixed and covered by tests

Closure rationale:

- the remaining old-shape references are now either explicitly historical, preserved audit/planning traceability, or future-expansion ideas rather than current runtime defects
- no further active runtime or current-doc contradictions were found in the closure-oriented review
- keeping this plan open would now mostly create planning residue rather than drive a real unresolved implementation outcome

Any future work beyond this point should be opened as a new explicit workstream, such as broader criteria-surface expansion or a new validation-hardening effort.

## Goal

Turn the selected V2 structured verification model into an implementation-ready change plan grounded in the current evaluator code paths.

## Baseline

This plan starts from:

1. `docs/product/current-evaluator-reference.md`
2. `docs/zzz-archive/product/v2-structured-verification-input-proposal.md`
3. `docs/zzz-archive/product/v2-structured-verification-result-proposal.md`
4. `docs/zzz-archive/1-plan/plans/01-structured-verification-v2.md`
5. `docs/zzz-archive/1-plan/handoffs/01-structured-verification-v2.md`

## Historical Audit Note

The `Implementation Audit` section below records the pre-cutover baseline that was captured before the first V2 runtime implementation landed.

It is preserved for traceability.

It does not describe the current runtime.

For current runtime behavior, use:

- `docs/product/current-evaluator-reference.md`
- `docs/zzz-archive/1-plan/handoffs/03-structured-verification-v2-implementation-planning.md`

## Implementation Audit

### Historical Baseline Shape At Time Of Audit

- `src/nape_evaluator/application/io/cli.py`
  - direct CLI transport is built around repeated `--test` plus positional `--test-parameters-file`
  - parameter files must decode to a top-level JSON object
  - blocked parameter loading is represented before the use case runs
- `src/nape_evaluator/domain/use_case_models.py`
  - invocation state is modeled as `TestInvocationRequest`
  - caller-owned input is still named `test_parameters`
  - request batching is modeled as `EvaluateEvidenceRequest(evidence_path, test_invocations)`
- `src/nape_evaluator/domain/use_cases.py`
  - the evaluator calls `evaluate(evidence_data, invocation.test_parameters, metadata)`
  - successful tests are expected to return a two-item `(outcome, reason)` tuple
  - result rows are built as flat packets with `executed`, `outcome`, and `reason`
  - blocked or failed invocations still produce a per-request result row
- `src/nape_evaluator/application/io/output_contract.py`
  - CLI output nests `results` and `evaluator`
  - summary counts are keyed off flat result `outcome` values and `executed`
- `src/nape_evaluator/application/driver/test_of_detail_gateway.py`
  - the gateway only loads the Python module
  - no test-signature or return-shape validation is centralized here today

### Historical Test Surface At Time Of Audit

- `tests/test_cli_contract.py`
  - exercises CLI argument binding, parameter-file loading, blocked invocation behavior, and flat JSON output expectations
- `tests/test_evaluator_use_case.py`
  - exercises request execution, shared-message contextualization, blocked invocations, invalid outcomes, and parameter passing
- `tests/test_output_contract.py`
  - exercises summary counting and evaluator message formatting
- `tests/json/test_of_detail/verify_author_complete.py`
  - still models the current tuple-returning test contract

### Audit Findings

1. The selected V2 request model is cross-cutting.
   It affects CLI parsing, request dataclasses, evaluator execution, and result serialization rather than one isolated module.

2. The selected V2 result model is a true contract change.
   The current runtime assumes flat `outcome` / `reason` rows, while the selected direction requires outer `execution` plus inner structured `result`.

3. Evidence loading is mostly reusable.
   The evidence gateway already returns `(evidence_data, metadata, shared_messages)` and does not materially depend on `test_parameters`.

4. CLI transport is the largest unresolved implementation dependency.
   The codebase currently only knows how to bind one JSON object file per `--test`, so any V2 runtime plan has to either wait for Plan 02 transport decisions or stage non-CLI work first.

5. Test authoring and runtime compatibility need an explicit migration stance.
   The current runtime expects `evaluate(evidence, test_parameters, metadata)` and a tuple return, while the selected V2 docs now teach `evaluate(evidence, evaluations, metadata)` and a structured `result`.

## Scope

In scope:

- implementation planning for the selected V2 request model
- implementation planning for the selected V2 result model
- code-path audit and change staging
- explicit identification of cross-plan dependencies and blockers

Out of scope:

- implementing the full V2 runtime in this plan document
- deciding final CLI ergonomics beyond what must be recorded as a dependency
- changing evaluator fundamentals that were preserved by Plan 01

## Targeted Updates

Status:

- substantially implemented
- remaining work is now mostly residual legacy cleanup, validation-precision review, and closure-readiness assessment

### Phase 1: Domain Contract Refactor Plan

- replace request-side `test_parameters` planning language with V2 `evaluations`
- realize the use-case request seam as a builder-only verified request object
- define the new invocation model that carries:
  - `test`
  - `evidence`
  - caller-owned `evaluations`
  - evaluator-owned blocked execution state
- define the V2 execution/result packet boundary in code terms:
  - outer invocation echo
  - outer `execution`
  - inner test-owned `result`

### Phase 2: Validation Ownership Plan

- add evaluator-owned pre-test validation for:
  - `subject.name`
  - `subject.data_type`
  - `criteria` object shape
  - first-pass subject/data-type compatibility
- keep that validation concentrated at request-builder finalization time
- keep fact extraction and final reasoning test-owned
- record how validation failures map to blocked execution versus returned `inconclusive`

### Phase 3: Test Runtime Boundary Plan

- update the planned Python test boundary to `evaluate(evidence, evaluations, metadata)`
- define how the evaluator validates the returned structured `result`
- implement the already selected clean cutover to V2-only tests without a compatibility shim

### Phase 4: Output Contract And Summary Plan

- replace flat row planning with:
  - echoed outer request context
  - `execution`
  - structured `result`
- update aggregate summary planning so counts are driven by:
  - `execution.executed`
  - `result.conclusion` for completed tests
- keep evaluator messages separate from test-owned result content

### Phase 5: CLI And Fixture Alignment Plan

- align direct CLI transport with Plan 02 decisions before runtime implementation
- update fixture tests and sample tests to the selected V2 model
- align docs that still describe current `test_parameters` transport once implementation sequencing is chosen

## Open Implementation Questions

1. Should V2 runtime work be staged behind a compatibility layer, or treated as a clean contract cutover?
   Answer:
   V2 runtime must be a clean contract cutover.
2. Where should evaluator-side V2 request validation live?
   Answer:
   In the `EvaluateEvidenceRequest` seam through builder-finalization validation.
3. How should the full outer request packet be keyed for repeated requested tests?
   Answer:
   Use top-level `tests`.
4. Where should post-execution test `result` validation live?
   Answer:
   In `EvaluateEvidenceResponse`.
5. What conclusion vocabulary should V2 use for completed test-owned results?
   Answer:
   `true`, `false`, `inconclusive`, and `error`.

## Selected Decisions

- V2 runtime must be a clean contract cutover.
- Do not plan for a tuple-return compatibility shim or mixed V1/V2 runtime behavior.
- Implementation planning should assume the Python test boundary, request shape, and result shape change together at the V2 cutover point.
- The full outer request packet should use top-level `tests` for the repeated requested test array.
- V2 request validation belongs in the use-case request seam, not in the gateway and not as scattered ad hoc checks in the use case body.
- `EvaluateEvidenceRequest` should become the verified post-builder request object for the evaluator use case.
- For this request-bearing seam, the public construction entrypoint should be `EvaluateEvidenceRequest.builder()`, and finalization should be `try_build()`.
- The CLI adapter should remain responsible for transport parsing and raw input decoding only, then map boundary input into the request builder.
- The use case should accept only a built `EvaluateEvidenceRequest` and should treat that object as already validated caller-owned input.
- Post-execution test `result` validation should live in `EvaluateEvidenceResponse`.
- The V2 completed-test conclusion vocabulary should be `true`, `false`, `inconclusive`, and `error`.

## Selected Request-Seam Direction

### Standards Basis

This direction follows the deeper engineering standards under `../../specifications/engineering-standards`, especially:

- `6-requirements/01-use-case-requirements.md`
- `6-requirements/03-builder-requirements.md`
- `6-requirements/04-construction-requirements.md`
- `1-standards/10-io-adapters.md`
- `1-standards/18-bounded-objects-and-immutability.md`
- `1-standards/23-use-cases.md`

Applied meaning:

- a request-bearing use case must define an explicit bounded request object
- when caller-provided data crosses that seam, the request must also define a builder
- the request object's `builder()` entrypoint is the only supported public way to start construction
- `try_build()` is the correct finalization path when validation may fail
- request-build failure happens before the use-case execution seam is crossed
- the I/O adapter translates boundary input into the request builder but does not own domain request semantics

### Builder-Only Request Model

The V2 evaluator request seam should be realized as:

- `EvaluateEvidenceRequest`
  - verified, frozen, post-builder use-case request object
- `EvaluateEvidenceRequestBuilder`
  - collects raw caller-owned request input and performs final validation in `try_build()`
- nested or adjacent bounded request support surfaces:
  - `TestInvocationRequest`
  - `EvaluationInput`
  - `EvaluationSubject`
  - `EvaluationCriteria`

The final built request object should be the only form accepted by `evaluate_request(...)`.

Direct public construction of an unverified `EvaluateEvidenceRequest` should not remain the normal seam path.

### Exact Builder API Direction

Recommended request entrypoint:

```python
request = (
    EvaluateEvidenceRequest.builder()
    .evidence_path(args.evidence)
    .raw_tests(raw_tests)
    .try_build()
)
```

Recommended outer request builder surface:

- `EvaluateEvidenceRequest.builder()`
- `EvaluateEvidenceRequestBuilder.evidence_path(evidence_path: str) -> EvaluateEvidenceRequestBuilder`
- `EvaluateEvidenceRequestBuilder.raw_tests(raw_tests: list[dict]) -> EvaluateEvidenceRequestBuilder`
- `EvaluateEvidenceRequestBuilder.add_raw_test_invocation(raw_test_invocation: dict) -> EvaluateEvidenceRequestBuilder`
- `EvaluateEvidenceRequestBuilder.try_build() -> EvaluateEvidenceRequest`

Recommended raw invocation shape collected by the outer builder:

```python
{
    "test": "./coverage_check.py",
    "evaluations": [
        {
            "subject": {
                "name": "coverage",
                "data_type": "number",
            },
            "criteria": {
                "minimum": 80,
            },
        }
    ],
}
```

Recommended verified final request shape:

- `EvaluateEvidenceRequest.evidence_path`
- `EvaluateEvidenceRequest.test_invocations`
- `TestInvocationRequest.test_path`
- `TestInvocationRequest.evaluations`
- `TestInvocationRequest.blocked_code`
- `TestInvocationRequest.blocked_reason`
- `EvaluationInput.subject`
- `EvaluationInput.criteria`

### Validation Ownership

`EvaluateEvidenceRequestBuilder.try_build()` should own final request verification for caller-owned V2 input, including:

- presence of required request fields
- top-level request shape
- one or more test invocations
- per-invocation `test` presence and string validity
- `evaluations` presence and array shape
- each evaluation item containing exactly:
  - `subject`
  - `criteria`
- `subject.name` rule enforcement
  - lowercase snake_case
  - ASCII only
  - must start with a letter
  - must end with an alphanumeric
- supported `subject.data_type`
- `criteria` object shape
- supported first-pass criteria keys
- allowed multi-key combinations
- `subject.data_type` and `criteria` compatibility
- strict no-coercion typed values

Validation helpers should remain private to the builder implementation.

### Layer Ownership

Selected ownership split:

- CLI adapter:
  - parse arguments
  - load files
  - decode JSON
  - map raw boundary input into `EvaluateEvidenceRequest.builder()`
- request builder:
  - own verified request formation
  - reject malformed or incompatible caller-owned V2 input before execution
- use case body:
  - orchestrate evidence loading, test loading, test execution, and result shaping
  - trust the built request object instead of re-validating its semantics
- gateway:
  - own module-loading concerns only
  - do not own caller-owned request validation

### Related Non-Decision

This request-seam decision does not mean all evaluator-side validation belongs in `EvaluateEvidenceRequest`.

Returned test `result` validation is post-execution behavior and should therefore be handled in `EvaluateEvidenceResponse` construction, not in the request object and not in the gateway.

## Selected Response-Side Direction

### Response Validation Ownership

`EvaluateEvidenceResponse` should become the owning response-side construction surface for post-execution result validation.

Applied meaning:

- the use case orchestrates execution and gathers raw completed-test result content
- response construction validates and shapes the final outer evaluator response contract
- the gateway does not own test-result contract validation
- request construction and response construction remain separate bounded phases

### Conclusion Vocabulary

For completed test-owned results, the selected V2 conclusion vocabulary is:

- `true`
- `false`
- `inconclusive`
- `error`

Summary planning and output-contract work should use those values instead of the current `pass` / `fail` conclusion pair.

## Implementation Task Breakdown

### Slice 1: Request-Seam Refactor In `src/nape_evaluator/domain/use_case_models.py`

Goal:

- replace the current directly constructed request models with the selected builder-only V2 request seam

Tasks:

- add `EvaluateEvidenceRequest.builder()`
- add `EvaluateEvidenceRequestBuilder`
- convert `EvaluateEvidenceRequest` into the verified post-builder request object
- replace request-side `test_parameters` ownership with V2 caller-owned `evaluations`
- add bounded request support surfaces for:
  - `EvaluationSubject`
  - `EvaluationCriteria`
  - `EvaluationInput`
- update `TestInvocationRequest` so it carries:
  - `test_path`
  - verified `evaluations`
  - blocked execution state when needed
- add private builder validation helpers for:
  - top-level request shape
  - top-level `tests` array
  - per-test invocation shape
  - `subject.name`
  - `subject.data_type`
  - `criteria`
  - compatibility and no-coercion rules

Expected outcome:

- the use case can receive only a verified V2 request object
- request-build failure becomes the single evaluator-owned entrypoint for malformed caller input

### Slice 2: CLI Transport Refactor In `src/nape_evaluator/application/io/cli.py`

Goal:

- align the CLI adapter to the selected V2 packet-based transport model from Plan 02

Tasks:

- remove the V2 planning dependency on repeated `--test` plus positional `--test-parameters-file`
- add repeated `--invoke`
- add repeated `--invoke-file`
- add `--request-file`
- enforce `--request-file -` as stdin
- enforce mutual exclusivity between:
  - direct invocation flags
  - full-request transport
- decode:
  - repeated invocation packets for direct mode
  - one full outer request packet for `--request-file`
- map decoded boundary input into `EvaluateEvidenceRequest.builder()`
- keep transport-level errors in the CLI adapter:
  - unreadable file
  - invalid JSON
  - stdin read failure

Expected outcome:

- CLI parsing stays transport-only
- the builder owns V2 semantic request validation

### Slice 3: Use-Case Execution Refactor In `src/nape_evaluator/domain/use_cases.py`

Goal:

- update orchestration from the current tuple-returning, `test_parameters`-based runtime to the selected V2 request and result model

Tasks:

- switch the test call boundary to `evaluate(evidence, evaluations, metadata)`
- replace remaining request-side `test_parameters` assumptions with verified `evaluations`
- preserve evidence loading and shared-message contextualization where still valid
- update blocked-execution handling so it populates the selected outer V2 execution envelope
- collect raw completed-test result payloads for response construction rather than finalizing flat rows inline
- keep evaluator-owned execution failure handling distinct from completed test-owned `error` conclusions

Expected outcome:

- the use case becomes the V2 orchestration layer only
- request validation stays upstream and response validation stays downstream

### Slice 4: Response Construction Refactor In `src/nape_evaluator/domain/use_case_models.py` And `src/nape_evaluator/application/io/output_contract.py`

Goal:

- move result-envelope finalization and post-execution validation into `EvaluateEvidenceResponse`

Tasks:

- make `EvaluateEvidenceResponse` the owning response-construction surface for:
  - outer echoed request context
  - evaluator-owned `execution`
  - inner test-owned `result`
- validate completed-test `result` content there
- validate allowed V2 conclusion values:
  - `true`
  - `false`
  - `inconclusive`
  - `error`
- update summary counting rules in `output_contract.py` so counts are driven by:
  - `execution.executed`
  - `result.conclusion`
- preserve evaluator messages as evaluator-owned content

Expected outcome:

- completed-test result validation becomes centralized and bounded
- stdout serialization no longer assumes flat `outcome` / `reason` rows

### Slice 5: Test-Of-Detail Fixture And Contract-Test Refactor In `tests/`

Goal:

- replace current V1/V1.5 contract assumptions in tests and example test-of-detail files

Tasks by file:

- `tests/test_cli_adapter.py`
  - update parser and request-mapping tests for `--invoke`, `--invoke-file`, and `--request-file`
- `tests/test_cli_contract.py`
  - replace old output expectations with V2 invocation-packet and structured-result expectations
- `tests/test_evaluator_use_case.py`
  - replace `test_parameters` assertions with `evaluations`
  - replace tuple-return assumptions with structured `result` expectations
  - add response-validation and conclusion-vocabulary assertions
- `tests/test_output_contract.py`
  - update summary-counting assertions to `true` / `false` / `inconclusive` / `error`
- `tests/json/test_of_detail/verify_author_complete.py`
  - update the sample test to `evaluate(evidence, evaluations, metadata)`
  - return a structured `result`

Expected outcome:

- automated tests become the new source of truth for the V2 runtime contract

### Slice 6: Permanent Contract And User-Doc Alignment

Goal:

- move from “selected V2 direction” notes to concrete V2 contract documentation once implementation shape is stable

Tasks:

- update `docs/reference/evaluator-contract.md`
- update `docs/user/cli-reference.md`
- update `docs/user/quickstart.md`
- update `docs/user/test-of-detail-authoring.md`
- update `docs/product/current-evaluator-reference.md` only when runtime behavior actually changes
- reconcile examples in `docs/product/test-parameter-exploration.md` or archive/supersede it as needed

Expected outcome:

- permanent docs describe the implemented V2 CLI/runtime shape rather than parallel current-versus-selected notes

## Recommended Execution Order

1. Slice 1: request seam in `use_case_models.py`
2. Slice 2: CLI transport in `cli.py`
3. Slice 3: orchestration in `use_cases.py`
4. Slice 4: response construction and summary in `EvaluateEvidenceResponse` and `output_contract.py`
5. Slice 5: tests and fixtures
6. Slice 6: permanent docs

Rationale:

- the verified request seam is the main safety boundary and should exist before CLI and use-case rewiring
- CLI mapping should target the selected builder shape, not a temporary intermediate request model
- the use case and response construction refactors depend on the request and transport shape being settled
- tests should lock the new contract after the runtime surfaces are updated
- permanent docs should follow implemented truth, not lead it

## Immediate Next Execution Slice

If implementation starts next, the first concrete coding slice should be:

1. create the V2 request support surfaces in `src/nape_evaluator/domain/use_case_models.py`
2. introduce `EvaluateEvidenceRequest.builder()` and `try_build()`
3. add request-builder tests for:
   - valid `tests[*].evaluations[*]` packets
   - invalid `subject.name`
   - invalid `subject.data_type`
   - invalid `criteria`
   - incompatible `data_type` / `criteria`

This is the best first slice because it establishes the verified seam that every later file will depend on.

## Done Criteria

This plan is ready to close when:

- the code-path audit is captured durably
- implementation phases are sequenced clearly
- the implementation task breakdown is explicit by file and test surface
- Plan 02 dependencies are explicit instead of implicit
- remaining runtime ambiguities are isolated into answerable implementation questions
