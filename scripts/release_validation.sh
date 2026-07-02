#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TMP_DIR="$(mktemp -d)"
if [[ "${KEEP_RELEASE_VALIDATION_TMP:-0}" == "1" ]]; then
  trap 'echo "release-validation: retained temp dir at $TMP_DIR"' EXIT
else
  trap 'rm -rf "$TMP_DIR"' EXIT
fi

run_eval() {
  if [[ "${EVALUATOR_USE_MAIN_PY:-0}" == "1" ]]; then
    python3 main.py "$@"
  else
    nape-eval "$@"
  fi
}

assert_check_install() {
  local stdout_file="$1"
  local stderr_file="$2"
  python3 - "$stdout_file" "$stderr_file" <<'PY'
import sys
from pathlib import Path

stdout_text = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
stderr_text = Path(sys.argv[2]).read_text(encoding="utf-8")

assert stdout_text == "NAPE Evaluator CLI is installed and working."
assert stderr_text == ""
PY
}

assert_completed_true() {
  local stdout_file="$1"
  local stderr_file="$2"
  local expected_test="$3"
  local expected_evidence="$4"
  python3 - "$stdout_file" "$stderr_file" "$expected_test" "$expected_evidence" <<'PY'
import json
import sys
from pathlib import Path

output = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
stderr_text = Path(sys.argv[2]).read_text(encoding="utf-8")
expected_test = str(Path(sys.argv[3]).resolve())
expected_evidence = str(Path(sys.argv[4]).resolve())

assert stderr_text == ""
assert output["evaluator"]["summary"]["count"] == 1
assert output["evaluator"]["summary"]["ran"] == 1
assert output["evaluator"]["summary"]["true"] == 1
assert output["evaluator"]["summary"]["message_error"] == 0
row = output["results"][0]
assert str(Path(row["test"]).resolve()) == expected_test
assert str(Path(row["evidence"]).resolve()) == expected_evidence
assert row["execution"]["executed"] is True
assert row["execution"]["status"] == "completed"
assert row["result"]["conclusion"] == "true"
PY
}

assert_request_error() {
  local stdout_file="$1"
  local stderr_file="$2"
  local expected_code="$3"
  python3 - "$stdout_file" "$stderr_file" "$expected_code" <<'PY'
import json
import sys
from pathlib import Path

output = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
stderr_text = Path(sys.argv[2]).read_text(encoding="utf-8")
expected_code = sys.argv[3]

assert stderr_text == ""
assert output["results"] == []
assert output["evaluator"]["summary"]["count"] == 0
assert output["evaluator"]["summary"]["ran"] == 0
assert output["evaluator"]["summary"]["message_error"] == 1
messages = output["evaluator"]["messages"]
assert len(messages) == 1
message = messages[0]
assert message["scope"] == "request"
assert message["level"] == "error"
assert message["code"] == expected_code
PY
}

assert_blocked_result() {
  local stdout_file="$1"
  local stderr_file="$2"
  python3 - "$stdout_file" "$stderr_file" <<'PY'
import json
import sys
from pathlib import Path

output = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
stderr_text = Path(sys.argv[2]).read_text(encoding="utf-8")

assert stderr_text == ""
assert output["evaluator"]["summary"]["count"] == 1
assert output["evaluator"]["summary"]["ran"] == 0
assert output["evaluator"]["summary"]["inconclusive"] == 1
assert output["evaluator"]["summary"]["message_error"] == 1
row = output["results"][0]
assert row["execution"]["executed"] is False
assert row["execution"]["status"] == "blocked"
assert row["result"]["conclusion"] == "inconclusive"
assert output["evaluator"]["messages"][0]["level"] == "error"
PY
}

cat > "$TMP_DIR/verify_supported_loader.py" <<'PY'
def _criteria_by_name(evaluations):
    criteria = {}
    for item in evaluations:
        criteria[item["subject"]["name"]] = item["criteria"]
    return criteria


def _build_fact(name, value, status, value_type="text"):
    return {
        "name": name,
        "value": value,
        "value_type": value_type,
        "status": status,
    }


def _extract_status(evidence, evidence_type):
    if evidence_type in ("text", "pdf"):
        text = "\n".join(evidence)
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                if key.strip() == "status":
                    return value.strip()
        return None
    if evidence_type in ("json", "yaml"):
        return evidence.get("status")
    if evidence_type == "xml":
        return evidence.findtext("status")
    return None


def evaluate(evidence, evaluations, metadata):
    criteria = _criteria_by_name(evaluations)
    expected_status = criteria["status"]["equals"]
    expected_evidence_type = criteria["evidence_type"]["equals"]
    actual_evidence_type = metadata.get("evidence_type")

    evidence_type_fact = _build_fact(
        "evidence_type",
        actual_evidence_type,
        "found" if actual_evidence_type is not None else "not_found",
    )
    status = _extract_status(evidence, actual_evidence_type)
    status_fact = _build_fact(
        "status",
        status,
        "found" if status not in (None, "") else "not_found",
    )

    if actual_evidence_type != expected_evidence_type:
        return {
            "conclusion": "false",
            "facts": [evidence_type_fact, status_fact],
            "reason": f"Expected evidence_type {expected_evidence_type} but received {actual_evidence_type}.",
        }

    if status_fact["status"] != "found":
        return {
            "conclusion": "inconclusive",
            "facts": [evidence_type_fact, status_fact],
            "reason": "Status could not be established from the evidence.",
        }

    if status == expected_status:
        return {
            "conclusion": "true",
            "facts": [evidence_type_fact, status_fact],
            "reason": "Status and evidence type matched the expected values.",
        }

    return {
        "conclusion": "false",
        "facts": [evidence_type_fact, status_fact],
        "reason": f"Expected status {expected_status} but found {status}.",
    }
PY

cat > "$TMP_DIR/evidence.txt" <<'EOF'
status: complete
EOF

cat > "$TMP_DIR/evidence.json" <<'EOF'
{"status":"complete"}
EOF

cat > "$TMP_DIR/evidence.xml" <<'EOF'
<root><status>complete</status></root>
EOF

cat > "$TMP_DIR/evidence.yaml" <<'EOF'
status: complete
EOF

python3 - "$TMP_DIR/evidence.pdf" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
content = "BT\n/F1 24 Tf\n72 72 Td\n(status: complete) Tj\nET\n"
objects = [
    "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
    "2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n",
    "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
    f"4 0 obj\n<< /Length {len(content.encode('latin-1'))} >>\nstream\n{content}endstream\nendobj\n",
    "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
]

parts = ["%PDF-1.4\n"]
offsets = []
current = len(parts[0].encode("latin-1"))
for obj in objects:
    offsets.append(current)
    parts.append(obj)
    current += len(obj.encode("latin-1"))

xref_offset = current
xref = ["xref\n0 6\n", "0000000000 65535 f \n"]
for offset in offsets:
    xref.append(f"{offset:010d} 00000 n \n")
parts.extend(xref)
parts.append("trailer\n<< /Root 1 0 R /Size 6 >>\n")
parts.append(f"startxref\n{xref_offset}\n%%EOF\n")
path.write_bytes("".join(parts).encode("latin-1"))
PY

python3 - "$TMP_DIR/invoke-json.json" "$TMP_DIR/verify_supported_loader.py" <<'PY'
import json
import sys
from pathlib import Path

invoke_path = Path(sys.argv[1])
test_path = Path(sys.argv[2]).resolve()
packet = {
    "test": str(test_path),
    "evaluations": [
        {
            "subject": {"name": "status", "data_type": "text"},
            "criteria": {"equals": "complete"},
        },
        {
            "subject": {"name": "evidence_type", "data_type": "text"},
            "criteria": {"equals": "json"},
        },
    ],
}
invoke_path.write_text(json.dumps(packet), encoding="utf-8")
PY

run_success_case() {
  local label="$1"
  local evidence_path="$2"
  local expected_type="$3"
  local mode="$4"
  local stdout_file="$TMP_DIR/${label}.stdout.json"
  local stderr_file="$TMP_DIR/${label}.stderr.txt"
  local test_path="$TMP_DIR/verify_supported_loader.py"
  local invoke_file="$TMP_DIR/${label}.invoke.json"
  local request_file="$TMP_DIR/${label}.request.json"

  echo "release-validation: running $label"

  python3 - "$invoke_file" "$test_path" "$expected_type" <<'PY'
import json
import sys
from pathlib import Path

invoke_path = Path(sys.argv[1])
test_path = Path(sys.argv[2]).resolve()
expected_type = sys.argv[3]
packet = {
    "test": str(test_path),
    "evaluations": [
        {
            "subject": {"name": "status", "data_type": "text"},
            "criteria": {"equals": "complete"},
        },
        {
            "subject": {"name": "evidence_type", "data_type": "text"},
            "criteria": {"equals": expected_type},
        },
    ],
}
invoke_path.write_text(json.dumps(packet), encoding="utf-8")
PY

  if [[ "$mode" == "invoke" ]]; then
    if ! run_eval --evidence "$evidence_path" --invoke "$(cat "$invoke_file")" >"$stdout_file" 2>"$stderr_file"; then
      echo "release-validation: $label failed" >&2
      exit 1
    fi
  elif [[ "$mode" == "invoke-file" ]]; then
    if ! run_eval --evidence "$evidence_path" --invoke-file "$invoke_file" >"$stdout_file" 2>"$stderr_file"; then
      echo "release-validation: $label failed" >&2
      exit 1
    fi
  else
    python3 - "$request_file" "$evidence_path" "$invoke_file" <<'PY'
import json
import sys
from pathlib import Path

request_path = Path(sys.argv[1])
evidence_path = Path(sys.argv[2]).resolve()
invoke_path = Path(sys.argv[3])
request_path.write_text(
    json.dumps(
        {
            "evidence": str(evidence_path),
            "tests": [json.loads(invoke_path.read_text(encoding="utf-8"))],
        }
    ),
    encoding="utf-8",
)
PY
    if ! run_eval --request-file "$request_file" >"$stdout_file" 2>"$stderr_file"; then
      echo "release-validation: $label failed" >&2
      exit 1
    fi
  fi

  assert_completed_true "$stdout_file" "$stderr_file" "$test_path" "$evidence_path"
}

run_check_install_case() {
  local stdout_file="$TMP_DIR/check-install.stdout.txt"
  local stderr_file="$TMP_DIR/check-install.stderr.txt"
  echo "release-validation: running check-install"
  if ! run_eval --check-install >"$stdout_file" 2>"$stderr_file"; then
    echo "release-validation: check-install failed" >&2
    exit 1
  fi
  assert_check_install "$stdout_file" "$stderr_file"
}

run_request_error_case() {
  local request_file="$TMP_DIR/bad-request.json"
  local stdout_file="$TMP_DIR/bad-request.stdout.json"
  local stderr_file="$TMP_DIR/bad-request.stderr.txt"
  echo "release-validation: running malformed-request"
  printf '{bad json' > "$request_file"
  if ! run_eval --request-file "$request_file" >"$stdout_file" 2>"$stderr_file"; then
    echo "release-validation: malformed request case failed" >&2
    exit 1
  fi
  assert_request_error "$stdout_file" "$stderr_file" "request_json_decode_error"
}

run_missing_evidence_case() {
  local missing_evidence="$TMP_DIR/missing.json"
  local stdout_file="$TMP_DIR/missing-evidence.stdout.json"
  local stderr_file="$TMP_DIR/missing-evidence.stderr.txt"
  local test_path="$TMP_DIR/verify_supported_loader.py"
  local invoke_file="$TMP_DIR/missing-evidence.invoke.json"

  echo "release-validation: running missing-evidence"

  python3 - "$invoke_file" "$test_path" <<'PY'
import json
import sys
from pathlib import Path

invoke_path = Path(sys.argv[1])
test_path = Path(sys.argv[2]).resolve()
packet = {
    "test": str(test_path),
    "evaluations": [
        {
            "subject": {"name": "status", "data_type": "text"},
            "criteria": {"equals": "complete"},
        },
        {
            "subject": {"name": "evidence_type", "data_type": "text"},
            "criteria": {"equals": "json"},
        },
    ],
}
invoke_path.write_text(json.dumps(packet), encoding="utf-8")
PY

  if ! run_eval --evidence "$missing_evidence" --invoke "$(cat "$invoke_file")" >"$stdout_file" 2>"$stderr_file"; then
    echo "release-validation: missing evidence case failed" >&2
    exit 1
  fi
  assert_blocked_result "$stdout_file" "$stderr_file"
}

run_check_install_case
run_success_case "direct-json" "$TMP_DIR/evidence.json" "json" "invoke"
run_success_case "direct-txt" "$TMP_DIR/evidence.txt" "text" "invoke-file"
run_success_case "request-file-json" "$TMP_DIR/evidence.json" "json" "request-file"
run_success_case "direct-xml" "$TMP_DIR/evidence.xml" "xml" "invoke"
run_success_case "direct-yaml" "$TMP_DIR/evidence.yaml" "yaml" "invoke"
run_success_case "direct-pdf" "$TMP_DIR/evidence.pdf" "pdf" "invoke"
run_request_error_case
run_missing_evidence_case

echo "release-validation: OK"
