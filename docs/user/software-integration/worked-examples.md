# Worked Examples

This page shows concrete wrapper examples for software that uses `nape-evaluator` as a component.

Read this page after:

- [request-and-invocation.md](request-and-invocation.md)
- [response-handling.md](response-handling.md)
- [production-hardening.md](production-hardening.md)

These examples are intentionally process-boundary oriented.

They do not assume that importing evaluator internals is the preferred public integration API.

## What These Examples Are Trying To Show

The purpose of these examples is not to present a full application framework.

The purpose is to make the integration shape concrete:

- construct request packet
- invoke evaluator
- parse stdout JSON
- classify results and messages
- decide what the wrapper should do next

## Example 1: Minimal Wrapper Flow

This example is the smallest reasonable integration pattern.

It assumes:

- one evidence file
- one requested test
- one full outer request packet
- no advanced persistence or retry logic

### Situation

Your software wants to evaluate one evidence file against one Python test-of-detail and then inspect the structured result.

### Request Packet

```json
{
  "evidence": "./author_verification.json",
  "tests": [
    {
      "test": "./verify_author_complete.py",
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
      ]
    }
  ]
}
```

### Minimal Flow

1. build the full request object
2. serialize it to JSON
3. provide it to `nape-eval --request-file`
4. capture stdout, stderr, and exit status
5. parse stdout JSON
6. inspect the one returned `results[*]` row

### Language-Neutral Pseudocode

```text
request = {
  evidence: "./author_verification.json",
  tests: [
    {
      test: "./verify_author_complete.py",
      evaluations: [
        {
          subject: { name: "status", data_type: "text" },
          criteria: { equals: "complete" }
        }
      ]
    }
  ]
}

serialized = json_encode(request)
write_file(tmp_request_path, serialized)

process_result = run_process(
  argv = ["nape-eval", "--request-file", tmp_request_path]
)

output = json_decode(process_result.stdout)
row = output.results[0]

if row.execution.executed == true and row.result.conclusion == "true":
  return "completed_true"

if row.execution.executed == true and row.result.conclusion == "false":
  return "completed_false"

if row.execution.executed == true and row.result.conclusion == "inconclusive":
  return "completed_inconclusive"

if row.execution.executed == false and row.result.conclusion == "inconclusive":
  return "blocked_inconclusive"

return "contract_unavailable"
```

### What This Example Gets Right

- uses the full request packet directly
- treats stdout JSON as the primary machine-readable result
- reads `execution` and `result` together
- teaches a small but meaningful outcome split instead of one opaque fallback bucket

### What This Example Does Not Yet Do

- explicit timeout handling
- request retention policy
- wrapper-side classification of malformed stdout
- structured logging
- request-scoped versus test-scoped message handling

That is why this is a starter example, not a production default.

## Example 2: Minimal Successful Output Interpretation

Representative returned shape:

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
        "reason": "The author has achieved the status of complete."
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

Minimal wrapper interpretation:

- there was one requested test
- it completed
- it concluded `true`
- there were no evaluator warnings or errors

## Example 3: Defensive Rust-Oriented Wrapper Flow

This example is intentionally closer to a production integration pattern for a Rust caller.

It still stays at the evaluator process boundary.

### Goals

This version adds:

- explicit timeout handling
- stdout JSON parsing
- request artifact retention
- row-level classification
- evaluator-message inspection

### Example Rust-Oriented Pseudocode Shape

This is Rust-oriented pseudocode, not a copy-paste crate-ready module.

The point is to show the wrapper behavior clearly:

- timeout classification
- request retention for unusual outcomes
- evaluator-message inspection
- row-level classification

```rust
use serde_json::{json, Value};
use std::fs;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::time::Duration;

#[derive(Debug)]
enum WrapperOutcome {
    CompletedTrue,
    CompletedFalse,
    CompletedInconclusive,
    BlockedInconclusive,
    TimedOut,
    ContractUnavailable,
}

#[derive(Debug)]
struct EvaluatorRun {
    request_path: PathBuf,
    stdout_json: Value,
    stderr_text: String,
    exit_code: Option<i32>,
}

fn build_request() -> Value {
    json!({
        "evidence": "./author_verification.json",
        "tests": [
            {
                "test": "./verify_author_complete.py",
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
                ]
            }
        ]
    })
}

fn run_evaluator_with_timeout(
    request_path: &PathBuf,
    timeout: Duration,
) -> Result<Option<EvaluatorRun>, String> {
    let mut child = Command::new("nape-eval")
        .arg("--request-file")
        .arg(request_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|err| format!("failed to launch evaluator: {err}"))?;

    // Use any wrapper-local timeout strategy here. The exact mechanism is up to
    // the caller's runtime and dependency choices.
    let finished = wait_for_child_with_timeout(&mut child, timeout)
        .map_err(|err| format!("failed while waiting for evaluator: {err}"))?;

    if !finished {
        let _ = child.kill();
        return Ok(None);
    }

    let output = child
        .wait_with_output()
        .map_err(|err| format!("failed to collect evaluator output: {err}"))?;

    let stdout_text = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr_text = String::from_utf8_lossy(&output.stderr).to_string();
    let stdout_json: Value = serde_json::from_str(&stdout_text)
        .map_err(|err| format!("evaluator stdout was not valid JSON: {err}"))?;

    Ok(Some(EvaluatorRun {
        request_path: request_path.clone(),
        stdout_json,
        stderr_text,
        exit_code: output.status.code(),
    }))
}

fn classify(run: &EvaluatorRun) -> Result<(WrapperOutcome, bool), String> {
    let results = run.stdout_json["results"]
        .as_array()
        .ok_or("missing results array")?;

    let evaluator_messages = run.stdout_json["evaluator"]["messages"]
        .as_array()
        .ok_or("missing evaluator.messages")?;
    let has_error_message = evaluator_messages.iter().any(|message| {
        message["level"].as_str() == Some("error")
    });

    let first = results.first().ok_or("missing first result row")?;
    let executed = first["execution"]["executed"]
        .as_bool()
        .ok_or("missing execution.executed")?;
    let conclusion = first["result"]["conclusion"]
        .as_str()
        .ok_or("missing result.conclusion")?;

    let outcome = match (executed, conclusion) {
        (true, "true") => WrapperOutcome::CompletedTrue,
        (true, "false") => WrapperOutcome::CompletedFalse,
        (true, "inconclusive") => WrapperOutcome::CompletedInconclusive,
        (false, "inconclusive") => WrapperOutcome::BlockedInconclusive,
        _ => WrapperOutcome::ContractUnavailable,
    };

    Ok((outcome, has_error_message))
}

fn should_retain_request(outcome: &WrapperOutcome, has_error_message: bool) -> bool {
    match outcome {
        WrapperOutcome::CompletedInconclusive => true,
        WrapperOutcome::BlockedInconclusive => true,
        WrapperOutcome::TimedOut => true,
        WrapperOutcome::ContractUnavailable => true,
        WrapperOutcome::CompletedTrue | WrapperOutcome::CompletedFalse => has_error_message,
    }
}

fn retain_request_artifact(request_path: &PathBuf) -> Result<(), String> {
    let retained_path = PathBuf::from("./retained-requests").join(
        request_path.file_name().unwrap()
    );
    fs::create_dir_all("./retained-requests")
        .map_err(|err| format!("failed to create retained request directory: {err}"))?;
    fs::copy(request_path, retained_path)
        .map_err(|err| format!("failed to retain request artifact: {err}"))?;
    Ok(())
}

fn main() -> Result<(), String> {
    let request = build_request();
    let request_path = PathBuf::from("./tmp-request.json");
    fs::write(&request_path, serde_json::to_vec_pretty(&request).unwrap())
        .map_err(|err| format!("failed to write request file: {err}"))?;

    let maybe_run = run_evaluator_with_timeout(
        &request_path,
        Duration::from_secs(30),
    )?;

    let (outcome, run) = match maybe_run {
        None => {
            retain_request_artifact(&request_path)?;
            println!("wrapper outcome: {:?}", WrapperOutcome::TimedOut);
            return Ok(());
        }
        Some(run) => {
            let (outcome, has_error_message) = classify(&run)?;
            if should_retain_request(&outcome, has_error_message) {
                retain_request_artifact(&run.request_path)?;
            }
            (outcome, run)
        }
    };

    println!("wrapper outcome: {:?}", outcome);
    println!("exit code: {:?}", run.exit_code);
    println!("stderr: {}", run.stderr_text);

    let message_count = run.stdout_json["evaluator"]["summary"]["message_count"]
        .as_u64()
        .unwrap_or(0);
    println!("evaluator message_count: {}", message_count);

    Ok(())
}
```

### What To Notice In The Rust Example

1. the wrapper never imports evaluator internals
2. the wrapper serializes one full request packet explicitly
3. the wrapper parses stdout JSON before making a decision
4. the wrapper uses `execution.executed` plus `result.conclusion`
5. timeout is classified separately from evaluator JSON outcomes
6. unusual outcomes retain the request artifact
7. stderr and exit code are retained as supporting diagnostics
8. evaluator messages are inspected rather than ignored

### What A More Production-Ready Rust Version Would Add

- stronger typed deserialization instead of broad `Value`
- richer evaluator-message inspection, especially:
  - request-scoped warnings
  - `stack_trace`
- wrapper correlation ids
- cleanup policy for temporary and retained request files
- a concrete timeout helper implementation suited to the caller's runtime

## Example 4: Blocked Invocation Interpretation

Suppose your wrapper receives:

```json
{
  "results": [
    {
      "test": "./missing_test.py",
      "evidence": "./author_verification.json",
      "evaluations": [],
      "execution": {
        "executed": false,
        "status": "blocked"
      },
      "result": {
        "conclusion": "inconclusive",
        "facts": [],
        "reason": "The test could not be completed, so the conclusion is inconclusive. The evaluator could not find the test file."
      }
    }
  ],
  "evaluator": {
    "messages": [
      {
        "scope": "test",
        "level": "error",
        "source": "evaluator",
        "code": "test_file_not_found",
        "message": "Unable to find the file(s) for evaluation. [Errno 2] ...",
        "evidence_file": "./author_verification.json",
        "test_file": "./missing_test.py",
        "affected_tests": null,
        "stack_trace": "Traceback (most recent call last): ..."
      }
    ],
    "summary": {
      "count": 1,
      "ran": 0,
      "true": 0,
      "false": 0,
      "inconclusive": 1,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 0,
      "message_error": 1
    }
  }
}
```

Correct wrapper interpretation:

- this is not a completed test-level inconclusive
- this is a blocked invocation
- the evaluator owns the blocked reason
- the evaluator also emitted an operational error message

Incorrect interpretation:

- “the test completed and concluded inconclusive”

That would lose the key operational distinction.

## Example 5: Shared Warning Across Two Tests

Suppose one evidence file is evaluated by two requested tests and the evaluator emits one shared evidence warning:

```json
{
  "results": [
    {
      "test": "./verify_author_complete.py",
      "evidence": "./author_verification",
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
    },
    {
      "test": "./verify_author_approved.py",
      "evidence": "./author_verification",
      "evaluations": [
        {
          "subject": {
            "name": "approval",
            "data_type": "text"
          },
          "criteria": {
            "equals": "approved"
          }
        }
      ],
      "execution": {
        "executed": true,
        "status": "completed"
      },
      "result": {
        "conclusion": "false",
        "facts": [
          {
            "name": "approval",
            "value": "pending",
            "value_type": "text",
            "status": "found"
          }
        ],
        "reason": "The author has not achieved the expected status."
      }
    }
  ],
  "evaluator": {
    "messages": [
      {
        "scope": "request",
        "level": "warning",
        "source": "evaluator",
        "code": "missing_extension_text_fallback",
        "message": "Evidence file had no extension and was evaluated as text.",
        "evidence_file": "./author_verification",
        "test_file": null,
        "affected_tests": [
          "./verify_author_complete.py",
          "./verify_author_approved.py"
        ],
        "stack_trace": null
      }
    ],
    "summary": {
      "count": 2,
      "ran": 2,
      "true": 1,
      "false": 1,
      "inconclusive": 0,
      "message_count": 1,
      "message_info": 0,
      "message_warning": 1,
      "message_error": 0
    }
  }
}
```

Correct wrapper interpretation:

- two completed test rows exist
- one shared request-scoped warning exists
- the wrapper should not invent two fake warning rows unless its own product explicitly needs that denormalization

## Recommended Progression For A Real Integration

If you are starting from nothing, use this progression:

1. implement the minimal full-request subprocess flow
2. add response classification using `execution` plus `result.conclusion`
3. add evaluator-message handling
4. add timeout and request-retention hardening
5. then move to stronger typed deserialization or richer wrapper-local models

This order reduces the chance that you build a large abstraction before you have proven the evaluator boundary is being handled correctly.

## What To Build Next In Your Own Wrapper

After you can run these examples successfully, the next useful improvements are usually:

- a stronger wrapper-local result model
- explicit timeout handling
- request/response artifact retention
- wrapper-side metrics and observability
- integration tests that lock your own expected evaluator semantics
