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

## Smoke Test V1 Behavior

From the repository root:

```bash
python main.py --check-install
cd test
./author_test.sh
```

The author example is the committed V1 baseline smoke. It expects V1 text-line evidence behavior and should print JSON with `outcome` and `reason` when run against committed V1 code.

Current worktree caveat:

- The repository may contain uncommitted V2 typed-evidence WIP.
- That WIP changes `main.py` so JSON evidence is parsed before `evaluate(...)` is called.
- In that dirty worktree, `./author_test.sh` can return JSON `error` because the V1 test file still expects text lines.

For the observed V2 candidate WIP, the current companion smoke is:

```bash
cd test
./author_test_2.sh
```

At the time of this documentation pass, that command returns `inconclusive` because the dirty `test/author_verification.json` fixture has an empty `status` value.

Do not treat either smoke result as final V2 behavior until the code/WIP boundary is settled.

## Documentation Verification

When updating docs, verify:

```bash
rg -n "typed evidence|V2 candidate|V1" README.md docs
rg -n "nape-eval --check-install|--evidence|--test" README.md docs
git diff --check -- README.md docs .gitignore
```

## Deferred Hardening Items

The current docs pass intentionally does not change evaluator code. Track these before accepting V2 typed-evidence behavior:

- Move runtime imports such as `PyYAML` and `PyPDF2` into project runtime dependencies if typed loading is accepted.
- Decide whether `--check-install` should validate optional typed-loader dependencies or only prove the CLI starts.
- Add an executable `make docs-smoke` target after the code/WIP boundary is settled. It should be local-only and fixture-based.
- Decide whether JSON `error` output should still exit zero or should produce non-zero process status for fatal evaluator failures.
- Decide whether V2 preserves a raw text-lines compatibility mode.

## Generated Files

Do not commit Python cache files:

```text
__pycache__/
*.pyc
```

These are ignored by `.gitignore`.

## Dirty Worktree Awareness

This repository currently has staged and unstaged WIP. Do not revert or overwrite it during documentation work.
