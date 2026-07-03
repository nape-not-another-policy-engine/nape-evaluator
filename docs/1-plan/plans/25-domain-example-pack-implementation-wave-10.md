# Plan 25: Domain Example Pack Implementation Wave 10

## Purpose

Implement the tenth domain-rich example pack as executable evaluator examples and routing docs.

Wave 10 starts with IT / OT boundary verification assurance.

## Why This Exists

The first nine domain-rich packs now cover privileged access, utility / field restore readiness, transportation inspection freshness, manufacturing line restart readiness, payment settlement readiness, medical device release packet readiness, regulated quality batch release readiness, cold-chain exception readiness, and system-of-systems event confirmation readiness.

The next gap is an explicit IT / OT boundary verification family centered on remote access, controller internet exposure, and boundary-control state.

## Selected Direction

The implemented pack will be:

- IT / OT boundary verification assurance

The pack should include:

- simple single-subject fixtures
- one richer combined fixture
- coherent example evidence
- pattern-library tests that prove caller-owned evaluations are actually used
- doc routing that treats the pack as a domain example family rather than scattered generic fixtures

## Scope

Implement:

1. one coherent IT / OT boundary evidence family
2. remote access enabled fixture
3. internet exposed controller count fixture
4. boundary control status fixture
5. one combined IT / OT boundary readiness fixture
6. example-index and domain-doc updates
7. automated validation

## Completion Snapshot

This plan is complete.

Landed outcomes:

- new IT / OT boundary evidence fixtures:
  - `tests/json/evidence/it_ot_boundary_safe.json`
  - `tests/json/evidence/it_ot_boundary_remote_access_enabled.json`
  - `tests/json/evidence/it_ot_boundary_exposed.json`
- new IT / OT boundary single-subject fixtures:
  - `tests/json/test_of_detail/verify_it_ot_remote_access_disabled.py`
  - `tests/json/test_of_detail/verify_it_ot_internet_exposed_controller_count_maximum.py`
  - `tests/json/test_of_detail/verify_it_ot_boundary_control_segmented.py`
- new IT / OT boundary combined fixture:
  - `tests/json/test_of_detail/verify_it_ot_boundary_readiness.py`
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

- the IT / OT boundary pack is complete enough to serve as the tenth domain-rich exemplar
- the cross-pack progression now extends from multi-source confirmation into explicit boundary-control and exposure verification
