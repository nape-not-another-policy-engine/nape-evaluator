# Advanced Authoring Patterns

This page is for authors who already understand the V2 progression and now need to scale beyond simple one-subject, one-pattern tests.

It is not a replacement for the progression.

Start here only after you are comfortable with:

- [Authoring Progression](authoring-progression.md)
- [Authoring Examples Index](authoring-examples-index.md)
- [Scaffold Guide](scaffold.md)

## Purpose And Audience

Use this page when your test-of-detail is no longer just:

- one extracted fact
- one direct comparison
- one simple criterion

This page is meant for authors who need to handle things like:

- several facts in one decision
- typed and structural facts in the same test
- derived facts
- richer internal policy reasoning

The goal is to show how to scale complexity without:

- overloading caller-owned `evaluations`
- hiding business logic in vague helpers
- turning the evaluator transport into a policy DSL

## When You Actually Need This Page

You probably do not need this page yet if:

- one fact and one criterion still solve the problem
- your test is still mainly about proving the evidence shape
- you are still learning the basic result contract and fact model

You probably do need this page when one or more of these are true:

- one conclusion depends on several subjects
- one fact has to be parsed into a strong type before evaluation
- one fact is structural, such as an array or object
- you need to derive a fact instead of reading it directly
- the policy reasoning branches internally

If you are not sure, go back to:

- [Authoring Progression](authoring-progression.md)

## Advanced Complexity Dimensions

Advanced authoring usually grows along a small number of dimensions.

Treat them as separate dimensions on purpose.

That keeps the test understandable.

### 1. Fact Topology

Ask:

- do I need one fact or several facts?
- are those facts independent?
- does one fact depend on another?
- do I need a derived fact that is computed inside the test?

Useful distinction:

- independent facts:
  each fact can be established on its own
- dependent facts:
  one fact or one evaluation step depends on another already being valid
- derived facts:
  the test computes a new fact from evidence or from other facts

### 2. Criteria Richness

Ask:

- is one criterion enough?
- do I need a compatible pair such as `minimum` plus `maximum`?
- does the fact need value comparison, membership, exclusion, or presence-only evaluation?

Keep the criteria input simple for as long as possible.

If the policy is becoming complex, prefer keeping the complexity in Python test logic rather than pushing more semantics into transport.

### 3. Decision Topology

Ask:

- is this a direct comparison?
- is this a conjunction across several facts?
- is this branching logic inside the test?
- is this heading toward tiered or lookup-style reasoning?

The evaluator transport should stay simple.

The Python test owns the reasoning.

### 4. Establishment Strategy

Ask:

- should the test stop at the first unestablished fact?
- should it gather the full fact picture before returning `inconclusive`?

Use:

- [Fact Establishment Patterns](fact-establishment-patterns.md)

### 5. Code Organization Pressure

Ask:

- is `evaluate(...)` still readable?
- are parsing, establishment, and reasoning still cleanly separated?
- are helper names telling the truth about what they do?

Use:

- [Scaffold Guide](scaffold.md)

## Scaling Patterns In Recommended Order

Do not jump from a starter test straight to advanced internal policy logic.

Grow one dimension at a time.

Recommended order:

1. richer criteria for one fact
2. typed parsing for one fact
3. structural comparison for one fact
4. multiple subjects with one combined conclusion
5. dependent or derived facts
6. internal conditional or tiered reasoning

Why this order works:

- it lets you preserve clarity while adding capability
- it makes failures easier to diagnose
- it reduces the risk of mixing too many new responsibilities at once

### Example Growth Path

Reasonable growth path:

1. `status equals`
2. `coverage minimum`
3. `coverage minimum` plus `maximum`
4. `review_date` or `last_review_timestamp` as a typed fact
5. structural equality such as object or array checks
6. `coverage` plus `branch_coverage` in one conclusion
7. derived or branched reasoning if the domain really requires it

Use these docs while growing:

- [Authoring Examples Index](authoring-examples-index.md)
- [Evaluation Input Patterns](evaluation-input-patterns.md)

## Where Worked Examples Help Most

This page does not need a worked example under every heading.

That would make it repetitive and harder to navigate.

The highest-value places for worked examples are the places where advanced authors most often need to see the whole chain at once:

- caller-owned `evaluations`
- evidence shape
- extracted or established facts
- test-owned reasoning
- returned result

That means the best places for worked examples are:

- multi-subject test design
- typed fact design
- structural fact design
- derived fact design

Those are the places where syntax alone is not enough.

They are also the places where the existing executable fixture library already gives us strong canonical examples.

## How To Write The Python, Incrementally

The most important authoring point is this:

- do not try to write the final advanced test in one pass

Write it in layers.

That matters even more if the author is not deeply comfortable with Python yet.

The safest way to author these tests is:

1. get the public `evaluate(...)` shape correct
2. make the metadata checks explicit
3. index the caller-owned `evaluations`
4. extract one fact correctly
5. add fact-establishment handling
6. add the actual policy comparison
7. only then add:
   - more subjects
   - typed parsing
   - derived facts
   - richer internal reasoning

### Base Advanced Skeleton

This is the Python shape you should usually grow from:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    policy_error = _validate_policy_inputs(evaluation_index)
    if policy_error is not None:
        return policy_error

    facts = _extract_facts(evidence, evaluation_index)
    blocking_result = _handle_unestablished_facts(facts)
    if blocking_result is not None:
        return blocking_result

    return _evaluate_policy(facts, evaluation_index)


def _validate_metadata(metadata, evidence):
    if metadata.get("evidence_type") != "json":
        return _build_inconclusive_result("This test expects JSON evidence.")
    if metadata.get("schema_version") != "2":
        return _build_inconclusive_result("This test only supports evaluator schema version 2.")
    if not isinstance(evidence, dict):
        return _build_inconclusive_result("This test expects JSON evidence as a dictionary.")
    return None


def _index_evaluations(evaluations):
    indexed = {}
    for item in evaluations:
        subject = item.get("subject", {})
        name = subject.get("name")
        if isinstance(name, str):
            indexed[name] = item
    return indexed
```

That skeleton is intentionally simple.

It gives the author a stable outer shape before the domain-specific logic starts expanding.

### How To Grow That Skeleton

For advanced tests, grow the file in this order:

1. add `_validate_policy_inputs(...)`
   This is where you prove the required subject names and criteria keys exist.
2. add `_extract_facts(...)`
   Start with one fact, then grow to several.
3. add `_handle_unestablished_facts(...)`
   This is where fail fast or fail slow becomes explicit.
4. add `_evaluate_policy(...)`
   Keep actual business reasoning here.
5. if needed, add:
   - typed parsing helpers
   - derived-fact helpers
   - public-fact helpers when internal parsed state should not leak into returned facts

### What Not To Do

Do not start with:

- one giant `evaluate(...)` function
- inline dictionary lookups everywhere
- mixed extraction and policy reasoning in the same block

That usually works for 20 lines and then becomes hard to debug.

The worked examples below should therefore be read in two ways:

- as examples of input and result behavior
- as examples of how the Python file should be layered

## Multi-Subject Test Design

Multi-subject tests are where many authors accidentally start trying to put policy logic into the transport.

Do not do that.

The transport should keep saying:

- what subjects exist
- what criteria belong to each subject

The Python test should keep deciding:

- how those subjects are reasoned about together

### Good Mental Model

Caller-owned input answers:

- what facts matter
- how each fact is typed
- what threshold or expected values apply

Test-owned logic answers:

- how those facts interact
- which conditions are sufficient or insufficient
- how the final `true`, `false`, or `inconclusive` conclusion is reached

### Good First Multi-Subject Pattern

Use a conjunction first.

Example shape:

```json
[
  {
    "subject": {
      "name": "coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 80
    }
  },
  {
    "subject": {
      "name": "branch_coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 70
    }
  }
]
```

Then let the Python test decide how those criteria combine.

Primary fixtures:

- [verify_dual_coverage_fail_fast.py](../../../tests/json/test_of_detail/verify_dual_coverage_fail_fast.py)
- [verify_dual_coverage_thresholds.py](../../../tests/json/test_of_detail/verify_dual_coverage_thresholds.py)

### Fail Fast Versus Fail Slow In Multi-Subject Tests

Fail fast works well when:

- one missing fact already blocks useful evaluation
- you want the easiest control flow first

Fail slow works well when:

- several facts matter
- diagnostic completeness is important
- you want the returned `facts` set to explain the broader evidence condition

Do not decide this abstractly.

Decide it based on:

- how many facts matter
- whether those facts can be established independently
- how much diagnostic value the extra collection provides

### Worked Example: Two Coverage Facts, One Combined Conclusion

Use this fixture:

- [verify_dual_coverage_thresholds.py](../../../tests/json/test_of_detail/verify_dual_coverage_thresholds.py)

Use this evidence:

- [component_assurance.json](../../../tests/json/evidence/component_assurance.json)

Evidence shape:

```json
{
  "component": {
    "release_status": "approved",
    "feature_enabled": true,
    "service_owner": "alice",
    "build_age_days": 14,
    "measures": [
      {
        "metric": "coverage",
        "value": 85
      },
      {
        "metric": "branch_coverage",
        "value": 96
      }
    ]
  }
}
```

Caller-owned `evaluations`:

```json
[
  {
    "subject": {
      "name": "coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 80
    }
  },
  {
    "subject": {
      "name": "branch_coverage",
      "data_type": "number"
    },
    "criteria": {
      "minimum": 95
    }
  }
]
```

What the test establishes:

```json
[
  {
    "name": "coverage",
    "value": 85.0,
    "value_type": "number",
    "unit": "percent",
    "status": "found"
  },
  {
    "name": "branch_coverage",
    "value": 96.0,
    "value_type": "number",
    "unit": "percent",
    "status": "found"
  }
]
```

How the reasoning works:

1. validate that both `coverage` and `branch_coverage` evaluations exist
2. read `criteria.minimum` for each subject
3. extract both evidence facts
4. if either fact is missing or invalid, return `inconclusive`
5. if both facts are established, compare each fact to its own minimum
6. return one combined conclusion

Python structure to write first:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    coverage_evaluation = evaluation_index.get("coverage")
    branch_evaluation = evaluation_index.get("branch_coverage")
    if coverage_evaluation is None or branch_evaluation is None:
        return _build_inconclusive_result(
            "This test requires both coverage and branch_coverage evaluations with minimum criteria."
        )

    coverage_minimum = _read_numeric_criterion(coverage_evaluation, "minimum")
    branch_minimum = _read_numeric_criterion(branch_evaluation, "minimum")
    if coverage_minimum is None or branch_minimum is None:
        return _build_inconclusive_result(
            "This test requires coverage and branch_coverage criteria.minimum values to be numeric."
        )

    facts = {
        "coverage": _extract_measure_fact(evidence, "coverage"),
        "branch_coverage": _extract_measure_fact(evidence, "branch_coverage"),
    }
    missing_or_invalid = [
        fact for fact in facts.values() if fact["status"] != "found"
    ]
    if missing_or_invalid:
        return _build_inconclusive_result(
            list(facts.values()),
            "Unable to evaluate because one or more required coverage facts could not be established.",
        )

    return _evaluate_dual_thresholds(
        facts["coverage"],
        facts["branch_coverage"],
        coverage_minimum,
        branch_minimum,
    )
```

How to build that Python incrementally:

1. write `evaluate(...)` plus `_validate_metadata(...)`
2. make the two required evaluation lookups explicit
3. add `_read_numeric_criterion(...)`
4. add `_extract_measure_fact(...)` for one metric first
5. reuse `_extract_measure_fact(...)` for the second metric
6. choose fail fast or fail slow for missing facts
7. only then write `_evaluate_dual_thresholds(...)`

Returned result:

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "coverage",
      "value": 85.0,
      "value_type": "number",
      "unit": "percent",
      "status": "found"
    },
    {
      "name": "branch_coverage",
      "value": 96.0,
      "value_type": "number",
      "unit": "percent",
      "status": "found"
    }
  ],
  "reason": "Coverage is 85.0% and branch_coverage is 96.0%, which both meet their required minimums."
}
```

Why this is a strong advanced example:

- the transport still stays simple
- each subject keeps its own criteria
- the combined reasoning stays in Python
- the returned result is still one clean V2 result object

What this example teaches:

- multi-subject does not mean a new transport model
- one test can consume several evaluations and still return one conclusion
- advanced logic should be added in the test, not pushed into `criteria`

## Typed And Structural Fact Design

Typed and structural facts are still test-owned responsibilities.

They are not evaluator-owned business logic.

### Typed Facts

Common typed facts:

- `integer`
- `number`
- `date`
- `datetime`
- `duration`

The main idea is:

- extract raw evidence
- parse it into the needed type
- record whether the parsed fact is `found`, `not_found`, or `invalid`
- evaluate only after establishment is explicit

Useful fixtures:

- [verify_build_age_days_range.py](../../../tests/json/test_of_detail/verify_build_age_days_range.py)
- [verify_last_review_timestamp_range.py](../../../tests/json/test_of_detail/verify_last_review_timestamp_range.py)
- [verify_review_date_range.py](../../../tests/json/test_of_detail/verify_review_date_range.py)
- [verify_restore_duration_range.py](../../../tests/json/test_of_detail/verify_restore_duration_range.py)

### Worked Example: Typed Date Range

Use this fixture:

- [verify_review_date_range.py](../../../tests/json/test_of_detail/verify_review_date_range.py)

Use this evidence:

- [operations_timing.json](../../../tests/json/evidence/operations_timing.json)

Evidence shape:

```json
{
  "backup_review": {
    "review_date": "2026-06-15",
    "restore_duration": "PT45M"
  }
}
```

Caller-owned `evaluations`:

```json
[
  {
    "subject": {
      "name": "review_date",
      "data_type": "date"
    },
    "criteria": {
      "minimum": "2026-06-01",
      "maximum": "2026-06-30"
    }
  }
]
```

What the test does internally:

1. validate that the `review_date` evaluation exists
2. parse `criteria.minimum` and `criteria.maximum` into actual date values
3. extract the raw evidence field `backup_review.review_date`
4. parse the raw value into a date
5. if parsing fails, return `inconclusive` because the fact is `invalid`
6. if parsing succeeds, compare the parsed date to the allowed range

Python structure to write first:

```python
from datetime import date


def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    review_evaluation = evaluation_index.get("review_date")
    if review_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a review_date evaluation with minimum and maximum criteria."
        )

    minimum = _read_date_criterion(review_evaluation, "minimum")
    maximum = _read_date_criterion(review_evaluation, "maximum")
    if minimum is None or maximum is None:
        return _build_inconclusive_result(
            "This test requires review_date criteria.minimum and criteria.maximum to be ISO-8601 dates."
        )

    review_fact = _extract_review_date_fact(evidence)
    if review_fact["status"] != "found":
        return _build_inconclusive_result(
            [_public_fact(review_fact)],
            "Unable to evaluate because the review_date fact could not be established.",
        )

    return _evaluate_range(review_fact, minimum, maximum)
```

What the author needs to notice:

1. typed tests usually need a parsing helper such as `_parse_iso_date(...)`
2. the internal fact may carry extra fields such as `parsed_value`
3. the returned public fact should stay simple and readable
4. typed parsing errors are usually `inconclusive` when the evidence fact is unusable
5. malformed criteria values are usually returned as test-level `inconclusive` with a precise reason

Public fact returned by the test:

```json
[
  {
    "name": "review_date",
    "value": "2026-06-15",
    "value_type": "date",
    "status": "found"
  }
]
```

Returned result:

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "review_date",
      "value": "2026-06-15",
      "value_type": "date",
      "status": "found"
    }
  ],
  "reason": "review_date is 2026-06-15, which is within the allowed range of 2026-06-01 to 2026-06-30."
}
```

Why this is a strong advanced example:

- the caller still provides simple string input
- the test owns parsing and typed comparison
- the returned fact stays public and readable even though the test uses an internal parsed value

What this example teaches:

- typed authoring is not just a different label in `data_type`
- the test must own parsing discipline
- typed parsing should not leak complicated internal state into the public fact record

### Structural Facts

Common structural facts:

- `array`
- `object`
- `null`

Useful distinctions:

- exact array equality is not the same as membership logic
- exact object equality is not the same as field-by-field policy reasoning
- explicit `null` is not the same as missing

Useful fixtures:

- [verify_approver_profile_equals.py](../../../tests/json/test_of_detail/verify_approver_profile_equals.py)
- [verify_reviewer_roles_equals.py](../../../tests/json/test_of_detail/verify_reviewer_roles_equals.py)
- [verify_revocation_reason_null.py](../../../tests/json/test_of_detail/verify_revocation_reason_null.py)

### Worked Example: Exact Object Equality

Use this fixture:

- [verify_approver_profile_equals.py](../../../tests/json/test_of_detail/verify_approver_profile_equals.py)

Use this evidence:

- [access_grant_state.json](../../../tests/json/evidence/access_grant_state.json)

Evidence shape:

```json
{
  "access_grant": {
    "approver_profile": {
      "id": "manager-123",
      "department": "security"
    },
    "reviewer_roles": [
      "manager",
      "security"
    ],
    "revocation_reason": null
  }
}
```

Caller-owned `evaluations`:

```json
[
  {
    "subject": {
      "name": "approver_profile",
      "data_type": "object"
    },
    "criteria": {
      "equals": {
        "id": "manager-123",
        "department": "security"
      }
    }
  }
]
```

What the test does internally:

1. validate that `approver_profile` exists in `evaluations`
2. validate that `criteria.equals` is an object
3. extract `access_grant.approver_profile`
4. determine whether the fact is `found`, `not_found`, or `invalid`
5. compare the extracted object to the expected object using exact equality

Python structure to write first:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    approver_evaluation = evaluation_index.get("approver_profile")
    if approver_evaluation is None:
        return _build_inconclusive_result(
            "This test requires an approver_profile evaluation with an equals criterion."
        )

    expected_profile = approver_evaluation.get("criteria", {}).get("equals")
    if not isinstance(expected_profile, dict):
        return _build_inconclusive_result(
            "This test requires approver_profile criteria.equals to be an object."
        )

    approver_fact = _extract_approver_profile_fact(evidence)
    if approver_fact["status"] != "found":
        return _build_inconclusive_result(
            [approver_fact],
            "Unable to evaluate because the approver_profile fact could not be established.",
        )

    return _evaluate_equals(approver_fact, expected_profile)
```

What the author needs to notice:

1. structural tests still start with ordinary metadata and evaluation validation
2. the extraction helper should prove the type of the evidence value
3. exact object equality is valid when exact equality is really the requirement
4. field-by-field reasoning should be a separate policy helper if the domain becomes richer

Public fact returned by the test:

```json
[
  {
    "name": "approver_profile",
    "value": {
      "id": "manager-123",
      "department": "security"
    },
    "value_type": "object",
    "status": "found"
  }
]
```

Returned result:

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "approver_profile",
      "value": {
        "id": "manager-123",
        "department": "security"
      },
      "value_type": "object",
      "status": "found"
    }
  ],
  "reason": "approver_profile exactly matches the expected object."
}
```

Why this is a strong advanced example:

- it shows that structural facts can still stay simple when exact equality is the real need
- it avoids inventing a field-by-field mini-language in `criteria`
- it makes the difference between object equality and richer object reasoning explicit

What this example teaches:

- use exact equality when exact equality is the real requirement
- do not overcomplicate the pattern if the simple pattern is already correct
- if the domain needs field-by-field conditions later, that logic belongs in Python, not in a more overloaded transport shape

### Practical Rule

If one structural or typed pattern solves the problem directly, use it directly.

If the domain starts requiring several conditional interpretations of the same structure, the logic belongs in the Python test, not in a more complicated `criteria` transport shape.

## Derived Facts And Internal Reasoning Boundaries

Some advanced tests need facts that are not present directly in evidence.

That is acceptable.

The key is to make the derived fact explicit.

### Good Practice

- give the derived fact a real name
- record it in the returned `facts` when it materially affects the decision
- keep the derivation readable
- keep extraction and reasoning separate where possible

### Example Situations

- computing build age from a timestamp
- deriving a percentage from two evidence values
- normalizing several raw fields into one domain fact

### Boundary Rule

Do not let “derived fact” become an excuse to hide policy logic in parsing helpers.

Prefer a structure like:

1. extract raw evidence values
2. parse or normalize them
3. derive the needed fact
4. evaluate the policy

Use:

- [Scaffold Guide](scaffold.md)

### Worked Example: Derived Coverage Gap

Use this fixture:

- [verify_coverage_gap_maximum.py](../../../tests/json/test_of_detail/verify_coverage_gap_maximum.py)

Use this evidence:

- [component_assurance.json](../../../tests/json/evidence/component_assurance.json)

Evidence shape:

```json
{
  "component": {
    "release_status": "approved",
    "feature_enabled": true,
    "service_owner": "alice",
    "build_age_days": 14,
    "measures": [
      {
        "metric": "coverage",
        "value": 85
      },
      {
        "metric": "branch_coverage",
        "value": 96
      }
    ]
  }
}
```

Caller-owned `evaluations`:

```json
[
  {
    "subject": {
      "name": "coverage_gap",
      "data_type": "number"
    },
    "criteria": {
      "maximum": 15
    }
  }
]
```

What the test does internally:

1. validate that the `coverage_gap` evaluation exists
2. read `criteria.maximum`
3. extract the raw `coverage` fact
4. extract the raw `branch_coverage` fact
5. derive `coverage_gap` from those two facts
6. if either prerequisite fact cannot be established, return `inconclusive`
7. if the derived fact is established, compare it to the caller-provided maximum

Python structure to write first:

```python
def evaluate(evidence, evaluations, metadata):
    metadata_error = _validate_metadata(metadata, evidence)
    if metadata_error is not None:
        return metadata_error

    evaluation_index = _index_evaluations(evaluations)
    gap_evaluation = evaluation_index.get("coverage_gap")
    if gap_evaluation is None:
        return _build_inconclusive_result(
            "This test requires a coverage_gap evaluation with a maximum criterion."
        )

    maximum = _read_numeric_criterion(gap_evaluation, "maximum")
    if maximum is None:
        return _build_inconclusive_result(
            "This test requires coverage_gap criteria.maximum to be numeric."
        )

    coverage_fact = _extract_measure_fact(evidence, "coverage")
    branch_fact = _extract_measure_fact(evidence, "branch_coverage")
    gap_fact = _derive_coverage_gap_fact(coverage_fact, branch_fact)
    if gap_fact["status"] != "found":
        return _build_inconclusive_result(
            [
                _public_fact(coverage_fact),
                _public_fact(branch_fact),
                _public_fact(gap_fact),
            ],
            "Unable to evaluate because the derived coverage_gap fact could not be established.",
        )

    return _evaluate_gap(coverage_fact, branch_fact, gap_fact, maximum)
```

Derived-fact helper shape:

```python
def _derive_coverage_gap_fact(coverage_fact, branch_fact):
    statuses = {coverage_fact["status"], branch_fact["status"]}
    if "invalid" in statuses:
        return {
            "name": "coverage_gap",
            "value": None,
            "value_type": "number",
            "unit": "percentage_points",
            "status": "invalid",
        }
    if "not_found" in statuses:
        return {
            "name": "coverage_gap",
            "value": None,
            "value_type": "number",
            "unit": "percentage_points",
            "status": "not_found",
        }

    return {
        "name": "coverage_gap",
        "value": abs(branch_fact["value"] - coverage_fact["value"]),
        "value_type": "number",
        "unit": "percentage_points",
        "status": "found",
    }
```

What the author needs to notice:

1. a derived fact still gets its own explicit fact record
2. prerequisite fact statuses control the derived fact status
3. the derivation helper should compute one thing clearly
4. the evaluation helper should compare the derived fact, not recompute it again

Public facts returned by the test:

```json
[
  {
    "name": "coverage",
    "value": 85.0,
    "value_type": "number",
    "unit": "percent",
    "status": "found"
  },
  {
    "name": "branch_coverage",
    "value": 96.0,
    "value_type": "number",
    "unit": "percent",
    "status": "found"
  },
  {
    "name": "coverage_gap",
    "value": 11.0,
    "value_type": "number",
    "unit": "percentage_points",
    "status": "found"
  }
]
```

Returned result:

```json
{
  "conclusion": "true",
  "facts": [
    {
      "name": "coverage",
      "value": 85.0,
      "value_type": "number",
      "unit": "percent",
      "status": "found"
    },
    {
      "name": "branch_coverage",
      "value": 96.0,
      "value_type": "number",
      "unit": "percent",
      "status": "found"
    },
    {
      "name": "coverage_gap",
      "value": 11.0,
      "value_type": "number",
      "unit": "percentage_points",
      "status": "found"
    }
  ],
  "reason": "coverage_gap is 11.0 percentage points, derived from coverage 85.0% and branch_coverage 96.0%, which is within the allowed maximum of 15.0."
}
```

Why this is a strong advanced example:

- the caller still supplies a simple one-subject criterion
- the test makes the derivation explicit instead of hiding it
- the returned facts show both prerequisites and the derived fact
- the policy logic stays in the Python test without turning transport into a derived-expression language

What this example teaches:

- derived facts are legitimate test-owned authoring patterns
- derived facts should be explicitly named
- a derived fact can be the thing that is actually evaluated, even when its prerequisites come from several raw evidence facts

## Anti-Patterns

Advanced authoring fails most often when complexity grows faster than structure.

Watch for these anti-patterns.

### 1. Overloading `criteria`

Bad pattern:

- trying to encode the full policy in transport

Why it is a problem:

- it blurs evaluator-owned and test-owned responsibility
- it makes input packets harder to understand
- it pressures the transport into becoming a DSL

### 2. Mixing Extraction And Evaluation

Bad pattern:

- deciding policy while still trying to establish raw facts

Why it is a problem:

- returned reasons become confusing
- `inconclusive` and `false` logic get mixed together

### 3. Too Many Vague Helpers

Bad pattern:

- helpers named things like `_process_data(...)` or `_check_rules(...)`

Why it is a problem:

- readers cannot tell which responsibility lives where
- debugging gets harder, not easier

### 4. Weak Reasons From Complex Tests

Bad pattern:

- returning a conclusion with a reason that does not explain which fact or logic path mattered

Why it is a problem:

- advanced tests need stronger diagnosis, not weaker diagnosis

### 5. Jumping To Advanced Logic Too Early

Bad pattern:

- writing branched or tiered reasoning before basic fact discipline is stable

Why it is a problem:

- the test becomes hard to trust
- the failure path becomes hard to explain

## Decision Matrix

If you are stuck, use this quick routing table.

| If you are trying to decide... | Go here |
| --- | --- |
| which fixture to copy next | [Authoring Examples Index](authoring-examples-index.md) |
| which `subject` / `criteria` shape to use | [Evaluation Input Patterns](evaluation-input-patterns.md) |
| how to structure the Python file | [Scaffold Guide](scaffold.md) |
| how to choose fail fast versus fail slow | [Fact Establishment Patterns](fact-establishment-patterns.md) |
| how to get from beginner to intermediate authoring | [Authoring Progression](authoring-progression.md) |

## Boundary Of Current Recommendation

This page is about current recommended authoring direction, not every possible future pattern.

Recommended now:

- direct compare
- compatible multi-key criteria for one subject
- typed fact handling
- structural equality patterns
- multi-subject conjunction
- deliberate fail-fast or fail-slow choice

Documented as later or future-thinking only:

- internal conditional policy beyond the simple canonical fixtures
- tiered or lookup-style reasoning
- more specialized domain logic families

Do not treat later ideas as if they are a standardized transport surface.

The evaluator transport should remain simple.

The Python test should remain the place where richer reasoning lives.
