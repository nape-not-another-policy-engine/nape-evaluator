# NAPE Evaluator

The NAPE Evaluator (`nape-eval`) applies one or more trusted Python test-of-detail files to one evidence file and prints a structured JSON result object. It is the evaluator process invoked by the NAPE CLI during `nape collect report`.

## Current Contract

`nape-eval` evaluates one evidence file with one or more requested test invocations.

Direct mode:

```bash
nape-eval \
  --evidence ./author_verification.json \
  --invoke '{"test":"./verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}'
```

Full-request mode:

```bash
nape-eval --request-file ./request.json
cat request.json | nape-eval --request-file -
```

Expected stdout shape:

```json
{
  "results": [
    {
      "test": "./verify_author_complete.py",
      "evidence": "./author_verification.json",
      "evaluations": [
        {
          "subject": {
            "name": "status",
            "data_type": "text"
          },
          "criteria": {
            "equals": "complete"
          }
        }
      ],
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "true",
        "facts": [
          {
            "name": "status",
            "value": "complete",
            "value_type": "text",
            "status": "found"
          }
        ],
        "reason": "The author has achieved the expected status."
      }
    }
  ],
  "evaluator": {
    "messages": [],
    "summary": {
      "count": 1,
      "ran": 1,
      "true": 1,
      "false": 0,
      "inconclusive": 0,
      "message_count": 0,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 0
    }
  }
}
```

The current evaluator loads evidence by file extension before calling `evaluate(evidence, evaluations, metadata)`:

- `.json`: parsed JSON object
- `.xml`: XML root element
- `.yaml`, `.yml`: parsed YAML object
- `.pdf`: extracted text lines
- `.txt` and unknown extensions: text lines

The current metadata contract is intentionally small:

- `metadata["evidence_type"]`
- `metadata["schema_version"]`

The current caller-owned input contract is:

- top-level request uses `evidence` plus `tests`
- each requested test packet uses `test` plus `evaluations`
- each evaluation item uses `subject` plus `criteria`

Per-test results include:

- `test`
- `evidence`
- `evaluations`
- `execution`
- `result`

Result and evaluator failures are reported separately:

- `results[*].execution.executed == true` means the test function completed
- `results[*].execution.executed == false` means the requested invocation was blocked before the test completed
- blocked invocations still carry structured `results[*].result.conclusion == "inconclusive"` with evaluator-owned blocked reasoning
- `evaluator.messages[*].level == "error"` means the evaluator/runtime hit an operational failure
- if `evaluator.summary.ran` is less than `evaluator.summary.count`, one or more requested tests were blocked before completing execution

Invalid completed-test result contracts are treated as completed test contract errors:

- the test still counts in `evaluator.summary.ran`
- the result is normalized to `result.conclusion == "inconclusive"`
- the reason explains that the test returned an invalid result contract

## Start Here

- New users: [Installation](docs/user/installation.md), then [Quickstart](docs/user/quickstart.md)
- Migrating older usage: [V1 to V2 migration](docs/user/v1-to-v2-migration.md)
- Test authors: [Test-of-detail authoring](docs/user/test-of-detail-authoring.md), then [V2 test authoring](docs/user/v2-test-authoring/README.md)
- Software integrators: [Software integration guide](docs/user/software-integration/README.md)
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
