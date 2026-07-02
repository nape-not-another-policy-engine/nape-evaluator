# Authoring Examples Index

This page is the index into the executable V2 test-of-detail fixture library.

Use it when you want to answer questions like:

- which example should I copy first?
- which examples are simplest?
- which examples match my assurance domain?
- which examples demonstrate fail fast versus fail slow?

All executable fixtures referenced here live under:

- `tests/json/`
- `tests/xml/`
- `tests/yaml/`
- `tests/text/`
- `tests/pdf/`

Each format-family example tree uses the same basic model when practical:

- `evidence/`
- `test_of_detail/`
- `test_pattern_library.py`

## Quick Start Recommendation

If you only want three examples to begin with, use:

1. `verify_author_complete.py`
2. `verify_component_coverage_minimum.py`
3. `verify_dual_coverage_fail_fast.py`

That gives you:

- one simple text equality example
- one simple threshold example
- one simple multi-subject example

## By Evidence Format

### JSON

Use these when you want the broadest current example library.

- `tests/json/test_of_detail/verify_author_complete.py`
- `tests/json/test_of_detail/verify_component_coverage_minimum.py`
- `tests/json/test_of_detail/verify_dual_coverage_fail_fast.py`

### XML

Use this when you want the simplest structured non-dictionary example.

- `tests/xml/test_of_detail/verify_author_complete.py`

Use this next when your XML evidence uses namespaces.

- `tests/xml/test_of_detail/verify_author_complete_namespaced.py`

### YAML

Use this when you want a structured object example that feels close to JSON but still exercises typed YAML loading.

- `tests/yaml/test_of_detail/verify_component_coverage_minimum.py`

Use this next when the YAML value is present but invalid for the subject data type.

- `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`

### Text

Use this when you want the simplest line-oriented parser example.

- `tests/text/test_of_detail/verify_author_complete.py`

Use this next when text evidence contains competing candidate values and the fact cannot be established cleanly.

- `tests/text/test_of_detail/verify_author_complete_ambiguous.py`

### PDF

Use this when you want a text-extraction-backed example and need to see the defensive difference between plain text and PDF-derived text.

- `tests/pdf/test_of_detail/verify_author_complete.py`

Use this next when PDF extraction yields competing candidate values and the result should be `inconclusive`.

- `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`

## By Difficulty

### Starter

These are the best first examples to copy.

| Fixture | Why start here | Main pattern |
| --- | --- | --- |
| `verify_author_complete.py` | simplest text comparison and clean helper breakout | text `equals` |
| `verify_component_coverage_minimum.py` | simplest numeric threshold | number `minimum` |
| `verify_feature_flag_enabled.py` | simplest boolean comparison | boolean `equals` |
| `verify_service_owner_required.py` | simplest presence-only check | `required` |

### Intermediate

These add second criteria, richer type handling, or list/set-style comparisons.

| Fixture | Why it is intermediate | Main pattern |
| --- | --- | --- |
| `verify_component_coverage_range.py` | introduces two compatible numeric criteria in one object | number `minimum` + `maximum` |
| `verify_release_status_allowed_values.py` | moves from single equality to membership | `allowed_values` |
| `verify_release_status_disallowed_values.py` | inverse membership pattern | `disallowed_values` |
| `verify_build_age_days_range.py` | integer-specific range handling | integer `minimum` + `maximum` |
| `verify_last_review_timestamp_minimum.py` | first typed datetime parsing example | datetime `minimum` |
| `verify_review_date_range.py` | typed date parsing plus range | date `minimum` + `maximum` |
| `verify_restore_duration_range.py` | typed duration parsing plus range | duration `minimum` + `maximum` |

### Advanced

These are still bounded first-pass examples, but they are less likely to be the first fixture an author should copy.

| Fixture | Why it is advanced | Main pattern |
| --- | --- | --- |
| `verify_last_review_timestamp_range.py` | datetime parsing plus full window comparison | datetime `minimum` + `maximum` |
| `verify_approver_profile_equals.py` | exact object equality | object `equals` |
| `verify_reviewer_roles_equals.py` | exact array equality | array `equals` |
| `verify_revocation_reason_null.py` | explicit null-state handling | null `equals` |
| `verify_coverage_gap_maximum.py` | derived numeric fact from two raw evidence measures | derived fact `maximum` |
| `verify_dual_coverage_thresholds.py` | multi-subject fail-slow establishment | multi-subject conjunction |
| `verify_dual_coverage_fail_fast.py` | multi-subject fail-fast establishment | multi-subject conjunction |

If you are moving past simple fixture copying and need help understanding how these advanced examples fit together, use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)

## By Domain

### General Starter

These are good when the main goal is to learn the test shape, not to mirror a specific assurance domain.

| Fixture | Domain feel | Main pattern |
| --- | --- | --- |
| `verify_author_complete.py` | generic starter | text `equals` |
| `verify_feature_flag_enabled.py` | generic binary-state check | boolean `equals` |
| `verify_service_owner_required.py` | generic presence check | `required` |
| `tests/text/test_of_detail/verify_author_complete_ambiguous.py` | generic ambiguity handling | text `equals` with ambiguous establishment |
| `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py` | generic extracted-text ambiguity handling | text `equals` with ambiguous establishment |

### Engineering / Software Assurance

These map well to build, test, and component-quality evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_component_coverage_minimum.py` | minimum test coverage | number `minimum` |
| `verify_component_coverage_range.py` | target coverage band | number `minimum` + `maximum` |
| `verify_build_age_days_range.py` | acceptable build age window | integer `minimum` + `maximum` |
| `verify_coverage_gap_maximum.py` | allowable gap between two quality measures | derived fact `maximum` |
| `verify_dual_coverage_thresholds.py` | two required numeric quality gates | multi-subject fail slow |
| `verify_dual_coverage_fail_fast.py` | same domain with simpler establishment flow | multi-subject fail fast |
| `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py` | typed fact present but unusable | numeric threshold with invalid establishment |

### Authorization Assurance

These map well to access approval, review, and revocation evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_last_review_timestamp_minimum.py` | review is recent enough | datetime `minimum` |
| `verify_last_review_timestamp_range.py` | review falls within an allowed window | datetime `minimum` + `maximum` |
| `verify_approver_profile_equals.py` | approver metadata exactly matches expectation | object `equals` |
| `verify_reviewer_roles_equals.py` | reviewer roles exactly match expectation | array `equals` |
| `verify_revocation_reason_null.py` | field is explicitly null, not just absent | null `equals` |
| `tests/xml/test_of_detail/verify_author_complete_namespaced.py` | structured approval/status data with namespace handling | text `equals` with namespace-aware extraction |

### Operational / Timing Assurance

These map well to time-window and elapsed-time evidence.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_review_date_range.py` | review or attestation date window | date `minimum` + `maximum` |
| `verify_restore_duration_range.py` | restore or completion duration window | duration `minimum` + `maximum` |

### Status / State Assurance

These are useful when the evidence carries one or more status-like values.

| Fixture | Example concern | Main pattern |
| --- | --- | --- |
| `verify_release_status_allowed_values.py` | acceptable status list | `allowed_values` |
| `verify_release_status_disallowed_values.py` | prohibited status list | `disallowed_values` |
| `verify_author_complete.py` | exact expected status | text `equals` |

## By Establishment Style

### Fail Fast

- `verify_author_complete.py`
- `verify_component_coverage_minimum.py`
- `verify_component_coverage_range.py`
- `verify_feature_flag_enabled.py`
- `verify_release_status_allowed_values.py`
- `verify_release_status_disallowed_values.py`
- `verify_service_owner_required.py`
- `verify_build_age_days_range.py`
- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_last_review_timestamp_minimum.py`
- `verify_last_review_timestamp_range.py`
- `verify_approver_profile_equals.py`
- `verify_reviewer_roles_equals.py`
- `verify_revocation_reason_null.py`
- `verify_dual_coverage_fail_fast.py`

### Fail Slow

- `verify_coverage_gap_maximum.py`
- `verify_dual_coverage_thresholds.py`

## By Negative Path Type

### Ambiguous Extracted Fact

These examples show evidence that yields more than one competing candidate value, so the test returns `inconclusive` instead of claiming the fact is false.

- `tests/text/test_of_detail/verify_author_complete_ambiguous.py`
- `tests/pdf/test_of_detail/verify_author_complete_ambiguous.py`

Related evidence fixtures:

- `tests/text/evidence/author_verification_ambiguous_status.txt`

### Invalid Extracted Fact

These examples show evidence present but unusable, usually leading to `inconclusive`.

- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `tests/yaml/test_of_detail/verify_component_coverage_invalid_fact.py`

Related evidence fixtures:

- `operations_timing_invalid_review_date.json`
- `operations_timing_invalid_restore_duration.json`
- `tests/yaml/evidence/component_assurance_invalid_coverage.yaml`

### Namespace-Aware Extraction

This example shows evidence that is structurally valid XML but requires one explicit namespace-handling seam in the extraction helper.

- `tests/xml/test_of_detail/verify_author_complete_namespaced.py`

Related evidence fixtures:

- `tests/xml/evidence/author_verification_namespaced.xml`

### Invalid Caller Criteria For The Test

These examples show malformed criteria values that the test recognizes and rejects, usually leading to `inconclusive` with explicit test-owned reasoning.

- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_last_review_timestamp_minimum.py`
- `verify_last_review_timestamp_range.py`

### Derived Fact With Missing Prerequisite

This example shows a derived fact that cannot be established because one required raw evidence fact is missing.

- `verify_coverage_gap_maximum.py`

Related evidence fixture:

- `component_assurance_missing_branch.json`

## Recommended Copy Paths

### If You Want The Simplest Possible Starter

Copy:

- `verify_author_complete.py`

Then evolve to:

- `verify_component_coverage_minimum.py`

### If You Want A Threshold-Based Starter

Copy:

- `verify_component_coverage_minimum.py`

Then evolve to:

- `verify_component_coverage_range.py`
- `verify_build_age_days_range.py`

### If You Want A Typed Temporal Starter

Copy:

- `verify_last_review_timestamp_minimum.py`

Then evolve to:

- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_last_review_timestamp_range.py`

### If You Want A Multi-Subject Starter

Copy:

- `verify_dual_coverage_fail_fast.py`

Then evolve to:

- `verify_dual_coverage_thresholds.py`

That sequence lets authors start with simpler control flow before moving into fail-slow diagnostics.

### If You Want A Derived-Fact Starter

Copy:

- `verify_coverage_gap_maximum.py`

Use it after you already understand:

- one-subject threshold tests
- how facts are established before evaluation

That sequence helps you learn how to compute one explicit derived fact from two raw evidence facts without turning the transport into a policy language.

If the next question is no longer "which fixture should I copy?" but instead "how should I scale this authoring model safely?", use:

- [Advanced Authoring Patterns](advanced-authoring-patterns.md)
