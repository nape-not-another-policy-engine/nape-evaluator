# Request And Invocation

This page explains how software should build evaluator request packets and invoke the evaluator process correctly.

Read this page after [integration-model.md](integration-model.md).

The goal here is not just to show valid flag combinations.

The goal is to help an integrator answer these questions clearly:

- what exact JSON shape should my software build
- which invocation transport should my software choose
- how should my software launch `nape-eval`
- what should my software treat as primary success/failure signals
- what request artifacts should my software retain for diagnosis and traceability

## The Integration Problem This Page Solves

At the process boundary, the evaluator accepts:

- one evidence path
- one or more requested test invocation packets
- one selected CLI transport for supplying those packets

Many wrappers fail here by mixing:

- caller-owned packet construction
- shell argument formatting
- request persistence strategy
- output parsing assumptions

into one unstructured subprocess call.

This page gives a cleaner model.

## The Three Request Transport Shapes

The current evaluator supports three practical ways to supply request input.

### 1. Repeated `--invoke`

Shape:

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke '{"test":"./verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

Meaning:

- `--evidence` supplies the one outer evidence path
- each `--invoke` value is one requested test packet

Use this when:

- your wrapper already has request content in memory
- the packet is small enough that command-line JSON remains manageable
- you do not need file-based request artifacts as the primary transport

Avoid this when:

- packets are large
- you want deterministic retained request files
- shell escaping or process argument escaping would become error-prone

### 2. Repeated `--invoke-file`

Shape:

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke-file ./invoke-a.json \
  --invoke-file ./invoke-b.json
```

Meaning:

- `--evidence` still supplies the one outer evidence path
- each `--invoke-file` points to one JSON file containing one requested test packet

Use this when:

- your wrapper wants one file per requested test invocation
- you want simpler subprocess argument strings
- you want retained per-invocation artifacts for debugging or auditability

Avoid this when:

- your wrapper would need to create many temporary files for very short-lived simple requests and that extra file management gives no value

### 3. One Full `--request-file`

Shape:

```bash
nape-eval --request-file ./request.json
```

or:

```bash
cat request.json | nape-eval --request-file -
```

Meaning:

- your wrapper supplies one full outer request packet
- that packet includes both:
  - `evidence`
  - `tests`

Use this when:

- your wrapper already models the whole evaluator request as one object
- you want the cleanest exact artifact of what was sent
- you want to avoid splitting outer and inner request concerns at the CLI layer
- your wrapper can conveniently write one file or stream one full packet to stdin

This is the cleanest current process-boundary transport for many production wrappers.

## Recommended Default Choice

If your software is building evaluator requests programmatically and is not constrained by a legacy CLI shape, my recommendation is:

1. prefer one full outer request packet
2. transport it with `--request-file`
3. use a real file path when request retention matters
4. use `--request-file -` with stdin when you want to avoid materializing a persistent request file

Rationale:

- it matches the full domain request most directly
- it reduces the chance that your wrapper will accidentally separate outer and inner request responsibilities incorrectly
- it gives you one reproducible packet artifact
- it tends to make logging and replay easier

My secondary recommendation is:

- use repeated `--invoke-file` when your wrapper naturally manages one test invocation at a time but still wants file-backed artifacts

My least-preferred production default is:

- large or deeply nested inline `--invoke` JSON, because escaping, logging, and replay usually become less clear

## Exact Request Shapes

### Single Requested Test Packet

One direct invocation packet looks like this:

```json
{
  "test": "./verify_author_complete.py",
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
  ]
}
```

This packet represents exactly one requested test invocation.

It contains:

- `test`
- `evaluations`

It does not contain:

- `evidence`

That is why `--invoke` and `--invoke-file` still require a separate `--evidence` argument.

### Full Outer Request Packet

One full request packet looks like this:

```json
{
  "evidence": "./author_verification.json",
  "tests": [
    {
      "test": "./verify_author_complete.py",
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
      ]
    }
  ]
}
```

This packet represents the full caller-owned request.

It contains:

- the one evidence path
- all requested test invocation packets

## How Your Wrapper Should Build Requests

Your wrapper should usually model request construction in two layers.

### Layer 1: Wrapper-Level Domain Model

Your own software should usually have its own internal representation for:

- evidence selection
- test selection
- evaluation input assembly
- run metadata that belongs to your product rather than to the evaluator

Example wrapper-local model:

- selected evidence artifact
- chosen evaluator test set
- wrapper run id
- product workflow state

Do not force all of your own application state into the evaluator request packet.

Only the evaluator-owned request shape should cross the evaluator boundary.

### Layer 2: Evaluator Request Rendering

Then your wrapper should render that local model into one of the supported evaluator packet shapes.

That render step should be explicit.

It should be easy to inspect:

- what your product decided
- what exact evaluator request packet was emitted

This is especially important when your wrapper later needs to answer:

- which criteria did we send
- which test file did we ask to run
- which evidence file did we point the evaluator at

## Request Validation Expectations

The evaluator validates request structure before use-case execution.

Your wrapper should still perform basic preflight validation before launching the subprocess.

Recommended wrapper-side validation:

- evidence path is present
- at least one test is requested
- each test path is present
- `evaluations` exists and is an array
- your own wrapper-local serialization produced valid JSON

Do not rely on wrapper-side validation alone.

The evaluator is still the authority for the actual boundary validation rules.

Current evaluator validation expectations include:

- `evidence` must be a non-empty string
- `tests` must be a non-empty array
- each test item must contain exactly:
  - `test`
  - `evaluations`
- each evaluation item must contain exactly:
  - `subject`
  - `criteria`
- `subject.name` must be lowercase snake_case ASCII, start with a letter, and end with an alphanumeric
- duplicate `subject.name` values are not allowed within one requested test packet
- `subject.data_type` must be one of the supported bounded values
- `criteria` must be structurally compatible with that `subject.data_type`
- no hidden type coercion is performed

## Choosing Between File And Stdin Request Delivery

### Use A Real File Path When

- you want replayable request artifacts
- you want easier operator debugging
- you want to preserve exactly what was sent
- your wrapper already writes working files for the surrounding workflow

### Use Stdin With `--request-file -` When

- you want to avoid a persistent request file
- your wrapper already has the full request packet in memory
- your process-execution environment handles stdin payloads cleanly

### Tradeoff Summary

Real file path:

- easier debugging
- easier replay
- easier external inspection
- more filesystem cleanup responsibility

Stdin:

- fewer persistent artifacts
- fewer temp files
- slightly harder manual replay unless your wrapper also logs or retains the serialized packet elsewhere

## Subprocess Invocation Rules

Your wrapper should treat `nape-eval` as a normal deterministic subprocess.

Recommended invocation responsibilities:

1. build the argument vector explicitly
2. avoid shell-string concatenation when your runtime offers direct argv execution
3. capture:
   - stdout
   - stderr
   - exit status
4. set an explicit timeout
5. retain or log enough request context to replay failures

Preferred behavior:

- execute without a shell when your language/runtime allows it
- pass arguments as structured argv items
- keep JSON serialization separate from process launching

Avoid:

- building one large shell command string when direct argv execution is available
- treating stderr text as the primary contract
- treating zero exit status as the only success condition you need to inspect

## Stdout, Stderr, And Exit Status

Your wrapper should use these signals differently.

### Stdout

Stdout is the primary machine-readable output surface.

When the evaluator successfully emits valid contract JSON, your wrapper should parse stdout and treat that JSON as the authoritative action result.

### Stderr

Stderr is useful supporting operational context.

Your wrapper may log stderr, retain it, or attach it to wrapper-local diagnostics.

But stderr is not the main evaluator action contract. For non-`--check-install` evaluator invocations, stdout JSON is the primary contract even when the request was malformed.

### Exit Status

Exit status is secondary to contract availability for evaluator invocations.

The current contract is:

- exact standalone `--check-install` returns plain text with exit status `0`
- every non-`--check-install` evaluator invocation returns exit status `0`
- non-`--check-install` invocations are expected to provide evaluator JSON on stdout, including malformed caller/request input

That means a good wrapper should usually decide in this order:

1. did I receive valid evaluator JSON
2. if yes, parse and classify that contract
3. if no, then classify this as a wrapper/process-level invocation failure using stderr and exit status

## Recommended Invocation Decision Order

A practical wrapper should usually classify the subprocess result in this order:

1. did the subprocess launch successfully at all
2. did it time out
3. did stdout contain valid evaluator JSON
4. if yes, parse and use the JSON contract
5. if no, use exit status and stderr as wrapper-level diagnostic input

This order matters because otherwise a wrapper may incorrectly mark a run as failed even when the evaluator intentionally returned a structured JSON contract containing blocked or inconclusive outcomes.

For the current evaluator, malformed invocation input belongs in step 4, not step 5, because it is returned as evaluator JSON rather than as a separate parser-only process failure.

## Request Artifact Strategy

Production wrappers should decide explicitly what request artifact policy they want.

Reasonable options:

### Option 1: Retain Every Full Request Packet

Best when:

- traceability matters highly
- replay matters highly
- evaluation volume is manageable

Tradeoff:

- more storage

### Option 2: Retain Only Failed Or Inconclusive Cases

Best when:

- full retention is expensive
- you mainly need artifacts for diagnosis

Tradeoff:

- less complete replay coverage

### Option 3: Retain No Request File, But Log A Stable Serialized Hash Or Snapshot

Best when:

- the surrounding system already has its own stronger request audit model

Tradeoff:

- replay may require reconstructing the packet from other sources

Minimum recommended baseline:

- retain the full request packet for any invocation that produces:
  - blocked results
  - completed `inconclusive`
  - evaluator `message_error`
  - timeout
  - stdout parse failure

Stronger production default:

- retain all request packets at first if volume allows
- reduce later only when you have evidence that the storage and retention cost is not justified by the diagnostic value

## Minimal Wrapper Flow

At minimum, a wrapper should do this:

1. build one full outer request object
2. serialize it to JSON
3. invoke `nape-eval --request-file <path-or->`
4. capture stdout, stderr, and exit status
5. parse stdout JSON if present and valid
6. pass the parsed contract to a separate response-classification step

## Common Wrapper Mistakes

### Mistake 1: Mixing Wrapper State Into The Evaluator Packet

Bad pattern:

- putting wrapper-local workflow state into the evaluator packet because it is convenient

Better pattern:

- keep wrapper-local orchestration state in your own model
- render only the evaluator contract fields into the evaluator request

### Mistake 2: Treating Inline CLI JSON As The Canonical Audit Artifact

Bad pattern:

- logging only the final shell command string

Better pattern:

- retain the structured JSON packet separately from the subprocess command itself

### Mistake 3: Using Exit Status As The Only Result Signal

Bad pattern:

- `exit == 0` means success, `exit != 0` means failure

Better pattern:

- parse stdout JSON when available
- use exit status and stderr only as supporting process-level diagnostics for evaluator invocations

### Mistake 4: Letting The Shell Own Escaping Logic

Bad pattern:

- one giant quoted command string with embedded JSON

Better pattern:

- structured argv
- explicit JSON serialization
- shell-free process launch when possible

## Relationship To The Next Pages

After this page:

- read [response-handling.md](response-handling.md) for how to interpret the returned contract
- read [production-hardening.md](production-hardening.md) for timeout, logging, and operational guidance
- use [worked-examples.md](worked-examples.md) once you want end-to-end wrapper examples
