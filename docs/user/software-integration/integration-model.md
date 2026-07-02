# Integration Model

This page defines what `nape-evaluator` is and is not when another software system wraps it as a component.

Read this page before designing subprocess commands, packet builders, or response parsers.

## Purpose

The goal of this page is to make the integration boundary explicit so downstream software does not accidentally depend on behavior that the evaluator does not currently promise.

This matters because the evaluator has several different layers of behavior:

- caller-owned request construction
- evaluator-owned orchestration
- test-owned comparison logic
- CLI/process transport

If those concerns get blurred, a wrapper can become brittle even when the evaluator itself is behaving correctly.

## What This Guide Means By “Integration”

In this guide, integration means:

- another application invokes `nape-evaluator`
- that application supplies evidence and requested tests
- that application consumes evaluator output programmatically

Examples:

- a Rust application that launches `nape-eval` as one step in a larger workflow
- a service that evaluates evidence artifacts and stores evaluator output
- a desktop or web application that lets a user choose evidence and tests, then displays results
- an orchestration layer that runs several test invocations and aggregates the resulting records

This guide is not about:

- authoring the Python test-of-detail files themselves
- changing evaluator internals
- using the CLI manually from a shell for one-off inspection

## Current Supported Boundary

Today, the evaluator should be treated as a process-boundary component.

That means the supported integration shape is:

1. your software constructs evaluator request input
2. your software invokes the `nape-eval` executable
3. the evaluator emits one JSON object to stdout
4. your software parses that JSON object and applies its own downstream behavior

Current supported request transports:

- repeated `--invoke <json-object>`
- repeated `--invoke-file <json-file>`
- one full `--request-file <path-or->`

Current supported response transport:

- one JSON object written to stdout

Current supported install check:

- `--check-install`

## What Is Stable Versus What Is Not

### Stable Enough To Build Against

These are the intended current integration surfaces:

- the CLI executable
- the request packet shapes documented in:
  - [CLI reference](../cli-reference.md)
  - [Evaluator contract](../../reference/evaluator-contract.md)
  - [Current evaluator reference](../../product/current-evaluator-reference.md)
- the JSON output envelope with:
  - `results`
  - `evaluator.messages`
  - `evaluator.summary`

### Not The Recommended Public Integration Surface

These should not be treated as the primary supported downstream integration API unless product docs explicitly change direction later:

- importing internal modules from `src/nape_evaluator/...`
- constructing internal request/response domain objects from another codebase by direct import
- depending on private helper-function behavior
- depending on test-driver implementation details rather than the documented process contract

This does not mean such imports are impossible.

It means your wrapper should not assume those internal seams are the stable public contract.

## Why The Process Boundary Is The Right Current Model

The current evaluator is designed around a bounded executable behavior:

- it validates caller-owned request structure
- it loads evidence from file paths
- it dynamically imports trusted Python test files
- it emits CLI-shaped JSON

That is already a coherent machine-readable component boundary.

By contrast, treating internal Python modules as the supported integration surface would create ambiguity around:

- which internal types are public
- which validation layer your software should trust
- whether internal object constructors are stable external APIs
- whether future refactors would be considered breaking for downstream callers

The process boundary avoids that ambiguity.

## Ownership Model

A wrapper around the evaluator should keep three ownership zones explicit.

### 1. Caller-Owned Concerns

Your software owns:

- choosing the evidence path
- choosing one or more test paths
- building each requested test packet
- deciding the `evaluations` content
- deciding which CLI transport to use
- managing subprocess invocation
- interpreting the returned JSON for your own product

Caller-owned data includes:

- evidence path
- test path
- `evaluations`
- any wrapper-local run identifier, logging metadata, persistence key, or orchestration context

### 2. Evaluator-Owned Concerns

The evaluator owns:

- validating request packet structure
- rejecting malformed request packets before execution
- loading evidence by extension
- producing evaluator metadata
- executing each requested test independently
- emitting evaluator messages
- building evaluator summary counts
- synthesizing blocked-result `inconclusive` records when execution cannot complete

Evaluator-owned output includes:

- `execution`
- blocked-result reasoning
- `evaluator.messages`
- `evaluator.summary`

### 3. Test-Owned Concerns

The Python test-of-detail owns:

- extracting facts from the loaded evidence object
- deciding which facts are needed
- deciding whether facts are found, not found, or invalid
- applying comparison logic against caller-owned `evaluations`
- returning completed-test `conclusion`, `facts`, and `reason`

Test-owned output exists only when the test completed.

That is why a wrapper must not assume that every `result.reason` has the same owner or meaning.

## Trust And Execution Model

The evaluator dynamically imports and executes Python test files.

That means a wrapper must treat those test files as trusted executable code.

This has several implications:

1. your software should not treat a test path as harmless configuration
2. your software should control which test files are allowed to run
3. your software should understand that evaluator execution is not a sandbox
4. your software should preserve traceability for which test file was run against which evidence file

If your software presents a user-facing experience, the UI or API boundary should not imply stronger isolation than the evaluator actually provides.

## The Basic Runtime Flow

At a high level, a well-behaved wrapper should understand the runtime in this order:

1. build the caller-owned request packet
2. choose one invocation transport
3. launch `nape-eval`
4. wait for process completion or timeout
5. capture stdout, stderr, and exit status
6. if valid evaluator JSON is available, parse it
7. classify each `results[*]` row
8. classify each evaluator message
9. decide what your software should do next

## The Most Important Distinctions To Preserve

Many integration mistakes come from collapsing distinct meanings into one “success/failure” bucket.

Your wrapper should preserve these distinctions:

### Completed Test Versus Blocked Invocation

Completed test:

- `execution.executed == true`
- `execution.status == "completed"`
- the Python test completed and returned a result record

Blocked invocation:

- `execution.executed == false`
- `execution.status == "blocked"`
- the Python test did not complete successfully as a runnable evaluation step
- the evaluator synthesized the blocked `inconclusive` result

### Test Reasoning Versus Evaluator Operational Context

Test reasoning:

- lives in `results[*].result.reason` when the test completed
- explains the completed evaluation conclusion

Evaluator operational context:

- lives in `evaluator.messages[*]`
- explains load failures, import failures, execution failures, warnings, and similar operational events

### Completed `Inconclusive` Versus Blocked `Inconclusive`

Completed `inconclusive`:

- the test completed
- the test concluded that it could not establish or evaluate what it needed

Blocked `inconclusive`:

- the test did not complete
- the evaluator created the `inconclusive` result because execution was blocked

These are not interchangeable.

A wrapper that only looks at `result.conclusion` and ignores `execution` will lose important meaning.

## Recommended First Wrapper Shape

For a first implementation, your software should usually have these internal responsibilities:

1. request-packet builder
2. evaluator-process invoker
3. stdout JSON parser
4. response classifier
5. wrapper-level result mapper

That usually means:

- one function or component builds the request
- one function or component launches `nape-eval`
- one function or component validates/parses stdout JSON
- one function or component translates evaluator output into your application’s own model

This split keeps your software from mixing:

- subprocess mechanics
- evaluator contract knowledge
- product-specific business behavior

into one large integration function.

## Good And Bad Assumptions

### Good Assumptions

- the evaluator output JSON is the primary machine-readable contract
- request validation happens before the evaluator use-case seam is crossed
- one outer result row exists per requested test invocation
- evaluator messages are evaluator-owned and separate from test reasoning

### Bad Assumptions

- “`inconclusive` always means the same thing”
- “every failure should be read from `result.reason`”
- “if the process exit status is zero, there were no evaluator problems”
- “if one test is blocked, all tests must have been blocked”
- “internal Python imports are the official public API because they work today”

## What The Next Pages Will Add

- [Request and invocation](request-and-invocation.md) will show how to build and submit requests correctly.
- [Response handling](response-handling.md) will show how to classify and consume output correctly.
- [Production hardening](production-hardening.md) will show how to make the wrapper safer and more diagnosable.
- [Worked examples](worked-examples.md) will show end-to-end wrapper flows using the current process contract.
