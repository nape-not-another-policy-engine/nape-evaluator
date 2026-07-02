#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

VENV_DIR="$TMP_ROOT/nape-evaluator-venv"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install .
PATH="$VENV_DIR/bin:$PATH" bash ./scripts/release_validation.sh
