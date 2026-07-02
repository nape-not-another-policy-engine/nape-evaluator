# Software Integration Guide

This guide set is for software authors who want to wrap `nape-evaluator` as one component inside a larger application, workflow, service, or orchestration layer.

Use this guide when your software needs to:

- construct evaluator request packets
- invoke `nape-eval` correctly
- parse evaluator JSON output
- distinguish test conclusions from evaluator operational problems
- harden wrapper behavior for production use

Do not use this guide as the primary source for:

- writing Python test-of-detail files
- changing evaluator implementation internals
- learning the CLI flags for casual one-off manual use

Use these docs instead when that is your goal:

- [CLI reference](../cli-reference.md)
- [Test-of-detail authoring](../test-of-detail-authoring.md)
- [V2 test authoring](../v2-test-authoring/README.md)
- [Evaluator contract](../../reference/evaluator-contract.md)

## Current Supported Integration Position

The current supported integration surface is the evaluator process boundary.

That means the stable machine-readable integration model today is:

1. your software constructs request packets
2. your software invokes `nape-eval`
3. the evaluator validates and executes the request
4. your software parses the evaluator JSON output

This guide intentionally treats the evaluator as a subprocess-style component.

It does not assume that importing internal Python modules from `src/nape_evaluator/...` is the preferred or stable downstream integration surface for other software.

## What Your Wrapper Owns

Your software is responsible for:

- deciding which evidence file to evaluate
- deciding which test file or files to invoke
- constructing valid `evaluations` input
- choosing whether to use repeated `--invoke`, repeated `--invoke-file`, or one full `--request-file`
- launching the evaluator process
- capturing stdout, stderr, and exit status
- parsing stdout JSON when valid evaluator output is produced
- deciding what your own software should do with:
  - `true`
  - `false`
  - `inconclusive`
  - evaluator messages
  - blocked executions

The evaluator is responsible for:

- validating the request structure
- loading and classifying the evidence
- building evaluator metadata
- loading and executing each Python test-of-detail
- returning per-test results
- returning evaluator-owned messages and summary information

Each Python test-of-detail is responsible for:

- extracting facts from loaded evidence
- applying comparison logic against caller-owned `evaluations`
- returning completed-test reasoning in `result.reason`

## Start Here

If you are new to integrating the evaluator, read in this order:

1. [Integration model](integration-model.md)
2. [Request and invocation](request-and-invocation.md)
3. [Response handling](response-handling.md)
4. [Production hardening](production-hardening.md)
5. [Worked examples](worked-examples.md)

## Reading Paths By Need

If you need the fastest path to a working wrapper:

1. [Integration model](integration-model.md)
2. [Request and invocation](request-and-invocation.md)
3. [Response handling](response-handling.md)
4. [Worked examples](worked-examples.md)

If you already know how to launch a subprocess and mainly need output interpretation guidance:

1. [Response handling](response-handling.md)
2. [Production hardening](production-hardening.md)

If you are designing a more production-grade integration layer:

1. [Integration model](integration-model.md)
2. [Request and invocation](request-and-invocation.md)
3. [Response handling](response-handling.md)
4. [Production hardening](production-hardening.md)

## Guide Map

### [Integration model](integration-model.md)

Explains what the evaluator is and is not as a component.

This page defines:

- the current supported boundary
- the trust model
- the ownership split between caller, evaluator, and test-of-detail
- the assumptions your wrapper should and should not make

### [Request and invocation](request-and-invocation.md)

Explains how your software should construct request packets and invoke the evaluator process.

This page covers:

- direct invocation packets
- full outer request packets
- when to choose each CLI transport
- stdout, stderr, and exit-status expectations

### [Response handling](response-handling.md)

Explains how your software should parse and interpret the evaluator response.

This page covers:

- `results[*]`
- `execution`
- `result`
- `evaluator.messages`
- `evaluator.summary`
- blocked execution versus completed `inconclusive`

### [Production hardening](production-hardening.md)

Explains how to make a wrapper safer and more diagnosable in real use.

This page covers:

- timeout strategy
- request artifact retention
- logging and traceability
- trust boundaries around Python test files
- wrapper-side failure classification

### [Worked examples](worked-examples.md)

Shows concrete end-to-end wrapper examples.

This page covers:

- one minimal wrapper flow
- one more defensive production-style flow
- example request packets and example output interpretation

## Core Integration Rules

If you only remember a few rules from this guide, remember these:

1. treat the evaluator as a subprocess-style component unless the product docs explicitly say otherwise
2. treat stdout JSON as the primary machine-readable result surface
3. do not collapse evaluator operational messages into test reasoning
4. do not assume `inconclusive` always means the same thing
5. distinguish:
   - completed `inconclusive`
   - blocked `inconclusive`
   - evaluator `message_error`
6. keep the caller-owned request packet explicit and reproducible
7. treat Python test files as trusted executable code, not as inert configuration

## Relationship To Other Docs

This guide does not replace the contract reference.

Use:

- [current-evaluator-reference.md](../../product/current-evaluator-reference.md)
- [evaluator-contract.md](../../reference/evaluator-contract.md)

when you need the exact current committed boundary.

This guide exists to make that boundary easier for software integrators to use correctly.
