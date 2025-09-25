#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/johnninan/Documents/GitHub/kurama"
PYTHON_BIN="/opt/anaconda3/bin/python3"

cd "$REPO_DIR"

# If you use a venv, uncomment the next line and set the correct path:
# source "$REPO_DIR/.venv/bin/activate" && PYTHON_BIN="$REPO_DIR/.venv/bin/python3"

# Run as a module so imports like "from assistant import ..." work
exec "$PYTHON_BIN" -m src.main
