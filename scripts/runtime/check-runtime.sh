#!/usr/bin/env bash
# Provider-neutral, non-mutating FARIA personal runtime checks.
set -u

router_models_url="${1:-http://127.0.0.1:20128/v1/models}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
database_path="${FARIA_DB_PATH:-$HOME/.faria/data/faria.db}"
expected_migration="004"
failure_count=0
warning_count=0

pass() { printf 'PASS %-34s %s\n' "$1" "$2"; }
warn() { printf 'WARN %-34s %s\n' "$1" "$2"; warning_count=$((warning_count + 1)); }
fail() { printf 'FAIL %-34s %s\n' "$1" "$2"; failure_count=$((failure_count + 1)); }

if [ -x "$repo_root/household-mcp/.venv/bin/python" ]; then
  python_command="$repo_root/household-mcp/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  python_command="$(command -v python3)"
else
  python_command=""
fi

if [ -z "$python_command" ]; then
  fail "Python" "Python 3.11 or newer is required."
else
  python_version="$($python_command -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)"
  if "$python_command" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    pass "Python" "Supported Python $python_version is available."
  else
    fail "Python" "Python 3.11 or newer is required."
  fi
fi

household_mcp="$repo_root/household-mcp/.venv/bin/faria-household-mcp"
if [ -x "$household_mcp" ]; then
  pass "Household MCP executable" "Repository virtualenv entry point is executable."
else
  fail "Household MCP executable" "Run 'cd household-mcp && uv sync'."
fi

if [ -z "$python_command" ]; then
  fail "SQLite health" "Python is required for safe read-only SQLite checks."
elif [ ! -f "$database_path" ]; then
  fail "SQLite health" "The configured FARIA database file is missing."
else
  database_check="$($python_command - "$database_path" "$expected_migration" <<'PY' 2>/dev/null
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

path = Path(sys.argv[1]).expanduser()
expected = sys.argv[2]
uri = f"file:{quote(str(path.resolve()))}?mode=ro"
with sqlite3.connect(uri, uri=True, timeout=5.0) as connection:
    connection.execute("PRAGMA query_only = ON")
    integrity = connection.execute("PRAGMA integrity_check").fetchall()
    foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
    versions = tuple(
        str(row[0])
        for row in connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
    )
if integrity != [("ok",)]:
    raise SystemExit(2)
if foreign_keys:
    raise SystemExit(3)
if not versions or versions[-1] != expected:
    raise SystemExit(4)
directory_mode = oct(path.parent.stat().st_mode & 0o777)
file_mode = oct(path.stat().st_mode & 0o777)
print(f"migration={versions[-1]} directory_mode={directory_mode} file_mode={file_mode}")
PY
)"
  database_rc=$?
  if [ "$database_rc" -eq 0 ]; then
    pass "SQLite health" "integrity_check=ok, foreign_key_check=clean, migration=$expected_migration."
    case "$database_check" in
      *"directory_mode=0o700"*"file_mode=0o600"*)
        pass "SQLite permissions" "Database directory and file use restrictive permissions."
        ;;
      *)
        warn "SQLite permissions" "Review database directory/file permissions; target 0700/0600."
        ;;
    esac
  else
    case "$database_rc" in
      2)
        fail "SQLite health" "PRAGMA integrity_check did not return ok."
        ;;
      3)
        fail "SQLite health" "PRAGMA foreign_key_check reported violations."
        ;;
      4)
        fail "SQLite migration" "Expected migration $expected_migration is not applied."
        ;;
      *)
        fail "SQLite health" "The database could not be opened or its migration metadata is unreadable."
        ;;
    esac
  fi
fi

if ! command -v curl >/dev/null 2>&1; then
  fail "9Router reachability" "curl is not available on PATH."
else
  router_http="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "$router_models_url" 2>/dev/null || true)"
  case "$router_http" in
    200|401|403)
      pass "9Router reachability" "Logical local endpoint responded with HTTP $router_http."
      ;;
    *)
      fail "9Router reachability" "The local /v1/models endpoint did not respond safely."
      ;;
  esac
fi

if ! command -v age >/dev/null 2>&1; then
  warn "Backup encryption" "age is unavailable; encrypted backups cannot run yet."
else
  pass "Backup encryption" "age is available."
fi

if [ -z "${FARIA_BACKUP_DIR:-}" ]; then
  warn "External backup destination" "FARIA_BACKUP_DIR is not set for this shell."
elif [ ! -d "$FARIA_BACKUP_DIR" ]; then
  fail "External backup destination" "Configured backup directory is unavailable."
elif [ ! -w "$FARIA_BACKUP_DIR" ]; then
  fail "External backup destination" "Configured backup directory is not writable."
else
  pass "External backup destination" "Configured backup directory is available."
fi

if ! command -v hermes >/dev/null 2>&1; then
  fail "Hermes" "Hermes is not available on PATH."
else
  hermes_version="$(hermes --version 2>/dev/null | sed -n '1p')"
  if [ -n "$hermes_version" ]; then
    pass "Hermes" "$hermes_version"
  else
    fail "Hermes" "hermes --version returned no version."
  fi

  gateway_status="$(hermes gateway status 2>&1 || true)"
  if printf '%s\n' "$gateway_status" | grep -q 'Service definition matches' \
    && printf '%s\n' "$gateway_status" | grep -Eq 'supervised by launchd \(PID [0-9]+\)'; then
    pass "Gateway supervision" "Gateway is running under launchd."
  elif printf '%s\n' "$gateway_status" | grep -q 'detached gateway process is running'; then
    fail "Gateway supervision" "Gateway is detached and launchd is not active."
  else
    fail "Gateway supervision" "Gateway is not confirmed running under launchd."
  fi

  primary_override="$(hermes config get mcp_servers.faria-household.env.FARIA_DB_PATH --json 2>/dev/null || true)"
  cron_override="$(hermes config get mcp_servers.faria-household-cron-readonly.env.FARIA_DB_PATH --json 2>/dev/null || true)"
  if printf '%s\n%s\n' "$primary_override" "$cron_override" | grep -Eqi 'faria-rf06|/tmp/|/private/tmp/'; then
    fail "MCP database configuration" "A temporary FARIA_DB_PATH override is still configured."
  else
    pass "MCP database configuration" "No RF-06 temporary database override is active."
  fi

  mcp_list="$(hermes mcp list 2>&1 || true)"
  if printf '%s\n' "$mcp_list" | grep -Eq 'faria-household[[:space:]].*18 selected.*enabled'; then
    pass "Primary MCP selection" "faria-household exposes 18 selected tools."
  else
    fail "Primary MCP selection" "Expected 18 selected primary MCP tools."
  fi
  if printf '%s\n' "$mcp_list" | grep -Eq 'faria-household-cron-readonly.*1 selected.*enabled'; then
    pass "Cron MCP selection" "Cron alias exposes one selected tool."
  else
    fail "Cron MCP selection" "Expected one selected cron-readonly tool."
  fi

  if hermes mcp test faria-household >/dev/null 2>&1; then
    pass "Primary MCP discovery" "Connection and discovery succeeded."
  else
    fail "Primary MCP discovery" "Connection or discovery failed."
  fi
  if hermes mcp test faria-household-cron-readonly >/dev/null 2>&1; then
    pass "Cron MCP discovery" "Connection and discovery succeeded."
  else
    fail "Cron MCP discovery" "Connection or discovery failed."
  fi

  primary_tools="$(hermes config get mcp_servers.faria-household.tools.include --json 2>/dev/null || true)"
  readonly_tools="$(hermes config get mcp_servers.faria-household-cron-readonly.tools.include --json 2>/dev/null || true)"
  if [ -n "$python_command" ]; then
    primary_count="$(printf '%s' "$primary_tools" | "$python_command" -c 'import json,sys; data=json.load(sys.stdin); print(len(data) if isinstance(data,list) else -1)' 2>/dev/null || true)"
  else
    primary_count="-1"
  fi
  if [ "$primary_count" = "18" ]; then
    pass "Primary MCP allowlist" "Configured allowlist contains exactly 18 tools."
  else
    fail "Primary MCP allowlist" "Configured primary allowlist is not exactly 18 tools."
  fi
  if [ "$readonly_tools" = '["routine_get"]' ]; then
    pass "CRON_READONLY_OK" "Cron alias is restricted to routine_get only."
  else
    fail "CRON_READONLY_OK" "Cron alias tool selection drifted."
  fi

  telegram_toolsets="$(hermes config get platform_toolsets.telegram --json 2>/dev/null || true)"
  cron_toolsets="$(hermes config get platform_toolsets.cron --json 2>/dev/null || true)"
  if [ "$telegram_toolsets" = '["skills", "cronjob", "faria-household"]' ]; then
    pass "Telegram platform toolsets" "Only skills, cronjob, and primary Household MCP are selected."
  else
    fail "Telegram platform toolsets" "Telegram platform toolset selection drifted."
  fi
  if [ "$cron_toolsets" = '["skills", "faria-household-cron-readonly"]' ]; then
    pass "Cron platform toolsets" "Only skills and the cron-readonly alias are selected."
  else
    fail "Cron platform toolsets" "Cron platform toolset selection drifted."
  fi

  for platform in telegram cron; do
    tool_output="$(hermes tools list --platform "$platform" 2>&1 || true)"
    dangerous_enabled=0
    for tool in web browser terminal file code_execution delegation computer_use; do
      if ! printf '%s\n' "$tool_output" | grep -Eq "disabled[[:space:]]+$tool([[:space:]]|$)"; then
        dangerous_enabled=1
      fi
    done
    if [ "$dangerous_enabled" -eq 0 ]; then
      pass "$platform system tools" "Dangerous general-purpose tools are disabled."
    else
      fail "$platform system tools" "One or more dangerous general-purpose tools are not confirmed disabled."
    fi
  done

  skill_list="$(hermes skills list --source local 2>&1 || true)"
  if printf '%s\n' "$skill_list" | grep -q 'faria-finance' \
    && printf '%s\n' "$skill_list" | grep -q 'faria-home-ops'; then
    pass "FARIA skill discovery" "Finance and Home Ops skills are enabled."
  else
    fail "FARIA skill discovery" "Expected local FARIA skills were not discovered."
  fi

  cron_status="$(hermes cron status 2>&1 || true)"
  if printf '%s\n' "$cron_status" | grep -q 'Gateway is running'; then
    pass "Cron scheduler" "Scheduler ticker is running."
  else
    fail "Cron scheduler" "Scheduler ticker is not confirmed running."
  fi
  cron_jobs="$(hermes cron list --all 2>&1 || true)"
  if printf '%s\n' "$cron_jobs" | grep -Eqi 'rf-06|rf06|synthetic acceptance|cek galon'; then
    fail "Cron cleanup" "RF-06 synthetic cron markers remain."
  else
    pass "Cron cleanup" "No RF-06 synthetic cron markers detected."
  fi
fi

dashboard_http="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 2 http://127.0.0.1:8000/health 2>/dev/null || true)"
if [ "$dashboard_http" = "200" ]; then
  pass "Dashboard API" "Optional local health endpoint is healthy."
else
  warn "Dashboard API" "Optional local dashboard API is not running."
fi

printf '\nRuntime summary: %s failure(s), %s warning(s).\n' "$failure_count" "$warning_count"
if [ "$failure_count" -gt 0 ]; then
  exit 1
fi
exit 0
