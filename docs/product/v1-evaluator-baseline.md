# V1 Evaluator Baseline

This document records the historical V1 behavior that preceded the current typed-evidence evaluator.

## Baseline Scope

The V1 baseline is derived from committed files:

- `main.py` at `HEAD`
- `pyproject.toml` at `HEAD`
- `tests/v1_baseline/author_test.sh`
- `tests/v1_baseline/verify_author_complete.py`
- `tests/v1_baseline/author_verification.json`

Current committed behavior has moved beyond this baseline. Use this document for migration, compatibility review, and version-to-version comparison.

If you need the practical cutover steps rather than the raw historical baseline, use:

- `docs/user/v1-to-v2-migration.md`

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

| Area | V1 baseline | Current V2 behavior or decision pressure | Breaking impact | Recommendation | Status |
| --- | --- | --- | --- | --- | --- |
| Evidence input shape | `evaluate(evidence)` receives text lines from `readlines()`. | Current typed loader passes parsed objects for JSON/XML/YAML/PDF and text lines for TXT/unknown. | High: existing V1 tests that parse text lines can fail when receiving dicts or XML objects. | Keep typed evidence loading as the V2 contract and provide explicit migration guidance for older tests. | Migration guidance documented. |
| Supported file types | File extension is ignored; every evidence file is opened as text. | Current behavior branches on `.txt`, `.json`, `.xml`, `.yaml`, `.yml`, `.pdf`, and unknown extensions. | High: behavior changes based on filename extension. | Define supported extensions and fallback behavior as a formal contract. | Implemented, keep documented. |
| Runtime dependencies | V1 requires only the standard library at runtime. | Current behavior imports `yaml` and `PyPDF2`. | Medium: users may install a package that starts but fails for typed loaders if runtime dependencies are missing. | Declare accepted typed-loader libraries as project runtime dependencies, not only build requirements. | Implemented in package metadata. |
| `--check-install` | Prints a health message if the CLI starts. | Typed loaders introduce required runtime dependencies, but install check still validates base CLI startup rather than every loader path. | Medium: install check can pass while YAML/PDF evaluation later fails if packaging or environment setup is wrong. | Keep install check as a base CLI check, and verify loader support in clean install/release validation. | Direction chosen; release-process follow-up remains. |
| Outcome validation | V1 prints whatever `evaluate(...)` returns as `outcome`. | Current behavior validates expected NAPE outcomes before printing JSON and converts invalid values to result-level `error`. | Medium: invalid custom outcomes now become contract errors. | Keep invalid outcomes as result-level `error` while preserving `ran` accounting. | Implemented. |
| Failure and exit status | V1 catches failures, prints JSON `error`, and does not explicitly set non-zero exit status. | V2 keeps exact standalone `--check-install` as plain-text `0`, and returns `0` plus evaluator JSON for every other invocation, including malformed caller/request input. | Medium: wrappers must classify evaluator outcomes from JSON rather than from exit status alone. | Keep action-level and malformed-request failures machine-readable in JSON so wrappers can use one response contract. | Implemented. |
| Dynamic test execution | V1 dynamically imports and executes trusted Python test files. | V2 should keep trusted-code execution explicit unless a real sandbox is implemented. | Medium: sandboxing can break existing tests that import libraries or access local resources. | Document trusted-code execution honestly and revisit only when execution controls are an actual product feature. | Recommended V2 direction documented. |
| Package version | V1 package metadata is `1.0.0`. | Current package metadata is `2.0.0`. | Low to medium: version bump communicates breaking change. | Keep the major version signal aligned with contract changes. | Implemented. |
| Docs smoke fixtures | V1 has manual examples but no executable docs smoke target. | Current implementation has automated unit tests plus a local-only docs smoke target for documented examples. | Low: docs can still drift if the target is not run. | Keep `make docs-smoke` in local doc and release verification. | Implemented. |
