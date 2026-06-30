# NAPE Evaluator

The NAPE Evaluator (`nape-eval`) applies a test-of-detail Python file to one evidence file and prints a JSON result. It is the evaluator process invoked by the NAPE CLI during `nape collect report`.

## Current Contract

`nape-eval` evaluates one evidence file with one test file:

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

Expected stdout:

```json
{"outcome": "pass", "reason": "The author has achieved the status of complete."}
```

The current evaluator loads evidence by file extension before calling `evaluate(evidence)`:

- `.json`: parsed JSON object
- `.xml`: XML root element
- `.yaml`, `.yml`: parsed YAML object
- `.pdf`: extracted text lines
- `.txt` and unknown extensions: text lines

This is a breaking change from the historical V1 contract, which passed raw text lines for every evidence file. The V1 baseline remains documented in `docs/product/v1-evaluator-baseline.md`.

## Start Here

- New users: [Installation](docs/user/installation.md), then [Quickstart](docs/user/quickstart.md)
- Test authors: [Test-of-detail authoring](docs/user/test-of-detail-authoring.md)
- CLI reference: [CLI reference](docs/user/cli-reference.md)
- Contract details: [Evaluator contract](docs/reference/evaluator-contract.md)
- Evidence formats: [Evidence formats](docs/reference/evidence-formats.md)
- Maintainers: [Architecture](docs/maintainers/architecture.md), then [Local development](docs/maintainers/local-development.md)
- Historical baseline and traceability: [V1 evaluator baseline](docs/product/v1-evaluator-baseline.md) and [source traceability](docs/reference/source-traceability.md)

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
