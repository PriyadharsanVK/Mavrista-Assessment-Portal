#!/usr/bin/env bash
set -euo pipefail

# Assessment Portal - Production Startup Script for Linux
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo " Starting Assessment Portal Server (Mavrista Technologies)"
echo "=========================================================="

# Load .env if present
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Ensure data directory exists
mkdir -p data

# Check python version
PYTHON_BIN="$(which python3 || which python)"
if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python 3 is required but not found in PATH."
    exit 1
fi

echo "Using Python: $($PYTHON_BIN --version)"
echo "Host: ${ASSESSMENT_HOST:-0.0.0.0}"
echo "Port: ${ASSESSMENT_PORT:-8000}"
echo "Timezone: Asia/Kolkata (IST)"

exec "$PYTHON_BIN" server.py

