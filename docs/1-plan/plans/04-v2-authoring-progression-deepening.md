# Plan 04: V2 Authoring Progression Deepening

## Goal

Turn the current V2 authoring progression into a true beginner-to-expert teaching path that starts with “get going quickly” and builds toward fully diagnosable, safe, input-driven test-of-detail authoring.

## Why This Is Its Own Plan

The current progression is directionally correct, but its middle stages mix two different concerns:

- code organization
- operational safety and diagnosability

That is acceptable as a rough outline, but it is not yet the clearest hand-held path for a reader who has no NAPE context.

This work is not just copy editing. It is teaching-model design.

## Baseline

Read first:

1. `docs/product/current-evaluator-reference.md`
2. `docs/user/test-of-detail-authoring.md`
3. `docs/user/v2-test-authoring/README.md`
4. `docs/user/v2-test-authoring/authoring-progression.md`
5. `docs/user/v2-test-authoring/authoring-examples-index.md`
6. `docs/user/v2-test-authoring/evaluation-input-patterns.md`
7. representative fixtures under `tests/json/test_of_detail/`

## Current State

Current strengths:

- the authoring docs already describe the V2 runtime boundary accurately
- the guide set already includes progression, examples, scaffold, fact extraction, fact-establishment guidance, and a pattern library
- the fixture library now spans starter, typed, structural, temporal, fail-fast, and fail-slow examples

Current gap:

- the early progression is now much stronger, but the later stages still need the same level of tutorial precision
- `Stage 4` through `Stage 6` are still lighter than the earlier sections
- the document still needs a clear decision on how much later-stage depth belongs inline versus in companion pages

## Core Teaching Direction

The progression should teach in this order:

1. get a result quickly
2. externalize one rule into `evaluations`
3. guard the execution contract
4. establish facts explicitly
5. choose failure strategy
6. refactor into helpers
7. scale up to richer typed and multi-subject logic

This means the earlier draft’s “separate into helpers” move should no longer lead the middle of the story.

The safer and clearer ordering is:

- first explain what can go wrong
- then explain how to make those failure points explicit
- then explain how to structure helpers around those explicit responsibilities

## Scope

In scope:

- restructuring the authoring progression’s teaching order
- deepening the progression into a more tutorial-style document
- using the fixture library as supporting examples where useful
- planning the deepening work incrementally rather than all at once

Out of scope:

- redesigning the current V2 runtime contract
- changing the bounded first-pass criteria surface
- rewriting the entire V2 authoring guide set in one pass without section-level checkpoints

## Planning Strategy

This plan is intentionally a “plan to plan” after the first layer.

Reason:

- the first deepening pass should validate the teaching sequence before the later stages are locked down
- later sections should be planned in more detail after the earlier sections are rewritten and reviewed
- this keeps the tutorial logic honest instead of freezing too much structure up front

Applied rule:

- plan the document architecture and the first major rewrite section now
- after that section is complete, plan the next section at higher precision
- continue section by section until the progression reaches the intended end state

## Section Model

The target document should likely move from “stages only” to “stages plus teaching scaffolding.”

Each stage should eventually include:

- goal
- what the reader can ignore for now
- what can go wrong
- example input
- example code
- example output
- why this stage is not enough yet
- what the next stage adds

That full shape is the end state, but not every stage needs to be fully planned before the first rewrite pass starts.

## Planned Workstreams

### Workstream A: Teaching Sequence Rewrite

Purpose:

- reorder the progression so the document follows the beginner learning path rather than the internal code-shape path

Initial target order:

1. hardcoded starter
2. one caller-driven rule
3. defensive validation
4. fact establishment
5. fail-fast versus fail-slow choice
6. helper decomposition
7. richer multi-subject and typed logic

This workstream should be planned in detail now.

### Workstream B: Stage Deepening

Purpose:

- expand each stage into a tutorial section with examples, failure modes, and transition logic

This workstream should only be partially planned now.

Detailed planning for later stage groups should happen after Workstream A is complete.

### Workstream C: Example Binding

Purpose:

- decide where the progression should point to live fixtures versus inline minimal examples

This should be planned lightly now and refined after the rewritten stage sequence exists.

## Detailed Plan For The First Rewrite Section

### Section 1: Reframe The Progression Backbone

Deliverable:

- update `docs/user/v2-test-authoring/authoring-progression.md` so the stage order and document framing follow the selected beginner-to-expert teaching path

Required outcomes:

- the document explicitly frames itself as a path from “working quickly” to “fully diagnosable and safe”
- helper decomposition no longer appears before defensive validation, fact establishment, and failure-strategy choice
- the distinction between:
  - quick-start authoring
  - production-grade authoring
  is explicit
- the reader can see why each stage exists and why it comes in that order

Minimum content to land in this section:

- revised stage order
- stronger intro and framing
- one-sentence rationale for each stage
- a clear statement that later stages harden, not invalidate, earlier ones

What does not need to be fully solved in this section:

- the exact final example density for every stage
- the final split between inline code and cross-links to fixtures
- whether later stages should be split into sub-stages or appendices

## What Needs More Planning Later

After Section 1 is done, the next planning pass should determine:

1. how much example depth each stage should have
2. whether stages should be grouped into:
   - quick start
   - hardening
   - scaling up
3. how much output-example material should appear inline versus linked
4. whether fail-fast and fail-slow should stay in one stage or split into:
   - choosing a strategy
   - implementing the strategy
5. how strongly the progression should point into the fixture index and pattern library

## Second Planning Slice

This next planning slice intentionally covers only:

- the standard per-stage template
- `Stage 0` through `Stage 3`
- the broad grouping model for the later sections

It does not fully plan the later tutorial sections yet.

Reason:

- the early stages carry most of the beginner teaching burden
- the later sections can be planned more accurately once the early-stage teaching shape is settled

## Selected Per-Stage Template

The deepened progression should use one standard template for the earlier stages.

Recommended stage template:

1. goal
2. what you are doing here
3. what you can ignore for now
4. example input
5. example code
6. example output
7. what can go wrong
8. why this stage is not enough yet
9. what the next stage adds

Notes:

- not every later stage must use every heading with the same depth
- `Stage 0` through `Stage 3` should use this template most fully
- later stages can compress some sections when repetition would add little value

## Selected Example-Depth Strategy

### Early Stages

The early stages should be deeper than the later stages.

Selected depth:

- `Stage 0`
  - one inline evidence snippet
  - one inline minimal test
  - one compact inline output example
- `Stage 1`
  - one inline `evaluations` example
  - one inline updated test snippet
  - one compact illustration that changing input changes result
- `Stage 2`
  - one inline defensive-validation example
  - one compact returned `error` example
- `Stage 3`
  - one inline fact-shape example
  - one `not_found` fact example
  - one `invalid` fact example
  - one compact returned `inconclusive` example

## Grouping Decision

The grouped teaching parts should be visible in the tutorial itself, not just implicit in planning notes.

Selected visible section headers:

- Part 1: Get Working Quickly
- Part 2: Make It Safe And Diagnosable
- Part 3: Make It Maintainable And Scalable

Reason:

- the grouped parts help a new reader understand why the stages are clustered the way they are
- they make the progression easier to scan without changing the stage-by-stage teaching path
- they reinforce that quick-start and production-grade concerns are both valid, but different

## Current Delivery State

The progression document now includes:

- the reordered beginner-to-expert backbone
- deeper `Stage 0` through `Stage 3` sections using the selected tutorial template
- visible grouped part headers matching the selected teaching model
- deeper `Stage 4` through `Stage 6` sections that keep the main tutorial narrative inline while pushing full detail to the existing scaffold, examples index, and pattern-library companion docs
- explicit early-stage Python-writing guidance:
  - a shared “write the Python as you go” section
  - stage-specific incremental Python-building guidance for `Stage 0` through `Stage 6`

The next planning slice should therefore move on to:

- whether the current guide set is now sufficient without a new advanced companion page
- whether any remaining cross-link or wording gaps still block the intended beginner-to-expert path

## Proposed Advanced Companion Page

Recommendation:

- add one focused advanced companion page
- do not split the progression into several later-stage documents
- do not create a page per stage

Proposed path:

- `docs/user/v2-test-authoring/advanced-authoring-patterns.md`

Proposed purpose:

- serve as the synthesis layer for authors who already understand the progression and now need to scale test-of-detail complexity safely

Why this page is justified:

- `authoring-progression.md` should remain the primary linear teaching path
- `authoring-examples-index.md` helps authors choose examples, but does not synthesize advanced design choices
- `evaluation-input-patterns.md` gives pattern vocabulary, but does not walk an author through scaling composition decisions
- `scaffold.md` gives code structure guidance, but does not explain advanced reasoning topology
- the advanced topics now named in the docs are broader than the progression should absorb inline without losing its onboarding role

## Proposed Page Role Relative To Existing Docs

### `authoring-progression.md`

Role:

- primary start-to-finish teaching path

Should link to the advanced page:

- near the end of `Stage 6`
- in `Where To Go Next`

Reader question it answers:

- “How do I get from starter authoring to advanced authoring?”

### `authoring-examples-index.md`

Role:

- example and fixture selection surface

Should link to the advanced page:

- in the advanced fixture area
- in any future “advanced copy paths” section

Reader question it answers:

- “Which executable example should I copy next?”

### `evaluation-input-patterns.md`

Role:

- caller-owned input pattern vocabulary

Should link to the advanced page:

- where decision topology grows beyond direct compare and simple conjunction

Reader question it answers:

- “What shape of `subject` / `criteria` input should I use?”

### `scaffold.md`

Role:

- internal file organization and helper breakout guidance

Should link to the advanced page:

- if advanced authoring needs a note about when the default scaffold is no longer enough on its own

Reader question it answers:

- “How should I structure the Python file?”

## Proposed Section Outline

### 1. Purpose And Audience

What it should say:

- this page is for authors who already understand the progression and now need to scale beyond simple one-subject or one-pattern tests
- this is not a replacement for the progression

Primary links:

- `authoring-progression.md`
- `authoring-examples-index.md`

### 2. When You Actually Need This Page

What it should say:

- use this page when your test has outgrown:
  - one fact
  - one simple criterion
  - one direct comparison
- typical triggers:
  - several subjects
  - typed plus structural facts in one test
  - derived facts
  - policy logic that branches internally

Primary links:

- `authoring-progression.md` `Stage 6`

### 3. Advanced Complexity Dimensions

What it should say:

- advanced authoring usually grows along a few dimensions:
  - fact topology
  - criteria richness
  - decision topology
  - establishment strategy
  - code organization pressure

Subsections should include:

- one fact versus several facts
- independent versus dependent versus derived facts
- direct compare versus conjunction versus internal conditional reasoning
- fail fast versus fail slow in multi-subject tests

Primary links:

- `evaluation-input-patterns.md`
- `fact-establishment-patterns.md`

### 4. Scaling Patterns In Recommended Order

What it should say:

- do not jump from a starter test straight to conditional-policy logic
- grow complexity in a controlled order

Recommended sequence:

1. richer criteria for one fact
2. typed parsing for one fact
3. structural comparisons
4. multiple subjects with direct conjunction
5. dependent or derived facts
6. internal conditional or tiered reasoning

Primary links:

- `authoring-examples-index.md`
- `evaluation-input-patterns.md`

### 5. Multi-Subject Test Design

What it should say:

- how to reason when one conclusion depends on several facts
- how to keep caller-owned criteria separate from test-owned logic
- how to avoid turning `evaluations` into a policy DSL

Topics:

- one combined result from several subjects
- why subject-level criteria still matter
- where the actual reasoning should live
- when to choose fail fast versus fail slow

Primary fixture links:

- `verify_dual_coverage_fail_fast.py`
- `verify_dual_coverage_thresholds.py`

### 6. Typed And Structural Fact Design

What it should say:

- how to think about typed parsing and structural equality as authoring responsibilities

Topics:

- date, datetime, duration, integer parsing
- array equality versus membership-like logic
- object equality versus field-by-field reasoning
- explicit null versus missing

Primary fixture links:

- `verify_last_review_timestamp_range.py`
- `verify_review_date_range.py`
- `verify_restore_duration_range.py`
- `verify_approver_profile_equals.py`
- `verify_reviewer_roles_equals.py`
- `verify_revocation_reason_null.py`

### 7. Derived Facts And Internal Reasoning Boundaries

What it should say:

- some tests need facts that are not present directly in evidence
- explain derived facts without implying evaluator-owned business logic

Topics:

- compute inside the Python test
- keep derived fact names explicit
- keep reasoning readable
- avoid hiding policy inside parsing helpers

Primary links:

- `scaffold.md`
- `evaluation-input-patterns.md`

### 8. Anti-Patterns

What it should say:

- common ways advanced authoring becomes unreadable or misleading

Anti-patterns to cover:

- overloading `criteria` with policy logic
- encoding decision trees in transport
- mixing extraction and evaluation in the same helper
- creating too many vague helpers
- returning weak reasons from complex tests
- using advanced logic before basic fact discipline is solid

Primary links:

- `scaffold.md`
- `fact-establishment-patterns.md`

### 9. Decision Matrix: Which Guide To Use Next

What it should say:

- if you are choosing examples, go to the examples index
- if you are choosing input shape, go to the pattern library
- if you are reorganizing code, go to the scaffold
- if you are choosing failure strategy, go to fact-establishment patterns

Primary links:

- `authoring-examples-index.md`
- `evaluation-input-patterns.md`
- `scaffold.md`
- `fact-establishment-patterns.md`

### 10. Boundary Of Current Recommendation

What it should say:

- what is recommended now
- what is documented as later or future
- what should not yet be treated as a standard library pattern

Topics:

- current bounded first-pass patterns
- later conditional and tiered policy ideas
- avoiding accidental overcommitment in docs before runtime or product direction is settled

## Recommended First Draft Constraints

The first draft of the advanced page should:

- be synthesis-heavy, not code-dump-heavy
- use short focused examples, not full fixture copies
- link aggressively to executable fixtures instead of duplicating them
- make boundaries explicit between:
  - supported now
  - recommended now
  - possible later

The first draft should not:

- replace `Stage 6`
- re-explain all beginner material
- become a speculative future-design document

## Current Advanced-Page State

The first draft of:

- `docs/user/v2-test-authoring/advanced-authoring-patterns.md`

is now landed.

Current delivered scope:

- purpose and audience
- when the page is needed
- advanced complexity dimensions
- scaling order
- multi-subject test design
- typed and structural fact design
- derived fact boundaries
- anti-patterns
- decision matrix
- boundary of current recommendation
- worked examples for:
  - multi-subject conjunction
  - typed date comparison
  - structural object equality
  - derived numeric fact comparison

Current linked integration:

- `README.md` in the V2 authoring folder now includes the page in reading order
- `authoring-progression.md` now links to it from `Stage 6` and `Where To Go Next`
- `authoring-examples-index.md`, `evaluation-input-patterns.md`, and `scaffold.md` now route advanced readers toward it

The next planning slice should now focus on:

- whether the new page needs any additional worked examples beyond the four highest-value advanced patterns now included
- whether any companion docs now have redundant wording that should be tightened
- whether navigation between progression, advanced patterns, and examples index is now sufficient
- whether any other advanced pattern now justifies an executable canonical fixture beyond the derived-fact example already added

## Third Planning Slice

This planning slice covers only:

- `Stage 4`
- `Stage 5`
- `Stage 6`
- the inline-versus-linked depth rule for those later stages

It does not yet create new companion pages.

Reason:

- the repo already has companion material in:
  - `scaffold.md`
  - `authoring-examples-index.md`
  - `evaluation-input-patterns.md`
- the next useful move is to make the main progression sharper without turning it into a second scaffold or pattern reference

## Selected Later-Stage Teaching Goals

### Stage 4: Choose Fail Fast Or Fail Slow

Teaching goal:

- show that failure strategy is an authoring decision about diagnosability and control flow, not a runtime toggle

What this stage must teach clearly:

- both strategies still return `inconclusive` when required facts cannot be established
- the difference is:
  - when the test stops
  - how much fact context it returns
- authors should start fail fast unless they already know they need fuller diagnostics

Primary fixture bindings:

- `verify_dual_coverage_fail_fast.py`
- `verify_dual_coverage_thresholds.py`

Selected inline depth:

- one short side-by-side explanation of fail fast versus fail slow
- one compact inline fact-establishment contrast
- one compact inline `inconclusive` output example for each strategy
- no long duplicated full-file code blocks

Why this depth:

- the conceptual difference matters more than the full implementation listing
- the executable fixtures already carry the complete code examples

### Stage 5: Separate The Test Into Small Helpers

Teaching goal:

- show how clarified responsibilities become a maintainable internal layout

What this stage must teach clearly:

- helper decomposition is driven by responsibility boundaries already introduced in earlier stages
- the public contract stays:
  - `evaluate(evidence, evaluations, metadata)`
- helpers should separate:
  - metadata validation
  - evaluation indexing
  - fact extraction
  - fact establishment review
  - policy evaluation
  - result building

Primary reference bindings:

- `docs/user/v2-test-authoring/scaffold.md`
- `docs/user/v2-test-authoring/templates/v2_test_of_detail_scaffold.py`
- `verify_author_complete.py`
- `verify_review_date_range.py`

Selected inline depth:

- one compact helper map or skeleton
- one short explanation of why each helper exists
- no large embedded scaffold dump in the progression itself

Why this depth:

- duplicating the scaffold in the progression would make the tutorial noisy
- the progression should explain why the breakout exists, then point to the scaffold for the full default shape

### Stage 6: Scale Up To Richer Typed And Multi-Subject Logic

Teaching goal:

- show how an author grows from simple single-subject checks into richer typed and multi-subject tests without jumping straight into conditional-policy DSL thinking

What this stage must teach clearly:

- “scaling up” means adding one new dimension at a time:
  - richer criteria for one subject
  - typed parsing
  - explicit null, array, and object handling
  - multi-subject reasoning
- the caller still changes criteria without rewriting core test logic
- more complex reasoning still belongs in the Python test, not in the evaluator transport

Primary fixture bindings:

- `verify_component_coverage_range.py`
- `verify_build_age_days_range.py`
- `verify_last_review_timestamp_range.py`
- `verify_approver_profile_equals.py`
- `verify_reviewer_roles_equals.py`
- `verify_dual_coverage_thresholds.py`

Selected inline depth:

- one growth ladder from simple to richer examples
- one compact typed-versus-structural pattern table
- no full advanced policy code block in the progression

Why this depth:

- later-stage readers benefit more from navigational clarity than from another long embedded example
- the fixture library is now broad enough to do the heavy lifting

## Selected Later-Stage Output Strategy

The later stages should still show output inline, but only when the output clarifies a semantic distinction.

Selected rule:

- `Stage 4`
  - show compact `inconclusive` outputs for fail fast and fail slow
- `Stage 5`
  - output is optional; include only if needed to reinforce that helper decomposition does not change the returned contract
- `Stage 6`
  - prefer pattern and growth illustrations over more output JSON unless a specific typed distinction needs it

## Selected Inline Versus Linked Strategy For Later Stages

The later stages should be hybrid, but much more link-driven than `Stage 0` through `Stage 3`.

Selected rule by stage:

- `Stage 4`
  - explain inline
  - link to executable fixtures for full implementations
- `Stage 5`
  - explain inline
  - link strongly to `scaffold.md` and the scaffold template for full shape
- `Stage 6`
  - explain inline at the pattern-selection level
  - link strongly to `authoring-examples-index.md` and `evaluation-input-patterns.md`

Selected companion-page decision for now:

- do not create a new companion page yet
- first use the existing scaffold, examples index, and pattern library more deliberately from the progression

Rationale:

- the current guide set already has the right companion surfaces
- the main gap is orchestration between them, not missing pages

## Selected Rewrite Target For The Next Tutorial Pass

When the main progression is edited again, the next bounded rewrite should:

1. deepen `Stage 4` with fail-fast and fail-slow contrasts tied to the dual-coverage fixtures
2. deepen `Stage 5` with one compact helper skeleton and stronger scaffold cross-links
3. deepen `Stage 6` with a clearer growth ladder and stronger fixture-pattern cross-links

That rewrite should avoid:

- embedding large advanced code listings
- duplicating `scaffold.md`
- duplicating the examples index tables inside the progression

### Later Stages

The later stages should be lighter.

Selected depth:

- `Stage 4`
  - one fail-fast example
  - one fail-slow example
- `Stage 5`
  - mainly structure and helper breakout
- `Stage 6`
  - mainly scaling guidance plus fixture links

## Selected Output-Illustration Strategy

The progression should show output inline whenever the output teaches a semantic distinction.

Selected output rule:

- show compact inline result objects in the progression
- do not show full outer evaluator JSON packets unless a specific stage truly needs them

Required inline output distinctions in the early stages:

- `true`
- `false`
- `inconclusive`
- `error`

Selected style:

- progression doc:
  - compact result fragments
- reference docs and fixtures:
  - full contract detail

## Selected Inline-Versus-Fixture Strategy

Use a hybrid rule.

### `Stage 0` Through `Stage 3`

- embed small examples inline
- also link to one canonical fixture per stage

### `Stage 4` And Later

- summarize the concept inline
- use live fixtures as the primary concrete implementation reference

Rule of thumb:

- if the example is short and teaches a first-order concept, embed it inline
- if it is longer or mostly repeats a structure already taught, summarize it and link to the fixture

## Selected Stage-Group Model

Keep the stage numbers, but group them into broader sections.

Selected grouping:

### Part 1: Get Working Quickly

- `Stage 0`
- `Stage 1`

### Part 2: Make It Safe And Diagnosable

- `Stage 2`
- `Stage 3`
- `Stage 4`

### Part 3: Make It Maintainable And Scalable

- `Stage 5`
- `Stage 6`

This preserves:

- detailed step-by-step learning through numbered stages
- higher-level navigability through broader grouped parts

## Stage 0 Through Stage 3 Planning

### Stage 0: Hardcoded Starter Test

Purpose:

- normalize the simplest acceptable starting point

Required inline content:

- one small evidence snippet
- one minimal inline hardcoded test
- one compact `true` or `false` result example

Recommended fixture binding:

- primary live reference:
  - `tests/json/test_of_detail/verify_author_complete.py`
- note:
  - the fixture is more mature than the pure hardcoded starter, so the doc should present the inline example as the conceptual start and the fixture as the evolved real implementation

### Stage 1: Externalize One Rule Into `evaluations`

Purpose:

- show the first dynamic move from hardcoded logic to caller-owned input

Required inline content:

- one inline `evaluations` packet
- one updated test snippet
- one compact illustration that changing the input changes the result

Recommended fixture binding:

- primary live reference:
  - `tests/json/test_of_detail/verify_author_complete.py`
- secondary optional references:
  - `tests/json/test_of_detail/verify_component_coverage_minimum.py`

### Stage 2: Add Defensive Validation

Purpose:

- show how the test protects its own execution contract

Required inline content:

- one defensive-validation snippet
- one example of a test-level `error`
- one short explanation of the split between:
  - evaluator-owned validation
  - test-owned defensive validation

Recommended fixture binding:

- primary live references:
  - `tests/json/test_of_detail/verify_author_complete.py`
  - `tests/json/test_of_detail/verify_last_review_timestamp_minimum.py`
  - `tests/json/test_of_detail/verify_review_date_range.py`

### Stage 3: Add Fact Establishment Discipline

Purpose:

- show how the test distinguishes “can run” from “can decide”

Required inline content:

- one standard fact shape
- one `not_found` example
- one `invalid` example
- one compact `inconclusive` result example

Recommended fixture binding:

- primary live references:
  - `tests/json/test_of_detail/verify_review_date_range.py`
  - `tests/json/test_of_detail/verify_restore_duration_range.py`
  - `tests/json/test_of_detail/verify_service_owner_required.py`

## What Still Needs Later Planning

After these stage-level decisions are applied, the next planning pass should determine:

1. whether `Stage 4` should stay as one stage or split into strategy versus implementation
2. how much helper-detail `Stage 5` really needs inline
3. how much `Stage 6` should rely on the examples index versus the pattern library
4. whether the broad grouped parts should become actual visible headers in the document

## Immediate Recommendations

- do not try to fully blueprint every stage before the first rewrite pass
- first lock the teaching order
- then deepen the first few stages
- then plan the later stages with better precision once the new backbone is stable

## Exit Criteria For This Plan’s First Milestone

This plan’s first milestone is complete when:

- the progression’s teaching order is rewritten and stabilized
- the tutorial intent is explicit
- the next section-level planning questions are reduced to example depth and presentation detail rather than backbone uncertainty
