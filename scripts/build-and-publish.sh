#!/bin/bash
# build-and-publish.sh — run the full newsletter pipeline for a single slug.
# Usage: ./scripts/build-and-publish.sh <slug>
# Runs: research → build → publish in sequence. Exits on any failure.
set -euo pipefail

SLUG="${1:?Usage: $0 <slug>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Pipeline: ${SLUG} ==="
echo "--- [1/3] Research ---"
python3 "${REPO_ROOT}/lib/research.py" "${SLUG}"

echo "--- [2/3] Build ---"
python3 "${REPO_ROOT}/lib/build.py" "${SLUG}"

echo "--- [3/3] Publish ---"
python3 "${REPO_ROOT}/lib/publish.py" "${SLUG}"

echo "=== Done: ${SLUG} ==="
