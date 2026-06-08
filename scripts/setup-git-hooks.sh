#!/bin/sh
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

chmod +x "$REPO_ROOT/.githooks/pre-push"
git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "Configured Git hooks path to .githooks"
echo "pre-push hook is active."
