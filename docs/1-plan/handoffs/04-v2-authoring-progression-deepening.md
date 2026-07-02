# Handoff 04: V2 Authoring Progression Deepening

## Purpose

Resume the authoring-progression deepening work without re-deciding the overall teaching direction.

## Read Order

1. `docs/1-plan/roadmap.md`
2. `docs/1-plan/plans/04-v2-authoring-progression-deepening.md`
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

## Selected Direction

Do not plan the entire deepened tutorial in one pass.

Use progressive section planning:

1. stabilize the teaching backbone first
2. then deepen the earlier stages
3. then plan the later stages with more precision after the backbone is validated

## Resume Focus

When resuming this workstream, focus on:

1. assessing whether `advanced-authoring-patterns.md` now has the right worked-example density or whether one more advanced pattern still adds clear teaching value
2. assessing whether the main progression now gives enough Python-writing guidance before authors need the scaffold or advanced page
3. tightening any redundant wording across the progression and companion docs if the new page now covers it better
4. checking whether navigation between progression, advanced patterns, examples index, and scaffold is now sufficient

## Tomorrow First Move

Do not start by adding more new content.

Start with a deliberate red-team review of the full V2 authoring guide set.

Review these docs together as one guide system:

1. `docs/user/test-of-detail-authoring.md`
2. `docs/user/v2-test-authoring/README.md`
3. `docs/user/v2-test-authoring/authoring-progression.md`
4. `docs/user/v2-test-authoring/advanced-authoring-patterns.md`
5. `docs/user/v2-test-authoring/authoring-examples-index.md`
6. `docs/user/v2-test-authoring/evaluation-input-patterns.md`
7. `docs/user/v2-test-authoring/scaffold.md`
8. `docs/user/v2-test-authoring/fact-extraction.md`
9. `docs/user/v2-test-authoring/fact-establishment-patterns.md`

Run that review against these questions:

1. redundancy
   - are the same ideas now explained too many times?
   - should any wording be trimmed because another page now teaches it better?
2. navigation
   - does a beginner know where to go next at each stage?
   - does an advanced author know when to leave the progression and use the advanced page?
3. teaching transitions
   - are there any jumps where the docs still assume too much?
   - are there any places where the reader is told what to do but not why?
4. example sufficiency
   - are the current four advanced worked examples enough?
   - if not, is the gap truly worth another canonical fixture?

The recommended outcome of tomorrow’s first move is:

- produce a short red-team findings list
- then patch the docs directly to fix the highest-signal redundancy or navigation issues

Do not reopen the V2 input/output contract unless the review reveals a real contradiction.

Do not start a new workstream unless the review reveals a gap large enough to justify it.

## Guardrails

- do not quietly drift back to “code organization first” as the middle-stage teaching model
- do not invalidate the value of the hardcoded starter path
- do not imply that production-grade authoring is required for a first successful test
- do not overplan later tutorial sections before the new backbone exists

## Next Useful Outputs

- a decision on whether the current four worked examples are sufficient or whether one more advanced pattern is still worth adding
- any targeted cross-link or redundancy cleanup revealed by that assessment
- only if needed, a narrower refinement pass on the V2 authoring guide set
