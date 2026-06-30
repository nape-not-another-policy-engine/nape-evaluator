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
cd test
./author_test.sh
```

The current manual JSON smoke example is:

```bash
cd test
./author_test_2.sh
```

That command currently returns `inconclusive` because `test/author_verification.json` contains an empty `status` value.

The older V1-style smoke remains available for historical comparison:

```bash
cd test
./author_test.sh
```

That older test expects text-line JSON parsing and is not compatible with the current typed JSON contract.

## Automated Tests

Run:

```bash
python -m unittest
```

This covers:

- install check
- JSON CLI pass behavior
- JSON inconclusive behavior
- invalid JSON loader errors
- JSON, YAML, XML, TXT, and unknown-extension loader behavior

## Documentation Verification

When updating docs, verify:

```bash
rg -n "typed evidence|V1 baseline|historical" README.md docs
rg -n "nape-eval --check-install|--evidence|--test" README.md docs
git diff --check -- README.md docs .gitignore
```

## Deferred Hardening Items

- Add an executable `make docs-smoke` target for the documented examples. It should be local-only and fixture-based.
- Decide whether JSON `error` output should still exit zero or should produce non-zero process status for fatal evaluator failures.
- Decide whether the evaluator should validate `outcome` values before printing JSON.
- Decide whether a raw text-lines compatibility mode is still needed for migrated V1 tests.

## Generated Files

Do not commit Python cache files:

```text
__pycache__/
*.pyc
```

These are ignored by `.gitignore`.

## Historical Note

`docs/product/v1-evaluator-baseline.md` remains the source for the old all-text contract if you need to compare behavior or plan migrations.
