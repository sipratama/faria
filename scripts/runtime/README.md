# Runtime Verification — FARIA (RF-07A)

`scripts/runtime/check-runtime.sh` is the provider-neutral, non-mutating health command for the current personal runtime.

## Checks

It reports `PASS`, `WARN`, or `FAIL` for:

- Python 3.11+ and the Household MCP executable;
- authoritative SQLite presence, read-only open, `integrity_check`, `foreign_key_check`, migration `004`, and restrictive permissions;
- local 9Router `/v1/models` reachability without inference;
- `age` availability and external backup-directory readiness;
- Hermes installation and launchd gateway supervision;
- absence of RF-06 temporary `FARIA_DB_PATH` overrides;
- primary MCP discovery and exactly 18 selected/allowlisted tools;
- cron-readonly MCP discovery and exactly `routine_get` (`CRON_READONLY_OK`);
- exact Telegram and cron platform toolsets;
- disabled dangerous system tools on Telegram and cron;
- Finance/Home Ops skill discovery;
- cron scheduler status and RF-06 synthetic-job marker cleanup;
- optional local dashboard API health.

The dashboard being stopped is a warning. Database corruption, migration drift, gateway supervision failure, MCP/tool drift, cron security drift, or unreachable required runtime dependencies are failures.

## Safety

The script does not:

- mutate household data;
- create or run cron jobs;
- send Telegram messages;
- run a backup;
- invoke model inference;
- print database contents, Telegram IDs, credentials, private keys, full environment data, or full Hermes configuration.

It reads only supported command output and safe configuration keys.

## Usage

```bash
scripts/runtime/check-runtime.sh
```

An alternative non-secret local models endpoint may be supplied as the first argument:

```bash
scripts/runtime/check-runtime.sh http://127.0.0.1:20128/v1/models
```

Run after Hermes upgrades, configuration edits, machine restart, application updates, and RF-07B deployment migration.

## Operational Evidence Boundary

Prior RF-01 connectivity and RF-06 `CRON_READONLY_OK` acceptance remain historical evidence. The script re-checks the lightweight configuration/security boundary but does not send test reminders or perform destructive routine acceptance.

Production/personal reminder delivery should prefer a stable paid primary model behind `faria-household-main`. Physical provider model names remain 9Router-owned configuration and are never checked here.

See `docs/05_operations/RUNBOOK.md` for remediation and recovery procedures.
