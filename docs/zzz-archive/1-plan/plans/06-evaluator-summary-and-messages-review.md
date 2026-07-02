> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Plan 06: Evaluator Summary And Messages Review

## Completion Outcome

This plan is now complete.

Selected closure decision:

- keep `evaluator.messages` as the top-level evaluator-owned message stream
- use distinct-event message counting semantics rather than duplicated contextual rows
- use only `true`, `false`, and `inconclusive` as result conclusions
- represent blocked invocations with evaluator-synthesized structured `inconclusive` results
- include `scope`, `affected_tests`, and `stack_trace` in the evaluator message contract
- align permanent docs, examples, and executable sample fixtures to the landed contract

Closure verification:

- focused contract and orchestration tests were updated to the landed summary/message semantics
- broader regression passed with `python3 -m unittest discover`

## Goal

Review, clarify, and if needed tighten how evaluator-level `summary` and `messages` work, especially when one evidence file is evaluated by multiple requested tests.

## Implementation Status

The approved contract change in this plan is now implemented.

Landed behavior:

- `evaluator.messages` stays top-level and uses distinct-event semantics
- messages now carry:
  - `scope`
  - `affected_tests`
  - `stack_trace`
- valid result conclusions are now:
  - `true`
  - `false`
  - `inconclusive`
- blocked invocations now carry evaluator-synthesized structured `inconclusive` results
- invalid completed-test result contracts are normalized to completed `inconclusive` results
- permanent docs, examples, and executable sample test-of-detail fixtures are aligned to this contract

## Why This Is Its Own Plan

The evaluator already distinguishes between:

- test-owned completed results
- evaluator-owned operational notices

That distinction is important, but it is not yet explained with enough precision in the permanent docs or examples for multi-test runs.

There is also a likely follow-on product decision:

- whether evaluator-owned operational errors should force the related test-side conclusion to become `inconclusive`

That follow-on should not be mixed into the first clarification pass.

This plan therefore starts with research, contract clarification, examples, and test coverage review before any deeper contract change is selected.

## Baseline

Read first:

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/handoffs/06-evaluator-summary-and-messages-review.md`
3. `docs/product/current-evaluator-reference.md`
4. `docs/product/nape-evaluator-product-spec.md`
5. `docs/reference/evaluator-contract.md`
6. `src/nape_evaluator/domain/use_cases.py`
7. `src/nape_evaluator/application/io/output_contract.py`
8. `tests/test_evaluator_use_case.py`
9. `tests/test_output_contract.py`

## Current Planning Question

This workstream is centered on two immediate product questions:

1. should evaluator-level summary data remain in the contract
2. what was `evaluator.messages` originally intended for, and does that purpose still justify keeping it

The current preliminary answer is:

- keep `evaluator.summary`
- keep `evaluator.messages`
- tighten the explanation and examples so consumers can clearly distinguish:
  - evaluator-owned operational errors and warnings
  - test-owned `result.reason`
  - completed-test `conclusion: "error"`
  - blocked execution represented through `execution` plus evaluator messages

## Selected Follow-On Proposal

The clarification pass in this plan has now produced a selected contract-change proposal for a later follow-on.

This is not current runtime behavior.

It is the selected proposed direction to use if Plan 06 continues from clarification into contract change.

### Selected Direction

Use top-level evaluator messages with distinct-event semantics.

Do not group messages under each result item.

Do not keep the current duplicated contextual-row counting model as the long-term design.

Selected points:

- keep `evaluator.messages` as a top-level evaluator-owned stream
- treat each `evaluator.messages[*]` item as one distinct evaluator event
- add explicit message scope:
  - `request`
  - `test`
- use `affected_tests` on request-scoped shared events
- stop using `error` as a result conclusion
- valid result conclusions become:
  - `true`
  - `false`
  - `inconclusive`
- blocked test invocations should return evaluator-synthesized:
  - `result.conclusion: "inconclusive"`
  - while still preserving:
    - `execution.executed: false`
    - `execution.status: "blocked"`

### Selected Rationale

This direction was selected because it gives a clearer deductive model for large multi-test invocations:

- message counts reflect distinct evaluator events rather than duplicated contextual rows
- shared evidence-side conditions can be represented once and still identify all affected tests
- per-test blocked outcomes still receive one conclusion value
- evaluator-owned operational errors remain distinguishable from test-owned reasoning

### Selected Proposed JSON Shape

```json
{
  "results": [
    {
      "test": "./verify_author_complete.py",
      "evidence": "./author_verification",
      "evaluations": [
        {
          "subject": {
            "name": "status",
            "data_type": "text"
          },
          "criteria": {
            "equals": "complete"
          }
        }
      ],
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "true",
        "facts": [
          {
            "name": "status",
            "value": "complete",
            "value_type": "text",
            "status": "found"
          }
        ],
        "reason": "The author has achieved the expected status."
      }
    },
    {
      "test": "./verify_author_approved.py",
      "evidence": "./author_verification",
      "evaluations": [
        {
          "subject": {
            "name": "status",
            "data_type": "text"
          },
          "criteria": {
            "equals": "approved"
          }
        }
      ],
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "false",
        "facts": [
          {
            "name": "status",
            "value": "complete",
            "value_type": "text",
            "status": "found"
          }
        ],
        "reason": "The author did not achieve the expected status of approved."
      }
    },
    {
      "test": "./verify_author_roles.py",
      "evidence": "./author_verification",
      "evaluations": [
        {
          "subject": {
            "name": "roles",
            "data_type": "array"
          },
          "criteria": {
            "required": true
          }
        }
      ],
      "execution": {
        "executed": false,
        "status": "blocked"
      },
      "result": {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": "The test could not be completed because the evaluator could not import the test file."
      }
    }
  ],
  "evaluator": {
    "messages": [
      {
        "scope": "request",
        "level": "warning",
        "source": "evaluator",
        "code": "missing_extension_text_fallback",
        "message": "Evidence file had no extension and was evaluated as text.",
        "evidence_file": "./author_verification",
        "test_file": null,
        "affected_tests": [
          "./verify_author_complete.py",
          "./verify_author_approved.py",
          "./verify_author_roles.py"
        ],
        "stack_trace": null
      },
      {
        "scope": "test",
        "level": "error",
        "source": "evaluator",
        "code": "test_import_error",
        "message": "Failed to import the necessary files.",
        "evidence_file": "./author_verification",
        "test_file": "./verify_author_roles.py",
        "affected_tests": null,
        "stack_trace": "Traceback (most recent call last): ..."
      }
    ],
    "summary": {
      "count": 3,
      "ran": 2,
      "true": 1,
      "false": 1,
      "inconclusive": 1,
      "message_count": 2,
      "message_info": 0,
      "message_warning": 1,
      "message_error": 1
    }
  }
}
```

### Selected Summary Rules

Under the selected proposed direction:

- `summary.count` is requested test count
- `summary.ran` is completed-test count where the Python test completed
- `summary.true`, `summary.false`, and `summary.inconclusive` are result conclusion counts
- there is no `summary.error` because `error` is removed from the conclusion vocabulary
- `summary.message_count` is the count of distinct emitted evaluator events
- `summary.message_info`, `summary.message_warning`, and `summary.message_error` count distinct emitted evaluator events by level

### Stack Trace Requirement

The selected proposed direction also adds an explicit stack-trace rule for evaluator messages.

Use:

- `stack_trace: null` when no stack trace applies
- `stack_trace: "<trace text>"` when an evaluator error has stack-trace detail worth preserving

Priority cases:

- evaluator execution errors
- test execution errors
- import-related failures when traceback detail is available

Rationale:

- large invocations need enough diagnostic detail to explain operational failures without forcing users to reproduce them immediately
- execution errors are especially hard to reason about from a short message alone
- attaching stack-trace detail to the evaluator message preserves the evaluator-owned/test-owned boundary while still making the failure diagnosable

## Step 1.0 Recommended Answers For Review

The following recommendations are the proposed answers for the next contract-detail lock.

They are not yet implementation instructions.

They are the reviewable recommendations to approve or adjust before implementation begins.

### Review Question 1: What exact shape should `stack_trace` use?

Question:

Should `stack_trace` be:

- a raw multiline string
- a structured array of frames
- or omitted entirely when absent

Recommendation:

- use `stack_trace: "<raw multiline string>"` when trace text exists
- use `stack_trace: null` when trace text does not apply
- always keep the field present on evaluator messages in the future-direction contract

Tradeoffs:

- raw multiline string
  - pros:
    - preserves the original traceback exactly
    - easiest to capture from Python runtime failures
    - easiest for humans to read and copy into debugging workflows
  - cons:
    - less structured for programmatic frame analysis
- structured frame array
  - pros:
    - easier for tooling to inspect frame-by-frame
    - could support richer UI rendering later
  - cons:
    - larger implementation burden
    - risks losing fidelity to the original Python traceback text
    - harder to normalize consistently across failure types
- omitted when absent
  - pros:
    - slightly smaller payload
  - cons:
    - creates field-presence branching instead of stable contract shape

Rationale:

- the evaluator’s immediate need is diagnosability, not traceback analytics
- Python already produces human-meaningful traceback text naturally
- a stable `stack_trace` field with `null` when absent is easier for downstream consumers than optional field presence

### Review Question 2: For which evaluator errors should `stack_trace` be included?

Question:

Should `stack_trace` be included for:

- only execution and import-style failures
- or every evaluator `error` message whenever traceback text exists

Recommendation:

- include `stack_trace` on every evaluator `error` message when traceback text actually exists
- do not synthesize fake stack traces for non-exception conditions such as:
  - missing file detected without traceback detail
  - unsupported evidence type
  - request-scoped warnings

Tradeoffs:

- execution/import-only rule
  - pros:
    - simpler mental model
    - avoids attaching trace fields to simpler operational errors
  - cons:
    - arbitrary boundary
    - future code paths may produce useful traceback text outside those categories
- any evaluator error with real traceback text
  - pros:
    - consistent rule
    - no need to classify failures narrowly before deciding whether trace text is allowed
    - preserves useful diagnostics wherever the runtime naturally has them
  - cons:
    - some error rows may carry more detail than others

Rationale:

- “include it whenever traceback text exists” is the cleanest rule
- it keeps the contract simple:
  - evaluator warning or non-exception condition:
    - `stack_trace: null`
  - evaluator error raised from an exception path with available traceback text:
    - `stack_trace: "<trace text>"`

### Review Question 3: How should request-scoped shared messages identify affected tests?

Question:

For request-scoped shared events, should the message use:

- `test_file: null` plus `affected_tests`
- or repeat a primary `test_file` alongside `affected_tests`

Recommendation:

- use `test_file: null`
- use `affected_tests: [ ... ]` for request-scoped shared events
- reserve non-null `test_file` for `scope: "test"` messages only

Tradeoffs:

- `test_file: null` plus `affected_tests`
  - pros:
    - clean separation between request-scoped and test-scoped semantics
    - avoids ambiguity about whether one test is “primary”
    - easier deduction for consumers
  - cons:
    - consumers must read `affected_tests` for request-scoped events
- repeat a primary `test_file` too
  - pros:
    - might be convenient for some simple consumers
  - cons:
    - introduces ambiguity
    - risks inconsistent interpretation of a request-scoped event as test-specific

Rationale:

- one field should mean one thing
- if a message is request-scoped, it should not pretend to belong to one test
- `affected_tests` is the correct place to express scope impact

### Review Question 4: How standardized should blocked `inconclusive` `result.reason` be?

Question:

When the evaluator synthesizes a blocked `inconclusive` result, should `result.reason` be:

- standardized by failure type
- or free-text per individual code path

Recommendation:

- use standardized evaluator-generated wording by failure type
- allow insertion of precise dynamic detail where useful
- keep the wording template stable enough that readers can quickly recognize the class of failure

Recommended pattern:

- base sentence:
  - `The test could not be completed because ...`
- then append specific failure detail:
  - missing evidence file
  - evidence load failure
  - test file not found
  - test import failure
  - test execution failure

Example:

- `The test could not be completed because the evaluator could not import the test file.`
- `The test could not be completed because the evaluator could not load the evidence file.`

Tradeoffs:

- standardized wording
  - pros:
    - easier for users to scan across many blocked tests
    - easier to document
    - easier to keep consistent with evaluator messages
  - cons:
    - slightly less flexible
- free-text by code path
  - pros:
    - allows very tailored explanations
  - cons:
    - harder to keep consistent
    - increases drift and ambiguity across failure types

Rationale:

- a standardized opening sentence gives the user immediate meaning:
  - this is not a completed true/false judgment
  - this is an evaluator-blocked inconclusive outcome
- dynamic detail can still preserve specificity without sacrificing consistency

### Review Question 5: What is the ownership model for blocked `result.reason` under the proposed direction?

Question:

Once blocked invocations return `result.conclusion: "inconclusive"`, what should `result.reason` mean?

Recommendation:

- for completed tests:
  - `result.reason` remains test-owned reasoning
- for blocked tests:
  - `result.reason` becomes evaluator-synthesized reasoning explaining why the test could not complete
- document that this is an intentional dual-source field keyed by `execution.executed`

Tradeoffs:

- keep `result.reason` test-owned only
  - pros:
    - preserves original ownership purity
  - cons:
    - blocked inconclusive results would need some other field for the user-facing explanation
    - makes the per-result reading model harder
- allow evaluator-synthesized `reason` on blocked results
  - pros:
    - keeps every result row self-explanatory
    - supports the new “no error, only inconclusive” conclusion rule
    - avoids forcing consumers to join the meaning from another location before understanding the result row
  - cons:
    - `reason` is no longer purely test-authored in every case

Rationale:

- the user’s selected direction now requires one conclusion per invocation
- once blocked invocations also carry a conclusion, the result row should explain itself directly
- that ownership split is acceptable if it is documented explicitly:
  - completed result reason: test-owned
  - blocked inconclusive reason: evaluator-owned

### Review Question 6: Are any extra evaluator message fields needed beyond `scope`, `affected_tests`, and `stack_trace`?

Question:

Beyond the already selected message shape, should the future-direction contract add any more evaluator message fields now?

Current selected base fields already include:

- `scope`
- `level`
- `source`
- `code`
- `message`
- `evidence_file`
- `test_file`
- `affected_tests`
- `stack_trace`

Recommendation:

- do not add any extra evaluator message fields now
- keep the proposed message shape limited to the current base fields plus:
  - `scope`
  - `affected_tests`
  - `stack_trace`

Tradeoffs:

- add more fields now
  - pros:
    - could anticipate future UI or analytics needs
    - might reduce later contract evolution for niche cases
  - cons:
    - increases contract surface without a current demonstrated need
    - makes implementation and docs heavier
    - creates more long-term compatibility burden
- keep the field set minimal now
  - pros:
    - easier to reason about
    - easier to implement consistently across all error paths
    - preserves room for later expansion based on real needs
  - cons:
    - a later use case may require another contract change

Rationale:

- the proposed field set already supports the important deductions:
  - what happened
  - how severe it is
  - whether it is request-scoped or test-scoped
  - which tests were affected
  - where the failure occurred
  - how to debug it when a traceback exists
- adding more fields now would be speculative rather than requirement-driven

Explicit non-recommendations for now:

- do not add timestamps
- do not add message ids
- do not add machine-parsed traceback frames
- do not add retryability hints
- do not add separate category/subcategory fields

If later needed, those can be introduced from a smaller, more stable base contract.

### Review Question 7: Should blocked-result standardized wording be very compact or slightly more explanatory by default?

Question:

When the evaluator synthesizes a blocked `inconclusive` result, should the default `result.reason` wording be:

- very compact
- or slightly more explanatory

Recommendation:

- use slightly more explanatory wording by default
- keep it standardized and concise, but not so terse that the user still has to infer what happened

Recommended pattern:

- first sentence:
  - `The test could not be completed, so the conclusion is inconclusive.`
- second clause or sentence:
  - identify the evaluator-owned failure type in plain language

Examples:

- `The test could not be completed, so the conclusion is inconclusive. The evaluator could not import the test file.`
- `The test could not be completed, so the conclusion is inconclusive. The evaluator could not load the evidence file.`
- `The test could not be completed, so the conclusion is inconclusive. The evaluator encountered an execution error before the test could finish.`

Tradeoffs:

- very compact wording
  - pros:
    - smaller payloads
    - visually lighter in large outputs
  - cons:
    - forces readers to infer more from message codes or companion evaluator messages
    - weaker for first-time users or manual review
- slightly more explanatory wording
  - pros:
    - easier to understand in isolation
    - supports the new no-`error` conclusion model better
    - reduces ambiguity when a user reads only one result row first
  - cons:
    - slightly longer output text

Rationale:

- under the proposed direction, blocked invocations now carry a conclusion and a reason
- that reason should do enough work that the row is understandable even before the user cross-references `evaluator.messages`
- slightly more explanatory wording gives that clarity without becoming verbose

Recommended style constraints:

- keep the wording standardized by failure type
- keep it to one short explanatory statement plus one failure-specific statement
- do not embed full traceback text in `result.reason`
- keep stack-trace detail only in `evaluator.messages[*].stack_trace`

## Research Focus

The research pass should answer these precisely:

1. what the runtime does today for:
   - one successful test
   - multiple successful tests against the same evidence
   - evidence-level warnings shared across multiple tests
   - evaluator-owned blocked execution
   - completed tests that return `conclusion: "error"`
2. whether current `message_count` semantics reflect:
   - distinct evaluator events
   - contextualized per-test message rows
3. where permanent docs are currently clear versus ambiguous
4. what examples are missing for users and maintainers

## Approved-Direction Implementation Planning

The approved future-direction contract is now specific enough to convert into implementation planning.

This section defines the intended execution order and code/document surfaces.

It still does not authorize code changes by itself.

### Implementation Goal

Replace the current evaluator message and blocked-result behavior with the approved direction:

- top-level `evaluator.messages` stays
- message semantics move from duplicated contextual rows to distinct events
- message shape gains:
  - `scope`
  - `affected_tests`
  - `stack_trace`
- completed/result conclusion vocabulary becomes:
  - `true`
  - `false`
  - `inconclusive`
- `error` is removed from result conclusions and from summary conclusion counts
- blocked invocations return evaluator-synthesized:
  - `result.conclusion: "inconclusive"`
  - `result.reason: <standardized evaluator wording>`
- `execution.executed` and `execution.status` remain the execution-truth source

### Main Contract Consequences

The approved direction changes these runtime meanings:

1. `result.reason` becomes dual-source:
   - test-owned when `execution.executed == true`
   - evaluator-owned when `execution.executed == false`
2. blocked invocations no longer return `result: null`
3. `summary.error` is removed
4. `summary.inconclusive` now includes:
   - completed tests that returned `inconclusive`
   - blocked invocations represented as evaluator-synthesized `inconclusive`
5. shared request-scoped evaluator notices are represented once with:
   - `scope: "request"`
   - `affected_tests`
6. traceback detail moves into `evaluator.messages[*].stack_trace`

### File-Level Change Plan

#### 1. `src/nape_evaluator/application/io/output_contract.py`

Purpose:

- redefine message-building helpers and summary counting rules

Planned changes:

- expand `build_message(...)` to support:
  - `scope`
  - `affected_tests`
  - `stack_trace`
- make the stable message shape always include those fields
- remove `summary.error`
- keep `summary.count`, `summary.ran`, `summary.true`, `summary.false`, `summary.inconclusive`
- keep `summary.message_count`, `summary.message_info`, `summary.message_warning`, `summary.message_error`
- ensure `message_count` counts distinct emitted evaluator events under the new semantics
- ensure blocked `inconclusive` results count toward `summary.inconclusive`

#### 2. `src/nape_evaluator/domain/use_case_models.py`

Purpose:

- update result-contract validation to the new conclusion vocabulary and blocked-result contract

Planned changes:

- remove `error` from `SUPPORTED_RESULT_CONCLUSIONS`
- update completed-result validation accordingly
- change response validation so blocked result rows no longer require `result is null`
- add validation rules for evaluator-synthesized blocked results:
  - `execution.executed == false`
  - `execution.status == "blocked"`
  - `result` must be present
  - `result.conclusion == "inconclusive"`
  - `result.reason` must be non-empty evaluator-generated text
  - `result.facts` should be an array, normally empty on blocked results
- keep completed-result contract strict for test-returned values

#### 3. `src/nape_evaluator/domain/use_cases.py`

Purpose:

- refactor orchestration so message generation follows distinct-event semantics and blocked results are synthesized consistently

Planned changes:

- replace `contextualize_messages(...)` with logic that can produce either:
  - one request-scoped shared message with `affected_tests`
  - one test-scoped message for a single test
- stop duplicating one shared evidence message once per test in normal multi-test runs
- capture traceback text for evaluator error paths where real traceback data exists
- standardize blocked-result synthesis by failure type
- create one helper responsible for blocked `inconclusive` result construction
- create one helper responsible for evaluator-message construction from:
  - shared evidence warnings
  - evidence load failures
  - test file not found
  - test import error
  - test execution error
  - evaluator execution error

Recommended internal helper breakdown:

- `_build_request_scoped_message(...)`
- `_build_test_scoped_message(...)`
- `_build_blocked_inconclusive_result(...)`
- `_format_blocked_reason(...)`
- `_capture_stack_trace(...)`

#### 4. `src/nape_evaluator/application/driver/evidence_gateway.py`

Purpose:

- align evidence-loader message production to the new message contract

Planned changes:

- stop assuming only:
  - `level`
  - `source`
  - `code`
  - `message`
  - `evidence_file`
  - `test_file`
- emit shared evidence-side notices in a form that the use case can translate into:
  - `scope: "request"`
  - `affected_tests`
  - `stack_trace`
- keep warning behavior intact for:
  - `missing_extension_text_fallback`
  - `unknown_extension_text_fallback`
- include `stack_trace` only when real exception traceback text exists

#### 5. `tests/test_output_contract.py`

Purpose:

- lock the new summary and message-shape semantics

Planned changes:

- remove assertions tied to `summary.error`
- add assertions for:
  - message shape containing `scope`, `affected_tests`, `stack_trace`
  - blocked `inconclusive` result counting
  - distinct-event counting for request-scoped warnings
  - no duplicated message counting for shared request-scoped conditions

#### 6. `tests/test_evaluator_use_case.py`

Purpose:

- lock orchestration behavior under the new contract

Planned changes:

- replace tests that expect duplicated shared messages per test
- add tests for:
  - one request-scoped warning affecting multiple tests
  - one test-scoped failure message
  - blocked invocation returns synthesized `inconclusive` result
  - execution/import failures include `stack_trace` when traceback text exists
  - blocked-result reason uses standardized evaluator wording

#### 7. `tests/test_cli_contract.py`

Purpose:

- lock CLI-visible JSON contract changes

Planned changes:

- remove assertions tied to `summary.error`
- update blocked-output assertions so:
  - `results[*].result` is no longer `null`
  - blocked rows carry `conclusion: "inconclusive"`
- add a multi-test CLI example assertion set for:
  - request-scoped warning
  - distinct-event message counting

#### 8. Permanent Docs

Primary update targets after code passes:

- `docs/product/current-evaluator-reference.md`
- `docs/product/nape-evaluator-product-spec.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/cli-reference.md`
- `docs/examples/README.md`

Planned doc changes:

- remove runtime references to conclusion `error`
- explain blocked synthesized `inconclusive` results
- explain dual-source `result.reason`
- explain request-scoped versus test-scoped evaluator messages
- document `stack_trace`
- replace current-row-count explanation with distinct-event semantics

### Recommended Execution Order

1. update output-contract helpers
2. update response-validation rules
3. refactor use-case message/result synthesis
4. align evidence-gateway message payloads
5. update unit tests for output/use-case behavior
6. update CLI contract tests
7. run focused tests
8. patch permanent docs and examples
9. run full relevant test suite

### Test Sequence

Focused first:

- `python3 -m unittest tests.test_output_contract`
- `python3 -m unittest tests.test_evaluator_use_case`
- `python3 -m unittest tests.test_cli_contract`

Then broader evaluator regression set:

- `python3 -m unittest tests.test_request_builder`
- `python3 -m unittest tests.test_output_contract tests.test_evaluator_use_case tests.test_cli_contract`

Expand further if failures indicate adjacent drift.

### Migration Notes

The approved direction is a clean contract change, not a compatibility layer.

Consumers will need to absorb these output changes:

- no `result.conclusion: "error"`
- no `summary.error`
- blocked `results[*].result` becomes structured `inconclusive` content instead of `null`
- `evaluator.messages[*]` gains:
  - `scope`
  - `affected_tests`
  - `stack_trace`
- shared request-scoped notices will no longer be duplicated once per test

### Risks To Watch During Implementation

1. accidental blending of test-owned and evaluator-owned reasoning beyond the approved blocked-result case
2. losing traceback fidelity while normalizing message shape
3. under-testing the distinction between:
   - completed `inconclusive`
   - blocked synthesized `inconclusive`
4. leaving stale docs or tests that still assume:
   - `summary.error`
   - `result: null` for blocked rows
   - duplicated shared warnings per test

### Definition Of Ready For Code Changes

Implementation work can start once:

- the approved direction remains unchanged
- this execution order is accepted
- no new product-level contract fields are added
- code changes are explicitly authorized in a later step

## Scope

In scope:

- review of current runtime `summary` and `messages` behavior
- documentation clarification of purpose, ownership, and interpretation
- concrete examples for:
  - single-test runs
  - multi-test runs
  - blocked execution
  - evaluator warning/error versus test `reason`
- tests that make multi-test message/summary behavior explicit
- recording follow-on design pressure if the current behavior is confusing or inconsistent

Out of scope for the first pass:

- changing the evaluator/test ownership boundary
- broad output-contract redesign
- silently changing message-count semantics without explicit documentation
- implementing the later “evaluator error should force inconclusive” rule before the clarification pass is complete

## Execution Strategy

### Phase 1: Research And Contract Audit

Deliverables:

- a precise current-behavior readout grounded in code and tests
- identification of any inconsistencies between:
  - runtime behavior
  - product/reference/user docs
  - test coverage

Questions to resolve:

1. are shared evidence-level messages intentionally duplicated per requested test, or just contextualized that way by current implementation convenience
2. does `summary.message_count` describe event count or output-row count
3. is the current generic top-level evaluator failure path sufficiently contextualized when multiple tests were requested

### Phase 2: Permanent Documentation Clarification

Deliverables:

- updates to permanent docs that explain:
  - why `evaluator.summary` exists
  - why `evaluator.messages` exists
  - how to read them together with `results[*].execution` and `results[*].result`
  - how to distinguish evaluator-owned operational messages from test-owned reasoning
- at least one explicit example showing multiple tests against one evidence file
- at least one explicit example showing a blocked test with evaluator error messaging

Primary target docs:

- `docs/product/current-evaluator-reference.md`
- `docs/reference/evaluator-contract.md`
- `docs/user/cli-reference.md`
- `docs/user/quickstart.md` if needed
- `docs/examples/README.md` if needed

### Phase 3: Example And Test Alignment

Deliverables:

- test coverage that locks down the documented current behavior
- examples that make multi-test summary/message semantics visible

Priority test surfaces:

- `tests/test_output_contract.py`
- `tests/test_evaluator_use_case.py`
- `tests/test_cli_contract.py` if the CLI examples need stronger contract assertions

### Phase 4: Follow-On Design Decision Preparation

Deliverables:

- an explicit note capturing whether a second work item should change runtime semantics

The first expected follow-on is:

- whether evaluator-owned operational errors should force a related test-side conclusion to become `inconclusive` instead of remaining represented only as:
  - `execution.executed: false`
  - `execution.status: "blocked"`
  - `result: null`
  - evaluator `error` messages

That follow-on should be handled only after the current contract is documented clearly enough that the before/after change is easy to reason about.

## Done Criteria

This plan is ready to close when:

- permanent docs explain `summary` and `messages` clearly for both single-test and multi-test runs
- users can clearly distinguish evaluator-owned operational errors from test-owned `reason`
- examples exist that show the distinction concretely
- tests cover the documented current behavior tightly enough to prevent silent drift
- any remaining contract-change questions are recorded as explicit follow-on decisions rather than left implied
