# Plan 02: Expectation Binding And CLI Transport

## Goal

Define and document how caller-supplied comparison/configuration input should be transported into requested test executions, while preserving explicit ownership and safe failure behavior.

## Naming Note

Current committed code and some current docs still use `test_parameters`.

Current selected V2 proposal direction prefers `evaluations`, `subject`, and `criteria`.

This plan must be explicit about whether a statement refers to:

- the current implemented contract
- the proposed V2 terminology

## Baseline

Read first:

1. `docs/product/current-evaluator-reference.md`
2. `docs/product/test-parameter-exploration.md`
3. `docs/reference/evaluator-contract.md`
4. `docs/user/cli-reference.md`

## Current State

Current committed behavior:

- test call boundary is `evaluate(evidence, test_parameters, metadata)`
- direct CLI support uses repeated `--test-parameters-file`
- parameter files are matched to repeated `--test` arguments by position
- if parameter files are used, one must currently be supplied for every `--test`
- parameter transport/setup failures block only the affected invocation when possible

Selected V2 CLI direction:

- direct CLI should move away from positional `--test` + `--test-parameters-file` binding
- support `--invoke` for non-file usage
- support `--invoke-file` for file usage
- support `--request-file` for full-request file or stdin usage
- each repeated `--invoke` or `--invoke-file` represents exactly one requested test invocation
- each invocation payload must contain both:
  - `test`
  - `evaluations`

## Scope

In scope:

- direct CLI binding models
- parameter/evaluation transport behavior
- ownership boundaries between evaluator and test
- evaluator-side versus test-side failure handling
- documentation of explicit calling patterns

Out of scope:

- network-based parameter resolution
- hidden type coercion
- claim semantics
- unrelated result-packet redesign beyond what is needed to stay aligned with Plan 01

## Work Plan

1. Preserve the current three-argument test boundary.
   Do not reopen the basic signature unless a deliberate product decision says otherwise.

2. Decide the direct CLI binding model.
   The selected direct V2 direction is one repeated invocation packet per test rather than positional binding or split per-test flag blocks.

3. Keep ownership explicit.
   Caller-owned comparison input should stay separate from evaluator-owned metadata.

4. Keep failure ownership explicit.
   Evaluator-side transport/setup failures should remain distinct from test-owned returned errors.

5. Clarify documentation language.
   Make current versus proposed terminology visible so readers do not confuse implemented `test_parameters` with selected V2 `evaluations` / `criteria`.

6. Feed approved outcomes back into permanent docs.
   Update CLI, contract, authoring, and product docs once decisions are stable.

## Selected CLI Direction

### Core Shape

The selected V2 direct CLI shape is:

- support `--invoke` for non-file usage
- support `--invoke-file` for file usage
- support `--request-file` for programmatic or full-request usage
- each one represents exactly one test invocation
- each invocation contains both `test` and `evaluations`

This replaces the earlier direction of:

- repeated `--test`
- separate following `--evaluations-*` style flags
- positional file matching across repeated `--test`

### Rationale

- it keeps test-path ownership and caller-owned `evaluations` in one bounded invocation packet
- it removes positional ambiguity
- it maps cleanly into the selected `EvaluateEvidenceRequest.builder().raw_tests(...)` direction
- it supports both human-driven and automation-driven CLI usage without forcing files
- it keeps the V2 cutover explicit instead of dragging forward the older positional transport contract
- it provides a cleaner process-to-process entrypoint for Rust and other non-human callers without forcing shell-escaped inline JSON or temporary files

### Recommended Invocation Shapes

Non-file usage:

```bash
nape-eval \
  --evidence ./evidence.json \
  --invoke '{"test":"./coverage_check.py","evaluations":[{"subject":{"name":"coverage","data_type":"number"},"criteria":{"minimum":80}}]}' \
  --invoke '{"test":"./status_check.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

File usage:

```bash
nape-eval \
  --evidence ./evidence.json \
  --invoke-file ./coverage.invoke.json \
  --invoke-file ./status.invoke.json
```

Programmatic stdin usage:

```bash
cat request.json | nape-eval --request-file -
```

Full-request file usage:

```bash
nape-eval --request-file ./request.json
```

Recommended invocation-file shape:

```json
{
  "test": "./coverage_check.py",
  "evaluations": [
    {
      "subject": {
        "name": "coverage",
        "data_type": "number"
      },
      "criteria": {
        "minimum": 80
      }
    }
  ]
}
```

Recommended stdin request shape:

```json
{
  "evidence": "./evidence.json",
  "tests": [
    {
      "test": "./coverage_check.py",
      "evaluations": [
        {
          "subject": {
            "name": "coverage",
            "data_type": "number"
          },
          "criteria": {
            "minimum": 80
          }
        }
      ]
    }
  ]
}
```

### Invariants

- `--evidence` remains a shared top-level input for the whole CLI run
- each repeated `--invoke` value must decode as one invocation object
- each repeated `--invoke-file` must decode as one invocation object
- `--request-file` must decode as one full outer CLI request packet
- the full outer request packet should use top-level `tests` for the repeated requested test array
- each invocation object must contain:
  - `test`
  - `evaluations`
- `--invoke` and `--invoke-file` may be repeated in the same run
- each repeated invocation contributes one raw test item into `EvaluateEvidenceRequest.builder().raw_tests(...)`
- direct CLI should not require a separate `--test` argument once the V2 invocation-packet shape is adopted
- `--request-file` should carry the shared evidence locator plus the full invocation list in one packet
- `--request-file -` means read that full outer request packet from stdin
- direct invocation flags and full-request transport should be mutually exclusive in the same run

### Parsing Direction

The CLI adapter should:

- parse `--evidence`
- collect repeated `--invoke` JSON strings
- collect repeated `--invoke-file` JSON files
- optionally read one full request packet from a path or stdin when `--request-file` is used
- decode each one into a raw invocation object
- pass the combined raw invocation list into `EvaluateEvidenceRequest.builder()` for direct-flag mode
- pass the decoded full request packet into `EvaluateEvidenceRequest.builder()` for full-request mode

The CLI adapter should not:

- own V2 semantic validation for `subject`, `criteria`, or compatibility rules
- spread one invocation across multiple separate CLI flags
- preserve positional matching as the V2 contract shape

### Why Not The Earlier Split-Flag Model

The earlier model of:

- `--test`
- then `--evaluations-json` or `--evaluations-file`
- then another `--test`

is workable, but weaker than the selected direction because:

- it still requires a scoped parsing model
- it spreads one invocation across multiple arguments
- it keeps more parser state alive in the CLI adapter
- it is less direct for mapping into a builder that expects complete raw invocation packets

## Programmatic Caller Direction

For programmatic callers such as a Rust application, the selected direction is:

- support `--request-file`
- read a full outer request packet from a file path or from stdin when the value is `-`
- prefer this over custom binary transport for the first V2 CLI cut

Rationale:

- avoids shell-escaping complexity for nested JSON
- avoids command-length limits
- avoids forcing temporary files
- stays easy to inspect and debug
- maps cleanly into the builder-only `EvaluateEvidenceRequest` seam

Custom binary transport such as MessagePack or CBOR is a possible later extension, but it is not the recommended first V2 programmatic interface.

## Open Questions

- Should one-at-a-time micro-flags ever be supported later, or should V2 stay packet-based only?
  Answer:
  V2 should stay packet-based only.

## Selected Packet-Only Direction

V2 CLI transport should remain packet-based only.

That means the supported V2 caller-owned input forms are:

- `--invoke`
- `--invoke-file`
- `--request-file`

It should not add a second micro-flag input language such as:

- `--subject-name`
- `--subject-type`
- `--criteria-minimum`
- `--criteria-equals`

Rationale:

- packet-based input matches the selected builder-only `EvaluateEvidenceRequest` seam
- one invocation packet maps directly into one raw invocation object for request construction
- it avoids maintaining two parallel caller-input languages for the same contract
- it keeps nested `evaluations` / `subject` / `criteria` structure explicit
- it scales better to multi-subject and richer criteria shapes
- it avoids growing a larger CLI parser state machine for partial or scoped flag fragments
- it keeps validation and error reporting centered on one bounded input packet shape
- it reduces ambiguity around how fragmented flags combine into one invocation

## Done Criteria

This plan is ready to close when:

- a binding model is chosen and recorded
- the selected `--invoke` / `--invoke-file` model is documented clearly
- the packet-only direction is recorded clearly
- failure ownership is documented clearly
- current versus proposed terminology is explained clearly
- permanent user/reference/product docs reflect the approved direction
