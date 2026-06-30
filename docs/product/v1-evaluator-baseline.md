# V1 Evaluator Baseline

This document records committed V1 behavior for V2 evaluator planning.

## Baseline Scope

The V1 baseline is derived from committed files:

- `main.py` at `HEAD`
- `pyproject.toml` at `HEAD`
- `test/author_test.sh`
- `test/verify_author_complete.py`
- `test/author_verification.json`

Current uncommitted changes are treated as V2 candidate behavior, not the V1 baseline.

## V1 CLI Workflow

Check install:

```bash
nape-eval --check-install
```

Evaluate evidence:

```bash
nape-eval --evidence ./author_verification.json --test ./verify_author_complete.py
```

`--evidence` and `--test` must be supplied together.

## V1 Evidence Contract

Committed V1 reads the evidence file with:

```python
with open(args.evidence, "r") as f:
    text = f.readlines()
```

The test file receives a list of strings:

```python
outcome, reason = action_module.evaluate(text)
```

In V1, test-of-detail authors are responsible for parsing structured evidence, such as JSON, from those text lines.

## V1 Test-Of-Detail Contract

A test file must define:

```python
def evaluate(evidence_file):
    return "pass", "Reason text"
```

The function must return a two-item tuple:

- `outcome`
- `reason`

The evaluator does not validate the outcome vocabulary before printing JSON.

## V1 Output Contract

Successful evaluation prints JSON to stdout:

```json
{"outcome": "pass", "reason": "Reason text"}
```

NAPE CLI expects evaluator stdout to be valid JSON with:

- `outcome`
- `reason`

## V1 Error Behavior

The committed evaluator catches failures and prints JSON with `outcome: "error"`.

| Failure | V1 behavior |
| --- | --- |
| Missing evidence or test file | Prints JSON `error` with an "Unable to find" reason. |
| Import failure | Prints JSON `error` with a "Failed to import" reason. |
| Other exception | Prints JSON `error` with a "Failed to execute" reason. |

The evaluator does not explicitly set a non-zero exit status when it catches these errors.

## V1 Package Baseline

Package metadata at `HEAD`:

- package name: `nape`
- version: `1.0.0`
- console script: `nape-eval = "main:main"`
- Python requirement: `>=3.0`
- build requirements: `setuptools`, `wheel`, `twine`

## V2 Planning Inputs

V2 should explicitly decide:

- Whether to preserve text-line evidence input compatibility.
- Whether typed evidence loading is accepted.
- How test authors discover the type passed into `evaluate(evidence)`.
- Whether output outcomes are validated before printing JSON.
- Whether caught evaluator errors should exit zero or non-zero.
- Whether missing files and import failures should be reportable action errors or fatal process failures.
- Where runtime dependencies such as `PyYAML` and `PyPDF2` should be declared if typed loading is accepted.
- What trust model applies to dynamically imported test-of-detail files.
- Whether the evaluator needs a formal sandbox or only trusted-code documentation.

## V1 To V2 Compatibility Matrix

| Area | V1 baseline | V2 candidate or decision pressure | Breaking impact | Recommendation | Status |
| --- | --- | --- | --- | --- | --- |
| Evidence input shape | `evaluate(evidence)` receives text lines from `readlines()`. | Candidate typed loader passes parsed objects for JSON/XML/YAML/PDF and text lines for TXT/unknown. | High: existing V1 tests that parse text lines can fail when receiving dicts or XML objects. | Preserve a raw text-lines mode or provide explicit migration guidance. | Pending V2 decision. |
| Supported file types | File extension is ignored; every evidence file is opened as text. | Candidate behavior branches on `.txt`, `.json`, `.xml`, `.yaml`, `.yml`, `.pdf`, and unknown extensions. | High: behavior changes based on filename extension. | Define supported extensions and fallback behavior as a formal contract. | Pending V2 decision. |
| Runtime dependencies | V1 requires only the standard library at runtime. | Candidate behavior imports `yaml` and `PyPDF2`. | Medium: users may install a package that starts but fails for typed loaders if runtime dependencies are missing. | Declare accepted typed-loader libraries as project runtime dependencies, not only build requirements. | Pending package metadata fix. |
| `--check-install` | Prints a health message if the CLI starts. | Typed loaders may introduce optional or required runtime dependencies. | Medium: install check could pass while YAML/PDF evaluation later fails. | Decide whether install check validates all enabled loaders or only the base CLI. | Pending V2 decision. |
| Outcome validation | V1 prints whatever `evaluate(...)` returns as `outcome`. | V2 may validate expected NAPE outcomes before printing JSON. | Medium: invalid custom outcomes could become errors. | Validate against `pass`, `fail`, `inconclusive`, and `error`, or document that validation remains caller-owned. | Pending V2 decision. |
| Failure and exit status | V1 catches failures, prints JSON `error`, and does not explicitly set non-zero exit status. | V2 may distinguish action-level errors from fatal process failures. | Medium: NAPE CLI and scripts may rely on stdout JSON rather than exit status. | Define when failures are JSON `error` versus non-zero process exits. | Pending V2 decision. |
| Dynamic test execution | V1 dynamically imports and executes trusted Python test files. | V2 may keep trusted-code execution or introduce sandboxing restrictions. | Medium: sandboxing can break existing tests that import libraries or access local resources. | Document trusted-code execution for now; evaluate sandbox needs separately. | Pending security decision. |
| Package version | V1 package metadata is `1.0.0`. | Dirty candidate metadata changes version to `2.0.0`. | Low to medium: version bump communicates breaking change if accepted. | Use a major version bump only when the typed-evidence contract is finalized. | Pending release decision. |
| Docs smoke fixtures | V1 has manual examples but no executable docs smoke target. | V2 should validate examples across accepted evidence formats. | Low: docs can drift without executable checks. | Add local-only `make docs-smoke` after V1/V2 behavior is settled. | Planned follow-up. |
