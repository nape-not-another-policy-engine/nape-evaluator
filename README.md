# NAPE Evaluator

The NAPE Evaluator (`nape-eval`) applies one or more test-of-detail Python files to one evidence file and prints a JSON result object. It is the evaluator process invoked by the NAPE CLI during `nape collect report`.

## Current Contract

`nape-eval` evaluates one evidence file with one or more test files:

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

It can also pair each repeated `--test` with an optional repeated `--test-parameters-file` in the same order:

```bash
nape-eval \
  --evidence ./sonar_metrics.json \
  --test ./code_cover_80.py \
  --test-parameters-file ./code_cover_80.parameters.json
```

Expected stdout:

```json
{
  "results": [
    {
      "test": "./verify_author_complete.py",
      "evidence_file": "./author_verification.json",
      "test_parameters": {},
      "executed": true,
      "outcome": "pass",
      "reason": "The author has achieved the status of complete.",
      "test_parameters_source": null
    }
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 1,
      "ran": 1,
      "pass": 1,
      "fail": 0,
      "inconclusive": 0,
      "error": 0,
      "message_count": 0,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 0
    }
  }
}
```

The current evaluator loads evidence by file extension before calling `evaluate(evidence, test_parameters, metadata)`:

- `.json`: parsed JSON object
- `.xml`: XML root element
- `.yaml`, `.yml`: parsed YAML object
- `.pdf`: extracted text lines
- `.txt` and unknown extensions: text lines

This is a breaking change from the historical V1 contract, which passed raw text lines for every evidence file. The V1 baseline remains documented in `docs/product/v1-evaluator-baseline.md`.

The current metadata contract is intentionally small:

- `metadata["evidence_type"]`
- `metadata["schema_version"]`

The current test-parameter contract is also intentionally small:

- `test_parameters` is always a dict at the test call boundary
- if no parameter file is supplied, `test_parameters` is `{}` at runtime
- when a parameter file is supplied, it must decode to a top-level JSON object

Per-test results include:

- `test`
- `evidence_file`
- `test_parameters`
- `test_parameters_source`
- `executed`
- `outcome`
- `reason`

Evaluator messages include `test_parameters_source`, which is either the supplied parameter-file path or `null`.

Result and evaluator failures are reported separately:

- `results[*].executed == true` means the test function completed
- `results[*].executed == false` means the requested invocation was blocked before the test completed
- `results[*].outcome == "error"` with `executed == true` means a test ran and returned an `error` outcome
- `evaluator.messages[*].level == "error"` means the evaluator/runtime hit an operational failure
- if `evaluator.summary.ran` is less than `evaluator.summary.count`, one or more requested tests were blocked before completing execution

Unsupported returned outcomes are treated as test contract errors:

- the test still counts in `evaluator.summary.ran`
- the result is normalized to `results[*].outcome == "error"`
- the reason explains that the test returned an unsupported outcome value

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
