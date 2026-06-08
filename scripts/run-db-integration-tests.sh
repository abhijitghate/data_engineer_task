#!/bin/sh
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_NAME="scope_dbtests"

cleanup() {
  docker compose -p "$PROJECT_NAME" -f "$REPO_ROOT/docker-compose.yml" down -v >/dev/null 2>&1 || true
}
trap cleanup EXIT

cd "$REPO_ROOT"
docker compose -p "$PROJECT_NAME" -f docker-compose.yml --profile test up -d postgres migrate
docker compose -p "$PROJECT_NAME" -f docker-compose.yml --profile test run --rm test
