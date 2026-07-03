# Plan 14: Domain Example Pack Research And Mapping

## Purpose

Research high-risk assurance domains across industries and create a structured basis for future example packs.

This plan is not about changing the evaluator contract.

It is about choosing realistic example domains, evidence shapes, and test-of-detail patterns that match how assurance work actually appears in industry.

## Why This Exists

The repo now has:

- the selected V2 request and result model
- format-specific authoring guidance
- a first-wave and second-wave example library focused on extraction patterns

What it does not yet have is a sufficiently broad, realistic domain map showing:

- which industries are good anchors for examples
- which company types inside those industries are plausible users
- which high-risk assurance problems are common
- which evidence shapes and test-of-detail patterns map cleanly to those problems

## Research Goals

Build a domain map that covers:

- classic regulatory / compliance use cases
- high-risk operational assurance use cases
- IT / OT boundary cases
- fleet / transportation cases
- application and software verification cases
- system-of-systems cases
- health and safety-critical cases

## Output

The first-pass output should provide:

1. a vertical-by-vertical map
2. example company types inside each vertical
3. common high-risk assurance problems
4. candidate evidence sources
5. candidate `subject` examples
6. candidate test-of-detail example ideas
7. a recommendation for which domains should become:
   - starter examples
   - intermediate examples
   - advanced / systems examples

## Guardrails

- keep examples centered on verification of facts from evidence
- do not turn the transport into a policy language
- prefer examples that can be reduced to clear evidence plus one or more evaluations
- distinguish source-grounded sector concerns from recommended example-pack inferences

## Work Steps

1. create the active plan and handoff
2. research a spread of current sector references and standards/guidance anchors
3. expand `docs/user/v2-test-authoring/domain-examples.md` into a richer domain map
4. record recommended domain-pack sequencing for future implementation
5. closure-review whether the first-pass map is broad enough to guide example-pack construction
