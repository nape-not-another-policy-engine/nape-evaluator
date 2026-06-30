# Installation

`nape-eval` is installed from the Python package named `nape`.

## Install From PyPI

```bash
python3 -m pip install nape
```

Verify:

```bash
nape-eval --check-install
```

Expected output:

```text
NAPE Evaluator CLI is installed and working.
```

## PATH Notes

If `nape-eval` is not found after installation, confirm where Python installs console scripts.

Common user-local locations:

```text
$HOME/.local/bin
$HOME/Library/Python/<version>/bin
```

Add the relevant directory to `PATH`.

## Local Development Install

From the repository root:

```bash
python3 -m pip install .
nape-eval --check-install
```

For a clean reinstall:

```bash
python3 -m pip uninstall -y nape
python3 -m pip install .
```

## Version Notes

Committed V1 package metadata reports version `1.0.0`.

The current worktree may contain uncommitted V2 candidate metadata, including a `2.0.0` version change. Treat that as unreleased until reviewed and committed.

## Troubleshooting

**`nape-eval: command not found`**

The Python scripts directory is not on `PATH`, or the package is not installed in the active Python environment.

**`ModuleNotFoundError` from a test file**

The test-of-detail file imported a dependency that is not installed in the environment running `nape-eval`.

**NAPE CLI report generation fails before evaluating actions**

Run:

```bash
nape-eval --check-install
```

NAPE CLI calls this check before action evaluation.
