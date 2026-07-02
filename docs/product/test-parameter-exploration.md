# Test Parameter Exploration

## Superseded Status

This document is retained as historical exploration only.

It does not describe the selected or current V2 evaluator contract.

Use these docs for the selected/current direction instead:

- `docs/product/v2-structured-verification-input-proposal.md`
- `docs/product/v2-structured-verification-result-proposal.md`
- `docs/product/current-evaluator-reference.md`

The selected and implemented V2 model now uses:

- `evaluate(evidence, evaluations, metadata)`
- caller-owned `evaluations[*].subject` plus `criteria`
- packet-based CLI/request transport through `--invoke`, `--invoke-file`, and `--request-file`

This document explores a possible V2 feature for passing caller-supplied test parameters into a test-of-detail.

It is exploratory input, not a final contract.

## Purpose

Use this document to:

- show concrete examples of how caller-supplied comparison inputs could look
- separate evaluator-owned metadata from caller-owned test parameters
- surface typing and defensive-behavior questions before implementation

## Input Example

One external example under consideration looks like this:

```yaml
activity:
  - name: app-testing
    short: "Application Testing"
    description: "This activity verifies that all of the proper testing control were either passed, or met the minimum expected criteria."
    action:
      - name: code-cover-80
        short: "Code Coverage > 80%"
        description: "Unit Test Coverage must be at least 80%"
        test: "activity/app-testing/code_cover_80.py"
        testParameters:
          minCoverage: 80
        evidence: "evidence/app-testing/sonar_metrics.json"
```

This is useful exploratory input from a customer. It is not yet the evaluator contract.

## Design Constraints

Any final design should preserve these rules:

- evaluator-owned metadata remains distinct from caller-owned test parameters
- the evaluator should not silently mutate caller intent
- type handling should be explicit, predictable, and reviewable
- failures should be clear to the calling user without relying on Python tracebacks
- test-of-detail execution should remain deterministic and process-local

## Historical Explored Contract Direction

At the time of this exploration, the strongest direction under consideration was:

```python
def evaluate(evidence, test_parameters, metadata):
    ...
```

Why this is the current recommendation:

- `evidence` is the loaded subject being evaluated
- `test_parameters` is caller-owned comparison/configuration input
- `metadata` is evaluator-owned execution context

That separation is clearer than:

- replacing `metadata` with `test_parameters`
- hiding `test_parameters` inside `metadata`

## Candidate Shapes

### Option 1: Replace metadata

```python
def evaluate(evidence, test_parameters):
    ...
```

Assessment:

- not recommended

Why:

- drops evaluator-owned metadata from the contract
- forces evidence-type and schema checks somewhere else
- makes future evaluator-owned execution context harder to extend cleanly

### Option 2: Hide parameters inside metadata

```python
def evaluate(evidence, metadata):
    test_parameters = metadata.get("test_parameters", {})
```

Assessment:

- possible, but not preferred

Why:

- mixes evaluator-owned and caller-owned concerns
- makes it easier for tests to treat all metadata as equally trustworthy or equally user-supplied
- weakens failure clarity when the wrong side of the contract is malformed

### Option 3: Separate explicit argument

```python
def evaluate(evidence, test_parameters, metadata):
    ...
```

Assessment:

- recommended

Why:

- separates concerns cleanly
- keeps caller-owned comparison inputs adjacent to the evidence being evaluated
- makes validation ownership clearer
- keeps future extension paths explicit

## Parameter Type Direction

The safest starting point is to treat `test_parameters` as a JSON-compatible mapping:

```python
{
    "minCoverage": 80,
    "allowedStatuses": ["complete", "approved"],
    "requireBranchCoverage": True,
    "owner": None,
}
```

Recommended allowed value classes:

- string
- integer
- float
- boolean
- null
- list of JSON-compatible values
- object/map of JSON-compatible values

Recommended first rule:

- pass parameters as plain Python dict/list/scalar values
- do not auto-wrap them into dynamic attribute objects

That means this style is preferred:

```python
def evaluate(evidence, test_parameters, metadata):
    min_coverage = test_parameters.get("minCoverage")
```

This style should not be the primary contract:

```python
def evaluate(evidence, test_parameters, metadata):
    min_coverage = test_parameters.minCoverage
```

Why:

- dict access is explicit
- missing-key handling is clearer
- attribute-style objects introduce ambiguity around defaults, mutation, and missing-field behavior

## Example: Numeric Threshold

Caller-owned parameters:

```json
{
  "minCoverage": 80
}
```

Recommended test shape:

```python
def evaluate(evidence, test_parameters, metadata):
    if metadata.get("evidence_type") != "json":
        return "error", "This test expects JSON evidence."

    min_coverage = test_parameters.get("minCoverage")
    if not isinstance(min_coverage, (int, float)):
        return "error", "This test requires numeric test parameter 'minCoverage'."

    measures = evidence.get("component", {}).get("measures", [])
    coverage_value = None
    for measure in measures:
        if measure.get("metric") == "coverage":
            coverage_value = float(measure.get("value", 0))
            break

    if coverage_value is None:
        return "inconclusive", "The 'coverage' metric is missing from the evidence."

    if coverage_value >= min_coverage:
        return "pass", f"Coverage is {coverage_value}%, which meets the required {min_coverage}%."
    return "fail", f"Coverage is {coverage_value}%, which is below the required {min_coverage}%."
```

## Example: Enumerated Allowed Values

Caller-owned parameters:

```json
{
  "allowedStatuses": ["complete", "approved"]
}
```

Recommended test shape:

```python
def evaluate(evidence, test_parameters, metadata):
    allowed_statuses = test_parameters.get("allowedStatuses")
    if not isinstance(allowed_statuses, list) or not all(isinstance(v, str) for v in allowed_statuses):
        return "error", "This test requires string-list test parameter 'allowedStatuses'."

    status = evidence.get("status")
    if status in allowed_statuses:
        return "pass", f"Status '{status}' is allowed."
    return "fail", f"Status '{status}' is not in the allowed status list."
```

## Example: Nested Object Parameters

Caller-owned parameters:

```json
{
  "coveragePolicy": {
    "minLineCoverage": 80,
    "minBranchCoverage": 70
  }
}
```

Recommended test shape:

```python
def evaluate(evidence, test_parameters, metadata):
    coverage_policy = test_parameters.get("coveragePolicy")
    if not isinstance(coverage_policy, dict):
        return "error", "This test requires object test parameter 'coveragePolicy'."

    min_line = coverage_policy.get("minLineCoverage")
    min_branch = coverage_policy.get("minBranchCoverage")
    if not isinstance(min_line, (int, float)) or not isinstance(min_branch, (int, float)):
        return "error", "Coverage policy thresholds must be numeric."

    return "inconclusive", "Example only: coverage policy comparison not fully implemented here."
```

## Defensive Behavior Direction

Recommended first-pass ownership split:

- evaluator validates that the overall parameter payload is structurally passable
- the test-of-detail validates whether the specific parameters it needs are present and of the expected type

Recommended contract meaning:

- evaluator-side parameter transport failure:
  - evaluator message
  - blocked result item with `executed == false` if the test cannot be called safely
- test-level parameter mismatch:
  - returned `error`
  - test still counts as `ran`

Examples of evaluator-side failures:

- parameter payload cannot be decoded
- repeated test inputs cannot be matched to their parameter payloads
- parameter envelope is not a supported JSON-compatible structure

Examples of test-level failures:

- missing `minCoverage`
- `minCoverage` is `"80"` instead of numeric `80`, if coercion is not allowed
- `allowedStatuses` is not a list of strings

## CLI Binding Options

The current implemented direct-CLI shape is positional file binding:

```bash
nape-eval \
  --evidence ./service_report.json \
  --test ./status_check.py \
  --test-parameters-file ./status_check.parameters.json \
  --test ./coverage_check.py \
  --test-parameters-file ./coverage_check.parameters.json
```

Current implementation meaning:

- parameter files are matched to tests by position
- if any `--test-parameters-file` is used, one must currently be supplied for every `--test`
- the evaluator loads each parameter file as a top-level JSON object

Assessment:

- acceptable as an initial machine-usable shape
- weaker than desired for human readability because the parameter ownership is implied by order rather than syntax

### Option A: Keep Positional File Binding

Example:

```bash
nape-eval \
  --evidence ./service_report.json \
  --test ./status_check.py \
  --test-parameters-file ./status_check.parameters.json \
  --test ./coverage_check.py \
  --test-parameters-file ./coverage_check.parameters.json
```

Assessment:

- workable
- not preferred as the long-term human-facing CLI

Why:

- shortest migration from the current implementation
- weakest deductive signal that the parameters belong to the immediately preceding test
- fragile if users reorder or edit long commands

### Option B: Current-Test Scoped File Binding

Example:

```bash
nape-eval \
  --evidence ./service_report.json \
  --test ./status_check.py \
  --test-parameters-file ./status_check.parameters.json \
  --test ./coverage_check.py \
  --test-parameters-file ./coverage_check.parameters.json
```

Proposed meaning:

- each `--test` opens a new test invocation block
- following `--test-parameters-file` entries belong to the current test until the next `--test`
- the parser should reject `--test-parameters-file` before any `--test`

Assessment:

- strong candidate

Why:

- same surface syntax as today, but with better explicit contract meaning
- more naturally deductible that the file belongs to the current test
- still easy for automation

### Option C: Current-Test Scoped Inline Parameters

Example:

```bash
nape-eval \
  --evidence ./service_report.json \
  --test ./status_check.py \
  --test-parameter allowedStatuses='["complete","approved"]' \
  --test ./coverage_check.py \
  --test-parameter minCoverage=80
```

Proposed meaning:

- each `--test` opens a new test invocation block
- repeated `--test-parameter key=<json-value>` entries belong to the current test
- values are parsed as JSON-compatible scalar/list/object values

Assessment:

- strongest direct-CLI candidate for one-at-a-time parameter entry

Why:

- very clear that parameters belong to the current test
- no intermediate file required for simple ad hoc runs
- still supports explicit typing if the right-hand side is parsed as JSON

Tradeoffs:

- parser must track current invocation state
- quoting becomes more complex for lists, objects, and strings with spaces

### Option D: Current-Test Scoped Inline Full Object

Example:

```bash
nape-eval \
  --evidence ./service_report.json \
  --test ./coverage_check.py \
  --test-parameters-json '{"minCoverage":80}'
```

Assessment:

- plausible
- better for automation than for hand-authored commands

Why:

- keeps object shape explicit
- avoids repeated key parsing logic
- shell quoting becomes awkward quickly

### Option E: Explicit Labeled Binding

Example:

```bash
nape-eval \
  --evidence ./service_report.json \
  --test status=./status_check.py \
  --test-parameter status:allowedStatuses='["complete","approved"]' \
  --test coverage=./coverage_check.py \
  --test-parameter coverage:minCoverage=80
```

Assessment:

- most explicit
- likely too heavy for the first ergonomic improvement

Why:

- strongest possible ownership signal
- useful if the same test file is invoked multiple times with different parameter sets
- noisier and harder for non-technical users to author correctly

### Option F: Manifest-Oriented Binding

Example:

```yaml
tests:
  - test: ./status_check.py
    testParameters:
      allowedStatuses: ["complete", "approved"]
  - test: ./coverage_check.py
    testParameters:
      minCoverage: 80
```

Assessment:

- best for larger batches
- not the best answer to the one-parameter-at-a-time CLI question

Why:

- scales better than long repeated flag sequences
- easiest to review in version control
- less useful for fast local experimentation

## Current Recommendation For Future CLI Ergonomics

If the evaluator keeps direct CLI parameter support, the strongest next-step direction is:

- treat each `--test` as opening a test invocation block
- allow `--test-parameter key=<json-value>` to repeat under the current test
- keep `--test-parameters-file <file>` as an alternative under the current test
- reject parameter flags that appear before any `--test`
- reject mixing inline parameters and parameter-file input for the same test in the first pass

This would preserve the current domain model while making parameter ownership more deductible to the user.

## Key Open Questions

The major unresolved questions are:

1. Should the evaluator accept parameters only from NAPE CLI orchestration, or also from direct CLI users?
2. Should `test_parameters` always be a dict, even when empty?
3. Should the evaluator reject unsupported parameter types before calling the test?
4. Should the evaluator do any scalar coercion, or require exact caller-provided types?
5. What message/result codes should distinguish evaluator transport failure from test-level parameter mismatch?
6. Should direct CLI binding remain positional, or move to current-test scoped binding before more parameter features are added?

## Historical Recommendation Snapshot

At the time of this exploration, the strongest direction under consideration was:

- keep `metadata` as evaluator-owned context
- add `test_parameters` as a separate third argument
- treat `test_parameters` as a plain JSON-compatible dict
- avoid implicit type coercion
- report parameter transport problems as evaluator messages
- report test-specific parameter mismatch as returned `error`
