# Local Development

## Install Locally

```bash
python3 -m pip install .
nape-eval --check-install
```

Uninstall:

```bash
python3 -m pip uninstall -y nape
```

## Build Release Artifacts

```bash
make build-release
```

Artifacts are written under:

```text
build-output/dist
```

## Install Built Wheel

```bash
make pip-install
```

## Publish

```bash
PYPI_URL=<repository-url> make pypi-publish
```

## Smoke Test Current Behavior

From the repository root:

```bash
python main.py --check-install
make docs-smoke
```

If you want to run the current JSON path manually:

```bash
cd tests/manual
bash ./author_test_2.sh
```

That command currently returns `inconclusive` because `tests/json/evidence/author_verification_empty_status.json` contains an empty `status` value.

## Historical Comparison Smoke

The older V1-style smoke remains available only for historical comparison:

```bash
cd tests/v1_baseline
bash ./author_test.sh
```

That older test expects text-line JSON parsing and is not compatible with the current V2 transport and result contract.

## Automated Tests

Run:

```bash
python -m unittest
```

This covers:

- install check
- no-argument zero-exit JSON error behavior
- `--check-install` exclusivity with evaluation arguments
- CLI contract behavior through subprocess tests
- direct CLI adapter behavior through unit tests
- request-builder validation
- JSON true-result behavior
- JSON inconclusive behavior
- invalid JSON loader errors
- JSON, YAML, XML, TXT, and unknown-extension loader behavior

The current test ownership split is:

- `tests/test_cli_contract.py`: end-to-end CLI contract via `main.py`
- `tests/test_cli_adapter.py`: parser and transport behavior in `src/nape_evaluator/application/io/cli.py`
- `tests/test_request_builder.py`: request-builder validation
- `tests/test_evaluator_use_case.py`: orchestration behavior
- `tests/test_evidence_gateway_routing.py`: loader routing and metadata behavior
- `tests/test_text_evidence_loading.py`: text loading and text fallback behavior
- `tests/test_structured_evidence_loading.py`: JSON, XML, and YAML behavior
- `tests/test_pdf_evidence_loading.py`: PDF behavior
- `tests/test_unprocessable_evidence.py`: blocked binary-format behavior
- `tests/test_test_execution.py`: test-of-detail gateway implementation behavior
- `tests/test_output_contract.py`: output shaping behavior

## Documentation Verification

When updating docs, verify:

```bash
make docs-smoke
rg -n "V1 baseline|historical" README.md docs
rg -n "nape-eval --check-install|--evidence|--invoke|--request-file" README.md docs
git diff --check -- README.md docs .gitignore
```

## Generated Files

Do not commit Python cache files:

```text
__pycache__/
*.pyc
```

These are ignored by `.gitignore`.

## Historical Note

`docs/product/v1-evaluator-baseline.md` remains the source for the old all-text contract if you need to compare behavior or plan migrations.

Current product-level direction is recorded in:

- `docs/product/current-evaluator-reference.md`
- `docs/product/v2-policy-direction.md`
