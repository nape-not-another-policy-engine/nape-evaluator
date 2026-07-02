# V2 Test Authoring

This folder contains the detailed guide set for the current V2 test-of-detail contract.

Start with:

- `docs/user/test-of-detail-authoring.md`

Use these current docs first:

- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-policy-direction.md`

Use the archived proposals only if you want the deeper historical design rationale behind the selected V2 shape:

- `docs/zzz-archive/product/v2-structured-verification-input-proposal.md`
- `docs/zzz-archive/product/v2-structured-verification-result-proposal.md`

## How To Use This Folder

Use the docs in this folder in the way that matches your current need:

- if you are new and want the hand-held path, start with [Authoring Progression](authoring-progression.md)
- if you already know the contract and want a fixture to copy, start with [Authoring Examples Index](authoring-examples-index.md)
- if you want the recommended internal Python structure, start with [Scaffold Guide](scaffold.md)
- if you need help choosing `subject` / `criteria` shapes, start with [Evaluation Input Patterns](evaluation-input-patterns.md)
- if your test has outgrown one-subject or one-pattern logic, start with [Advanced Authoring Patterns](advanced-authoring-patterns.md)

## Reading Order

1. [Overview](overview.md)
2. [Authoring Progression](authoring-progression.md)
3. [Scaffold Guide](scaffold.md)
4. [Fact Extraction](fact-extraction.md)
5. [Fact Establishment Patterns](fact-establishment-patterns.md)
6. [Evaluation Input Patterns](evaluation-input-patterns.md)
7. [Authoring Examples Index](authoring-examples-index.md)
8. [Advanced Authoring Patterns](advanced-authoring-patterns.md)
9. [Domain Examples](domain-examples.md)

## Included Template

Use the scaffold template here as a starting point:

- [templates/v2_test_of_detail_scaffold.py](templates/v2_test_of_detail_scaffold.py)
