# Production Hardening

This page explains how to harden evaluator integration in a larger software system.

Read this page after:

- [request-and-invocation.md](request-and-invocation.md)
- [response-handling.md](response-handling.md)

The earlier pages explain how to call the evaluator correctly and how to interpret the response correctly.

This page explains how to make that integration safer, more diagnosable, and more operationally trustworthy.

## What “Hardening” Means Here

In this guide, hardening means making explicit decisions about:

- trusted-code execution
- timeout behavior
- subprocess failure handling
- request and response artifact retention
- logging and observability
- wrapper-side failure classification
- operational traceability

This is not about changing the evaluator contract.

It is about making your wrapper resilient around that contract.

## The Main Production Risks

The current evaluator has a few risks that a wrapper must treat as first-class concerns.

### 1. Python Test Files Are Executable Code

The evaluator dynamically imports and executes Python test-of-detail files.

That means:

- a test path is not inert configuration
- a test file is not just data
- evaluator execution is not a sandbox

If your wrapper lets users or other systems influence test selection, you must decide how that selection is constrained.

### 2. Evidence And Request Problems Can Produce Different Failure Shapes

Your wrapper must distinguish between:

- process launch failure
- process timeout
- invalid or unavailable stdout contract
- evaluator operational error messages
- blocked invocations
- completed `inconclusive`

If you collapse all of those into one “evaluation failed” bucket, operators lose the ability to tell what actually happened.

### 3. Replay And Traceability Matter

When a run is disputed or needs diagnosis, the minimum useful questions are usually:

- what evidence path was used
- what exact request packet was sent
- which test file or files were requested
- what stdout JSON came back
- what stderr came back
- whether the process timed out

If your wrapper cannot answer those questions, support and audit work become harder very quickly.

## Trusted-Code Guardrails

### Recommended Position

Treat test files as trusted executable artifacts that must be governed explicitly by the surrounding software.

Good wrapper-side controls include:

- only allow test files from approved directories
- only allow test files selected from a curated manifest or registry
- record the exact path that was executed
- record the version or commit identity of the test bundle when available
- avoid taking arbitrary end-user raw file paths and executing them directly without policy

### What Not To Imply

Your wrapper should not imply:

- that evaluator execution is sandboxed
- that test files are harmless because they return JSON
- that user-selected paths are safe merely because the evaluator validates request shape

Request validation and code trust are different concerns.

## Timeout Strategy

Your wrapper should set an explicit timeout for evaluator execution.

Do not rely on indefinite waiting by default.

### Why Timeouts Matter

The evaluator may be delayed by:

- large evidence files
- expensive test logic
- stalled filesystem behavior
- unexpected code paths inside trusted test files

Without a timeout, your wrapper can hang even when the evaluator boundary itself is correct.

### Recommended Timeout Model

Use a wrapper-local timeout policy with at least:

1. a default timeout
2. an override mechanism for known slow evaluation classes
3. a separate timeout classification in your own product model

Treat timeout as a wrapper/process-level outcome, not as a fabricated evaluator JSON result.

If the process times out and no valid evaluator JSON was captured, that is not the same thing as:

- completed `inconclusive`
- blocked `inconclusive`
- evaluator `message_error`

It is a wrapper-side execution failure condition.

### Good Timeout Behavior

When timeout occurs, your wrapper should usually:

1. stop the subprocess
2. record that timeout occurred
3. retain request context
4. retain any partial stdout/stderr if useful
5. classify the run as contract-unavailable or timed-out at the wrapper level

## Request Artifact Retention

Your wrapper should make an explicit retention choice for evaluator requests.

### Recommended Minimum

Retain the exact serialized request packet for any run that includes:

- blocked results
- completed `inconclusive`
- evaluator `message_error`
- timeout
- stdout parse failure

### Why Retention Matters

Without the exact packet, it can be difficult to prove:

- which `evaluations` were sent
- whether the test path was correct
- whether the wrong evidence file was used
- whether replay matches the original run

### Retention Patterns

Reasonable patterns:

1. retain every full outer request packet
2. retain only unusual or diagnosable cases
3. retain a stable canonical serialization plus an external object-store pointer

For early production systems, my recommendation is:

- retain all request packets at first if volume allows
- reduce later only when you have evidence that the storage cost is not justified

This is intentionally stronger than the minimum baseline described in [request-and-invocation.md](request-and-invocation.md).

That earlier page describes the minimum retention floor for unusual outcomes.

This page gives the preferred production starting point when your system can afford broader retention.

## Response Artifact Retention

At minimum, a production wrapper should strongly consider retaining:

- parsed stdout JSON
- raw stdout
- stderr
- process exit status
- timeout flag
- wrapper correlation id
- request artifact or pointer to it

This is especially important for:

- blocked invocations
- completed `inconclusive`
- evaluator `message_error`
- wrapper-side process failures

## Logging And Observability

Good logging should preserve the boundary between:

- wrapper-owned operational events
- evaluator-owned operational messages
- test-owned completed reasoning

### Recommended Log Fields

Your wrapper should strongly consider logging:

- wrapper run id
- evidence path
- requested test paths
- request transport used
- subprocess start time
- subprocess end time
- duration
- exit status
- timeout status
- parse-success or parse-failure status
- summary counts when JSON parsing succeeds
- whether evaluator `message_error` was present

### What To Avoid

Avoid logs that reduce everything to one line such as:

- “evaluation failed”
- “evaluation succeeded”

Those logs are too lossy for operational diagnosis.

## Wrapper-Side Failure Classification

Your software should have its own bounded classification model around the evaluator.

Recommended first-pass categories:

### 1. Invocation Failure

Meaning:

- the subprocess could not be launched at all

Examples:

- executable missing
- permission issue
- environment issue

### 2. Timeout

Meaning:

- the subprocess did not complete within the wrapper’s allowed time

### 3. Contract Unavailable

Meaning:

- the subprocess ended, but your wrapper could not obtain valid evaluator JSON

Examples:

- empty stdout
- malformed stdout
- wrapper-side decode failure

### 4. Evaluator Contract Available With Operational Errors

Meaning:

- valid evaluator JSON exists
- evaluator messages include error-level operational context

This still needs row-by-row interpretation.

### 5. Completed Results Available

Meaning:

- valid evaluator JSON exists
- one or more result rows were successfully returned

This category can coexist with:

- evaluator warnings
- evaluator errors
- blocked rows

That is why wrapper classification should be layered rather than single-valued.

## Separation Of Concerns In Your Wrapper

A hardened wrapper should usually keep these responsibilities separate:

1. request construction
2. subprocess execution
3. stdout parsing
4. evaluator-contract classification
5. product-specific business mapping
6. persistence/logging

This separation reduces several common problems:

- one giant function that mixes process mechanics and product logic
- accidental loss of raw diagnostic data
- difficulty replaying or unit testing individual failure modes

## Change Control And Version Awareness

Your wrapper should treat evaluator contract changes as real integration events.

At minimum, you should know:

- which evaluator version your wrapper was tested against
- which request/result semantics your wrapper assumes
- whether your wrapper depends on fields such as:
  - `affected_tests`
  - `stack_trace`
  - request-scoped versus test-scoped message `scope`

### Recommended Practice

When you upgrade evaluator versions:

1. rerun wrapper integration tests
2. verify the request and response docs still match your assumptions
3. verify summary/message semantics specifically
4. verify any UI or downstream reporting that depends on `inconclusive` interpretation

## Recommended Operational Defaults

If you need a conservative starting point, I recommend:

1. use full outer request packets
2. transport with `--request-file`
3. execute subprocesses without a shell
4. set explicit timeouts
5. retain request/response artifacts for unusual outcomes
6. log wrapper correlation ids and evaluator summary counts
7. restrict test-file selection to approved locations or manifests
8. keep evaluator messages and test reasoning separate in your own data model

## Common Hardening Mistakes

### Mistake 1: Treating Test Paths As User Data Without Governance

Problem:

- arbitrary trusted-code execution risk

Better:

- constrain and audit test selection

### Mistake 2: Treating Timeout As Evaluator `Inconclusive`

Problem:

- wrapper process failure is misreported as evaluator result meaning

Better:

- classify timeout separately at the wrapper layer

### Mistake 3: Retaining Only Final Boolean Outcome

Problem:

- no replay or diagnosis path

Better:

- retain request and response artifacts for unusual cases

### Mistake 4: Logging Only Summary Counts

Problem:

- row-level and message-level explanation is lost

Better:

- log summary as aggregate context, but preserve the full contract or a durable pointer to it

### Mistake 5: Mixing Wrapper Errors Into Evaluator Messages

Problem:

- downstream consumers cannot tell whether the evaluator said something or the wrapper invented it

Better:

- keep wrapper diagnostics in wrapper-owned fields or logs
- keep evaluator JSON intact as evaluator-owned output

## What The Worked Examples Should Demonstrate

The worked examples that follow should show:

- one minimal wrapper flow
- one more defensive wrapper flow
- how timeout, request retention, and response classification fit together

That is the next best place to turn these hardening rules into concrete integration patterns.
