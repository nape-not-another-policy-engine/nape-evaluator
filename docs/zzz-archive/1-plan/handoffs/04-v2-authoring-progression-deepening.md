> Historical document
>
> This document is retained for historical reference only.
> It should not be used for any current execution, implementation, or decision-making unless it is being referenced explicitly for historical or traceability purposes.

# Handoff 04: V2 Authoring Progression Deepening

## Purpose

Record the completed state and closure decision for the authoring-progression deepening workstream.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/zzz-archive/1-plan/plans/04-v2-authoring-progression-deepening.md`
3. `docs/user/v2-test-authoring/authoring-progression.md`
4. `docs/user/v2-test-authoring/authoring-examples-index.md`
5. `docs/user/v2-test-authoring/evaluation-input-patterns.md`
6. `docs/user/test-of-detail-authoring.md`
7. `docs/product/current-evaluator-reference.md`

## Current State

- the V2 authoring guide set is now broad and executable:
  - progression guide
  - examples index
  - scaffold guide
  - fact extraction guide
  - fact-establishment guidance
  - evaluation-input pattern library
- the fixture library now covers starter, typed, structural, temporal, fail-fast, fail-slow, invalid extracted fact, and invalid caller-criteria paths
- the current remaining weakness is not runtime accuracy; it is teaching sequence and tutorial depth
- the selected direction for the progression is now:
  - first success
  - then first caller-driven rule
  - then safety and diagnosability
  - then helper decomposition
  - then richer scaling
- the progression backbone has now been rewritten to match that teaching order
- the progression now explicitly distinguishes:
  - quick-start authoring
  - production-grade authoring
- the current progression now already provides:
  - revised stage order
  - explicit stage rationale
  - explicit “why this stage is not enough yet” transitions
  - a cleaner beginner-to-expert narrative
- the progression now also provides:
  - visible grouped parts:
    - Part 1: Get Working Quickly
    - Part 2: Make It Safe And Diagnosable
    - Part 3: Make It Maintainable And Scalable
  - deeper `Stage 0` through `Stage 3` sections with inline input, code, output, and failure-mode examples
  - explicit early-stage Python-writing guidance:
    - one shared “write the Python as you go” section
    - stage-level “how to write this Python” guidance for `Stage 0` through `Stage 6`
- the next bounded planning slice is now also selected:
  - `Stage 4` through `Stage 6` are now planned at higher precision
  - no new companion page is selected yet
  - the existing scaffold, examples index, and pattern library should carry most of the later-stage detail
- the selected later-stage teaching direction is now:
  - `Stage 4`
    - teach fail fast versus fail slow as a diagnosability and control-flow choice
    - anchor on `verify_dual_coverage_fail_fast.py` and `verify_dual_coverage_thresholds.py`
  - `Stage 5`
    - teach helper decomposition as the consequence of clarified responsibilities
    - anchor on `scaffold.md`, the scaffold template, `verify_author_complete.py`, and `verify_review_date_range.py`
  - `Stage 6`
    - teach scale-up as one new dimension at a time:
      - richer criteria
      - typed parsing
      - structural comparisons
      - multi-subject reasoning
    - anchor on range, typed temporal, structural, and dual-coverage fixtures
- the progression now also applies that later-stage plan:
  - `Stage 4` now includes inline fail-fast versus fail-slow contrasts and compact `inconclusive` examples
  - `Stage 5` now includes a compact helper skeleton plus explicit scaffold cross-links
  - `Stage 6` now includes a growth ladder, pattern-family table, and stronger links into the examples index and pattern library
- the current recommended next documentation move is now more concrete:
  - the approved advanced companion page now exists at:
    - `docs/user/v2-test-authoring/advanced-authoring-patterns.md`
  - it is a synthesis page, not another progression rewrite and not a fixture dump
  - the detailed section outline and link strategy remain captured in Plan 04
- the new page is now integrated into the guide set:
  - `README.md` reading order includes it
  - `authoring-progression.md` links to it from the later-stage guidance
  - `authoring-examples-index.md`, `evaluation-input-patterns.md`, and `scaffold.md` now route advanced readers toward it
- the advanced page is no longer synthesis-only:
  - it now includes worked examples for:
    - multi-subject conjunction
    - typed date range evaluation
    - structural object equality
    - derived numeric fact comparison
  - the canonical dedicated derived-fact fixture now exists at:
    - `tests/json/test_of_detail/verify_coverage_gap_maximum.py`
  - that fixture is documented in the advanced page, examples index, and evaluation-input pattern library
- a first deliberate red-team pass on the full guide set has now been completed
- that pass found and fixed two doc-system issues:
  - entry-point navigation was too weak:
    - `README.md`, `overview.md`, and `test-of-detail-authoring.md` now route readers by need, not only by linear reading order
  - early progression snippets were accidentally regressing from fact-aware result examples back to simplified `facts: []` success paths:
    - `authoring-progression.md` now keeps the early stages incrementally consistent with the stated "harden, do not invalidate" teaching model
- the remaining advanced-example question has now been resolved:
  - the current advanced worked-example set is sufficient
  - no additional canonical advanced conditional-policy pattern should be added in this workstream
  - the selected boundary is to keep this guide set centered on verification of facts and evidence-backed test-of-detail conclusions, not broader policy branching

## Selected Direction

Do not plan the entire deepened tutorial in one pass.

Use progressive section planning:

1. stabilize the teaching backbone first
2. then deepen the earlier stages
3. then plan the later stages with more precision after the backbone is validated

## Closure Decision

This workstream is complete.

Do not continue it by default.

If a future need emerges, treat it as a new explicit refinement decision rather than unfinished residue from Plan 04.

## Why It Closed

- the authoring progression now teaches the intended staged path
- the companion docs now route readers by need
- the advanced page now covers the selected advanced example families
- the remaining plausible addition, conditional policy, was explicitly rejected for this workstream because it would pull the guide set away from fact verification and toward broader policy logic

## If Reopened Later

Only reopen a similar workstream if one of these becomes true:

- product direction broadens the intended role of test-of-detail authoring guidance
- users need a new advanced example family that is still clearly within fact-verification boundaries
- the current guide set shows a real teaching failure in practice

## Guardrails

- do not quietly drift back to “code organization first” as the middle-stage teaching model
- do not invalidate the value of the hardcoded starter path
- do not imply that production-grade authoring is required for a first successful test
- do not broaden this guide set into a general policy-design guide without an explicit new decision

## Durable Outputs

- the completed authoring guide set under `docs/user/v2-test-authoring/`
- the tightened routing in:
  - `docs/user/test-of-detail-authoring.md`
  - `docs/user/v2-test-authoring/README.md`
  - `docs/user/v2-test-authoring/overview.md`
- the corrected early-stage progression examples in:
  - `docs/user/v2-test-authoring/authoring-progression.md`
