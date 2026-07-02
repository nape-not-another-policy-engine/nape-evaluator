# User Documentation

Use this folder when installing `nape-eval`, running it directly, writing test-of-detail files, or integrating the evaluator into other software.

## Reading Order

1. [Installation](installation.md)
2. [Quickstart](quickstart.md)
3. [CLI reference](cli-reference.md)
4. [Test-of-detail authoring](test-of-detail-authoring.md)
5. [V2 test authoring](v2-test-authoring/README.md)
6. [Software integration](software-integration/README.md)

## Current Behavior Note

These docs describe the current committed V2 evaluator contract.

Historical V1 material remains available in `../product/v1-evaluator-baseline.md` for migration review only.

## V2 Authoring Guide Note

The `v2-test-authoring/` subfolder is the detailed guide set for the current V2 authoring model.

Use it for scaffolds, fact extraction patterns, fact-establishment tradeoffs, and evaluation-input examples.

## Software Integration Guide Note

The `software-integration/` subfolder is the dedicated guide set for software that wraps `nape-evaluator` as a component.

Use it for:

- request packet construction
- subprocess invocation guidance
- response parsing and classification
- production hardening and worked wrapper examples
