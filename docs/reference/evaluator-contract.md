# Evaluator Contract

This reference defines the evaluator boundary consumed by NAPE CLI.

## Process Contract

Install check:

```bash
nape-eval --check-install
```

Action evaluation:

```bash
nape-eval --evidence <evidence-file> --test <test-file>
```

`--evidence` and `--test` must be provided together.

## Security Boundary

The evaluator dynamically imports and executes the Python file supplied by `--test`.

Treat test-of-detail files as executable code:

- Run only trusted test files.
- Review test files before publishing them in assurance procedure repositories.
- Do not run untrusted test files on a workstation or CI runner with sensitive credentials.
- Keep evidence parsing deterministic and local to the evidence file.

## Test Import Contract

The evaluator dynamically imports the file supplied by `--test`.

The file must define:

```python
def evaluate(evidence):
    ...
```

## Evidence Contract

The evaluator inspects the evidence file extension before calling `evaluate(...)`.

| Extension | Input to `evaluate(evidence)` |
| --- | --- |
| `.txt` | text lines |
| `.json` | parsed JSON object |
| `.xml` | XML root element |
| `.yaml`, `.yml` | parsed YAML object |
| `.pdf` | extracted text lines |
| unknown | text lines |

## Return Contract

`evaluate(...)` must return:

```python
outcome, reason
```

The evaluator serializes the result:

```json
{"outcome": "pass", "reason": "Reason text"}
```

## Outcome Vocabulary

The expected NAPE outcome vocabulary is:

- `pass`
- `fail`
- `inconclusive`
- `error`

The evaluator does not validate the returned outcome before serializing JSON.

## Failure Contract

The evaluator catches these failures and prints JSON `error` output:

| Failure | JSON reason prefix |
| --- | --- |
| `FileNotFoundError` | `Unable to find the file(s) for evaluation.` |
| `ImportError` | `Failed to import the necessary files.` |
| evidence load failure | `Error loading evidence:` |
| Other exception | `Failed to execute the evidence evaluation.` |

Consumers should not infer success from exit status alone. For action evaluation, parse stdout JSON and inspect `outcome`.

Example current behavior:

```bash
python main.py --evidence ./missing.json --test ./missing_test.py
echo $?
```

The evaluator can print JSON like this while still exiting successfully:

```json
{"outcome": "error", "reason": "Unable to find the file(s) for evaluation. ..."}
```

Treat this as the current evaluator behavior unless and until exit-status handling changes.

## NAPE CLI Dependency

NAPE CLI report generation depends on:

- `nape-eval --check-install` succeeding.
- action evaluation printing valid JSON.
- JSON containing `outcome` and `reason`.

If the evaluator process exits non-zero or prints malformed JSON, NAPE CLI report generation can fail before writing a report.
