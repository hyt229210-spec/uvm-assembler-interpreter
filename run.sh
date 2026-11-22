#!/usr/bin/env bash

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$ROOT/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "Virtual environment not found."
    exit 1
fi

exec "$PYTHON" "$ROOT/src/assembler.py" "$@"