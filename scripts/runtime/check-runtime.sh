#!/usr/bin/env bash
# FARIA RF-01 checks for the accepted host-managed macOS topology.
# Manual chat and Telegram evidence is recorded in scripts/runtime/README.md.
set -euo pipefail

router_models_url="${1:-http://127.0.0.1:20128/v1/models}"
blocked_count=0

pass()     { printf 'PASS                            %-30s %s\n' "$1" "$2"; }
blocked()  { printf 'BLOCKED_BY_LOCAL_CONFIGURATION %-30s %s\n' "$1" "$2"; blocked_count=$((blocked_count + 1)); }
recorded() { printf 'RECORDED_MANUAL_EVIDENCE        %-30s %s\n' "$1" "$2"; }

if ! command -v curl >/dev/null 2>&1; then
  blocked "A: 9Router reachability" "curl is not available on PATH."
else
  router_http="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "$router_models_url" 2>/dev/null || true)"
  case "$router_http" in
    200|401|403)
      pass "A: 9Router reachability" "$router_models_url responded with HTTP $router_http"
      ;;
    000|"")
      blocked "A: 9Router reachability" "No response from $router_models_url. Confirm 9Router is running on the host."
      ;;
    *)
      blocked "A: 9Router reachability" "$router_models_url returned unexpected HTTP $router_http. Confirm the port and /v1/models path."
      ;;
  esac
fi

if ! command -v hermes >/dev/null 2>&1; then
  blocked "B: Hermes installed" "hermes is not available on PATH. Use the official managed installer, then re-run."
else
  hermes_version="$(hermes --version 2>/dev/null | sed -n '1p')"
  if [ -n "$hermes_version" ]; then
    pass "B: Hermes installed" "$hermes_version"
  else
    blocked "B: Hermes installed" "hermes --version did not return version information."
  fi
fi

if ! command -v hermes >/dev/null 2>&1; then
  blocked "C: Gateway supervised" "Hermes is required before gateway status can be checked."
else
  gateway_status="$(hermes gateway status 2>&1 || true)"
  if printf '%s\n' "$gateway_status" | grep -q 'Service definition matches' \
    && printf '%s\n' "$gateway_status" | grep -Eq 'supervised by launchd \(PID [0-9]+\)'; then
    pass "C: Gateway supervised" "Current Hermes service definition is running under launchd."
  else
    blocked "C: Gateway supervised" "Run 'hermes gateway status'; if needed, configure with 'hermes setup gateway'."
  fi
fi

recorded "D: Normal Hermes chat" "PASS from RF-01A manual acceptance evidence; see scripts/runtime/README.md."
recorded "E: Telegram smoke test" "PASS from RF-01A manual acceptance evidence; see scripts/runtime/README.md."

printf '\n'
if [ "$blocked_count" -gt 0 ]; then
  printf 'RF-01 runtime checks blocked: %s non-secret check(s) failed.\n' "$blocked_count"
  exit 1
fi

printf 'RF-01 runtime connectivity checks pass. Security onboarding follow-ups remain documented in scripts/runtime/README.md.\n'
