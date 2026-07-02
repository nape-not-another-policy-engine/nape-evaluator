#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

check_install_output="$(python3 main.py --check-install)"
if [[ "$check_install_output" != "NAPE Evaluator CLI is installed and working." ]]; then
  echo "docs-smoke: unexpected --check-install output" >&2
  exit 1
fi

python3 main.py \
  --evidence tests/json/evidence/author_verification.json \
  --invoke '{"test":"tests/json/test_of_detail/verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}' \
  | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["evaluator"]["summary"]["count"] == 1
assert data["evaluator"]["summary"]["ran"] == 1
assert data["evaluator"]["summary"]["true"] == 1
assert data["results"][0]["result"]["conclusion"] == "true"
'

python3 main.py \
  --evidence tests/json/evidence/author_verification_empty_status.json \
  --invoke '{"test":"tests/json/test_of_detail/verify_author_complete.py","evaluations":[{"subject":{"name":"status","data_type":"text"},"criteria":{"equals":"complete"}}]}' \
  | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["evaluator"]["summary"]["count"] == 1
assert data["evaluator"]["summary"]["ran"] == 1
assert data["evaluator"]["summary"]["inconclusive"] == 1
assert data["results"][0]["result"]["conclusion"] == "inconclusive"
'

echo "docs-smoke: OK"
