# Response Handling

This page explains how software should parse evaluator output and interpret it correctly inside another software system.

Read this page after:

- [integration-model.md](integration-model.md)
- [request-and-invocation.md](request-and-invocation.md)

The main integration risk after request construction is not usually JSON parsing itself.

The main risk is misinterpreting what the evaluator is telling you.

This page is about avoiding that mistake.

## The Core Interpretation Problem

A wrapper that only reads one field such as:

- exit status
- `result.conclusion`
- `summary.message_error`

will lose important meaning.

The evaluator contract is intentionally richer than one pass/fail bit.

Your software should parse the whole response and classify it deliberately.

## The Outer Response Shape

The evaluator prints one JSON object to stdout with this top-level structure:

```json
{
  "results": [],
  "evaluator": {
    "messages": [],
    "summary": {}
  }
}
```

Top-level meaning:

- `results`
  - one row per requested test invocation
- `evaluator.messages`
  - evaluator-owned operational context
- `evaluator.summary`
  - aggregate counts across the invocation

Your wrapper should not collapse these into one flat list of outcomes.

Each top-level section has a different owner and a different meaning.

## How To Parse The Response Safely

At minimum, your software should:

1. parse stdout as JSON
2. verify the top-level object contains:
   - `results`
   - `evaluator`
3. verify `evaluator` contains:
   - `messages`
   - `summary`
4. iterate `results[*]` row by row
5. classify each row using:
   - `execution.executed`
   - `execution.status`
   - `result.conclusion`
6. separately classify evaluator messages
7. use `summary` as aggregate confirmation, not as the only source of meaning

## Per-Result Interpretation

Each `results[*]` item is one requested test invocation outcome.

Each row contains:

- `test`
- `evidence`
- `evaluations`
- `execution`
- `result`

The first thing your wrapper should check on each row is not `result.conclusion`.

It should check:

- `execution.executed`
- `execution.status`

## Why `execution` Must Be Read First

`result.conclusion` alone is not enough.

The value `inconclusive` can mean at least two materially different things:

1. the test completed and intentionally returned `inconclusive`
2. the invocation was blocked and the evaluator synthesized the `inconclusive` result

Those are different operational situations.

The deciding fields are:

- `execution.executed`
- `execution.status`

## Row Classification Rules

### Case 1: Completed `true`

Meaning:

- `execution.executed == true`
- `execution.status == "completed"`
- `result.conclusion == "true"`

Interpretation:

- the Python test completed
- it concluded that the evaluated condition is true

### Case 2: Completed `false`

Meaning:

- `execution.executed == true`
- `execution.status == "completed"`
- `result.conclusion == "false"`

Interpretation:

- the Python test completed
- it concluded that the evaluated condition is false

### Case 3: Completed `inconclusive`

Meaning:

- `execution.executed == true`
- `execution.status == "completed"`
- `result.conclusion == "inconclusive"`

Interpretation:

- the Python test completed
- the test did not produce `true` or `false`
- the reason may include:
  - missing fact establishment
  - invalid fact parsing
  - test-known contract mismatch
  - completed-result normalization for an invalid returned result contract

### Case 4: Blocked `inconclusive`

Meaning:

- `execution.executed == false`
- `execution.status == "blocked"`
- `result.conclusion == "inconclusive"`

Interpretation:

- the Python test did not complete successfully as an executed evaluation step
- the evaluator synthesized the blocked result row
- the operational cause should also appear in `evaluator.messages`

## The Meaning Of `result.reason`

Your wrapper must not assume `result.reason` always comes from the same owner.

### When The Test Completed

If:

- `execution.executed == true`

then:

- `result.reason` is usually test-owned reasoning

In the ordinary completed case, it explains the completed evaluation result returned by the Python test.

There is one important exception in the current runtime:

- if the test completed but returned an invalid result contract, the evaluator normalizes that completed row to `conclusion == "inconclusive"`
- in that normalization path, `result.reason` is evaluator-authored explanatory text about the invalid completed result contract, not ordinary test-authored reasoning

### When The Invocation Was Blocked

If:

- `execution.executed == false`

then:

- `result.reason` is evaluator-owned blocked-result reasoning

It explains why the invocation could not be completed.

Practical wrapper rule:

- treat `result.reason` first as completed-row reasoning versus blocked-row reasoning
- when the row is completed, assume the text is usually test-authored unless the completed row reflects evaluator normalization of an invalid test result contract

## The Meaning Of `result.facts`

`result.facts` is owned by the completed test result model.

In practice:

- completed `true` often includes established facts
- completed `false` often includes established facts
- completed `inconclusive` may include partial, invalid, or missing fact records
- blocked `inconclusive` often has:
  - `facts: []`

Your wrapper should not assume:

- an empty `facts` array means success
- a non-empty `facts` array means success

Facts are supporting evaluation information, not a top-level status by themselves.

## Evaluator Messages

`evaluator.messages` is the evaluator-owned operational notice stream.

Use it for operational interpretation such as:

- evidence loading warnings
- evidence loading errors
- test file not found
- import failures
- evaluator/runtime execution failures
- request-scoped shared warnings that affect more than one requested test

Do not use `evaluator.messages[*].message` as a substitute for the completed test's claim reasoning.

That completed reasoning lives in:

- `results[*].result.reason`

## Message Fields

Each evaluator message contains:

- `scope`
- `level`
- `source`
- `code`
- `message`
- `evidence_file`
- `test_file`
- `affected_tests`
- `stack_trace`

### `scope`

Current supported values:

- `request`
- `test`

Interpretation:

- `request`
  - one evaluator event applies to more than one requested test or to the request as a whole
- `test`
  - one evaluator event is specific to one requested test

### `affected_tests`

Use this only for request-scoped shared events.

Interpretation:

- if `scope == "request"`, `affected_tests` identifies which requested tests were impacted
- if `scope == "test"`, this should be `null`

### `test_file`

Interpretation:

- if `scope == "test"`, this identifies the one affected test path
- if `scope == "request"`, this should be `null`

### `stack_trace`

Interpretation:

- `null` means no traceback detail is attached
- string content means traceback detail exists and your wrapper may choose to retain, log, or display it according to your own operational policy

## Request-Scoped Versus Test-Scoped Messages

This distinction matters in multi-test runs.

### Request-Scoped Message

Example meaning:

- one evidence-side warning applies to several requested tests

Interpretation rule:

- do not duplicate this into one invented wrapper-local message per test unless your own product explicitly needs that denormalized view

The raw evaluator contract is already giving you the cleaner source event:

- one message
- many affected tests

### Test-Scoped Message

Example meaning:

- one test file could not be imported

Interpretation rule:

- this event belongs to one test invocation context

## Summary Interpretation

`evaluator.summary` is an aggregate view.

It contains:

- `count`
- `ran`
- `true`
- `false`
- `inconclusive`
- `message_count`
- `message_info`
- `message_warning`
- `message_error`

### What Summary Is Good For

Use summary for:

- quick aggregate reporting
- sanity checks
- dashboards
- wrapper-level rollups

### What Summary Is Not Good For

Do not use summary as a replacement for row-by-row interpretation.

Summary does not tell you by itself:

- which test was blocked
- which completed row was inconclusive
- which message applied to which tests
- what exact reason or facts were returned

## Summary Field Meanings

### `count`

How many requested test invocations the caller asked for.

### `ran`

How many test invocations completed the `evaluate(...)` contract.

Important:

- `ran < count` means at least one invocation was blocked

### `true`, `false`, `inconclusive`

Counts from result conclusions across the returned rows.

Important:

- `inconclusive` includes both:
  - completed inconclusive rows
  - blocked evaluator-synthesized inconclusive rows

That is why summary alone cannot tell you which kind you have.

### `message_count`

Count of distinct emitted evaluator events.

Important:

- this is not a count of invented per-test duplicates
- request-scoped shared notices count once

### `message_info`, `message_warning`, `message_error`

Counts of distinct evaluator events by level.

Important:

- `message_error > 0` means evaluator/runtime operational problems were reported
- it does not mean every test row necessarily failed in the same way

## Recommended Response Classification Order

A robust wrapper should usually classify the parsed response in this order:

1. classify each `results[*]` row
2. classify evaluator messages
3. use summary to confirm the aggregate picture
4. map the evaluator contract into your product’s own model

That order is better than:

1. read `summary`
2. guess what happened

because the row-level and message-level data contain the actual explanation.

## A Practical Wrapper Classification Model

Your software will usually need its own internal categories.

A useful first-pass wrapper model might distinguish:

1. completed-true
2. completed-false
3. completed-inconclusive
4. blocked-inconclusive
5. evaluator-warning-present
6. evaluator-error-present
7. process-contract-unavailable

This is usually more useful than trying to flatten everything into one final boolean.

## Example Interpretation Scenarios

### Scenario 1: One Completed True Result

Likely signals:

- one row
- `execution.executed == true`
- `result.conclusion == "true"`
- no evaluator messages

Interpretation:

- normal successful evaluation

### Scenario 2: One Completed Inconclusive Result

Likely signals:

- one row
- `execution.executed == true`
- `result.conclusion == "inconclusive"`
- maybe no evaluator messages

Interpretation:

- the test completed but could not conclude true or false

### Scenario 3: One Blocked Invocation

Likely signals:

- one row
- `execution.executed == false`
- `result.conclusion == "inconclusive"`
- at least one evaluator `error` message

Interpretation:

- the invocation did not complete
- the evaluator, not the completed test, is telling you why

### Scenario 4: Several Tests With One Shared Warning

Likely signals:

- several rows in `results`
- one request-scoped warning message
- `affected_tests` listing several test paths
- `summary.message_warning == 1`

Interpretation:

- one shared operational notice applied across several test invocations

## What Your Wrapper Should Usually Persist

For diagnosis, a wrapper should strongly consider retaining:

- the full parsed evaluator JSON
- the exact request packet sent
- subprocess exit status
- stderr
- wrapper-local correlation identifiers

At minimum, retain these for any run with:

- blocked results
- completed `inconclusive`
- evaluator `message_error`

## Common Interpretation Mistakes

### Mistake 1: Reading Only `result.conclusion`

Problem:

- you cannot distinguish completed versus blocked `inconclusive`

Better:

- read `execution` first

### Mistake 2: Reading Only `summary`

Problem:

- you lose row-level detail and message-level ownership

Better:

- use summary as aggregate confirmation after row and message classification

### Mistake 3: Treating Evaluator Messages As Test Claims

Problem:

- evaluator operational failures and test reasoning become mixed

Better:

- keep `evaluator.messages[*].message` and `results[*].result.reason` distinct in your product model

### Mistake 4: Treating `message_error` As Equivalent To A Failed Business Decision

Problem:

- evaluator operational issues and domain conclusions are not the same thing

Better:

- treat evaluator messages as operational context
- treat per-test conclusions as evaluation outcomes

## Relationship To The Next Pages

After this page:

- read [production-hardening.md](production-hardening.md) for operational guardrails
- use [worked-examples.md](worked-examples.md) for end-to-end wrapper examples
