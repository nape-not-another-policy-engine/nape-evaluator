# NAPE Evaluator

The NAPE Evaluator (`nape-eval`) applies a test-of-detail Python file to one evidence file and prints a JSON result. It is the evaluator process invoked by the NAPE CLI during `nape collect report`.

## Current Contract

V1 evaluates one evidence file with one test file:

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

Expected stdout:

```json
{"outcome": "pass", "reason": "The author has achieved the status of complete."}
```

The committed V1 behavior reads evidence as text lines and passes those lines into the test file's `evaluate(evidence)` function. Typed evidence loading for JSON, XML, YAML, PDF, and text exists as V2 candidate work in the current worktree and should not be treated as released behavior until reviewed.

## Start Here

- New users: [Installation](docs/user/installation.md), then [Quickstart](docs/user/quickstart.md)
- Test authors: [Test-of-detail authoring](docs/user/test-of-detail-authoring.md)
- CLI reference: [CLI reference](docs/user/cli-reference.md)
- Contract details: [Evaluator contract](docs/reference/evaluator-contract.md)
- Evidence formats: [Evidence formats](docs/reference/evidence-formats.md)
- Maintainers: [Architecture](docs/maintainers/architecture.md), then [Local development](docs/maintainers/local-development.md)
- V2 planning: [V1 evaluator baseline](docs/product/v1-evaluator-baseline.md) and [source traceability](docs/reference/source-traceability.md)

## Install

The public install path is PyPI:

```bash
python3 -m pip install nape
nape-eval --check-install
```

Expected check output:

```text
NAPE Evaluator CLI is installed and working.
```
