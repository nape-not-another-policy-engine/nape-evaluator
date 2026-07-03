# Plan 21: Domain Example Pack Implementation Wave 6

## Purpose

Implement the sixth domain-rich example pack as executable evaluator examples and routing docs.

Wave 6 starts with medical device release packet assurance.

## Why This Exists

The first five domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, and payment settlement readiness.

The next gap is a safety-critical product assurance example family centered on release-packet completeness and release blocking conditions.

## Selected Direction

The implemented pack will be:

- medical device release packet assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent medical device release evidence family
2. release review status fixture
3. SBOM presence fixture
4. critical vulnerability count fixture
5. one combined release packet readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new medical device release evidence fixtures:
  - `tests/json/evidence/medical_device_release_ready.json`
  - `tests/json/evidence/medical_device_release_missing_sbom.json`
  - `tests/json/evidence/medical_device_release_blocked.json`
- new medical device single-subject fixtures:
  - `tests/json/test_of_detail/verify_medical_device_release_review_approved.py`
  - `tests/json/test_of_detail/verify_medical_device_sbom_present.py`
  - `tests/json/test_of_detail/verify_medical_device_critical_vulnerability_count_maximum.py`
- new medical device combined fixture:
  - `tests/json/test_of_detail/verify_medical_device_release_packet_readiness.py`
- pattern-library coverage added in:
  - `tests/json/test_pattern_library.py`
- routing and domain docs updated in:
  - `docs/user/v2-test-authoring/domain-examples.md`
  - `docs/user/v2-test-authoring/authoring-examples-index.md`
  - `docs/user/v2-test-authoring/domain-packs-overview.md`

Validation completed:

- `python3 -m unittest tests.json.test_pattern_library`
- `python3 -m unittest discover`
- `make docs-smoke`

Closure review result:

- the medical device release pack is complete enough to serve as the sixth domain-rich exemplar
- the cross-pack progression now extends from authorization and operations into business-process and safety-critical product assurance
