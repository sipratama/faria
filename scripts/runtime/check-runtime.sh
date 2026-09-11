#!/usr/bin/env bash
# FARIA RF-01 runtime check (portable shell equivalent of check-runtime.ps1).
# Read scripts/runtime/README.md for the manual checks (C, D, E) this script
# cannot safely automate. Never prints secret values. Never fabricates a
# PASS — anything it cannot verify is reported as BLOCKED_BY_LOCAL_CONFIGURATION.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.env}"
blocked_count=0

pass()    { printf 'PASS                            %-32s %s\n' "$1" "$2"; }
blocked() { printf 'BLOCKED_BY_LOCAL_CONFIGURATION %-32s %s\n' "$1" "$2"; blocked_count=$((blocked_count + 1)); }
manual()  { printf 'MANUAL_STEP_REQUIRED            %-32s %s\n' "$1" "$2"; }

if [ ! -f "$ENV_FILE" ]; then
  blocked ".env present" "Missing $ENV_FILE. Copy .env.example to .env and fill in real values, then re-run."
else
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [ -z "${ROUTER9_BASE_URL:-}" ]; then
  blocked "A: 9Router reachability" "ROUTER9_BASE_URL not set in .env."
else
  probe_url="${ROUTER9_BASE_URL%/}/models"
  if curl -fsS -m 5 "$probe_url" >/dev/null 2>&1; then
    pass "A: 9Router reachability" "GET $probe_url succeeded"
  else
    blocked "A: 9Router reachability" "Could not reach $probe_url. Confirm 9Router is running and the URL is correct for this host."
  fi
fi

if ! command -v docker >/dev/null 2>&1; then
  blocked "B: Hermes container running" "Docker is not installed/available on PATH."
else
  status="$(docker ps --filter 'name=faria-hermes-gateway' --format '{{.Status}}' 2>/dev/null || true)"
  if [ -z "$status" ]; then
    blocked "B: Hermes container running" "Container 'faria-hermes-gateway' is not running. From the repo root run: docker compose -f infra/docker/compose.yaml --env-file .env up -d gateway"
  else
    pass "B: Hermes container running" "faria-hermes-gateway: $status"
  fi
fi

manual "C: Normal Hermes chat" "See 'Check C' in scripts/runtime/README.md."
manual "D: Telegram gateway" "See 'Check D' in scripts/runtime/README.md."
manual "E: Unauthorized identity rejected" "See 'Check E' in scripts/runtime/README.md."

echo ""
if [ "$blocked_count" -gt 0 ]; then
  echo "RF-01 PARTIALLY READY: $blocked_count automated check(s) are BLOCKED_BY_LOCAL_CONFIGURATION."
  exit 1
else
  echo "Automated checks passed. Continue with the manual checks (C, D, E) in scripts/runtime/README.md."
  exit 0
fi
