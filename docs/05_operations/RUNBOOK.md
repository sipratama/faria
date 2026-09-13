# Operations Runbook — FARIA

> **Status:** Activated in RF-07A for the personal macOS runtime. Remote deployment remains deferred to RF-07B.

This runbook is for the household operator. It keeps personal household data private, avoids destructive automation, and uses only provider-neutral local commands.

## 1. Quick Health Check

From the repository root:

```bash
scripts/runtime/check-runtime.sh
```

Interpretation:

- `PASS`: required state is healthy;
- `WARN`: optional service or operational prerequisite needs attention but no corruption is proven;
- `FAIL`: a critical runtime, security, database, or configuration check failed; resolve it before relying on FARIA.

The script is non-mutating. It does not create records/jobs, send Telegram messages, run backups, print database contents, or dump Hermes configuration.

## 2. Is FARIA Running?

```bash
hermes gateway status
hermes cron status
hermes mcp list
```

The accepted personal topology expects the gateway to be supervised by launchd. A detached process with an unloaded service is not the desired steady state.

Restart the installed service with:

```bash
hermes gateway stop
hermes gateway start
hermes gateway status
```

If a stale detached process remains, inspect it before using `hermes gateway start --all`; that option affects every local Hermes profile.

Expected crash recovery: launchd restarts the installed gateway service. The dashboard API and Next.js dashboard remain optional local development processes in RF-07A.

## 3. Is Household MCP and SQLite Healthy?

```bash
hermes mcp test faria-household
hermes mcp test faria-household-cron-readonly
scripts/runtime/check-runtime.sh
```

The check opens SQLite read-only and verifies `PRAGMA integrity_check`, `PRAGMA foreign_key_check`, and the applied migration level. It never prints financial or routine data.

If the migration level is older than the repository baseline, stop and review the upgrade path before allowing a normal Household MCP startup to migrate the personal database. Take and verify an encrypted backup first.

## 4. Are 9Router and Tool Restrictions Healthy?

```bash
hermes tools list --platform telegram
hermes tools list --platform cron
hermes config get platform_toolsets.telegram --json
hermes config get platform_toolsets.cron --json
```

Expected:

- Telegram: `skills`, `cronjob`, and `faria-household` only;
- cron: `skills` and `faria-household-cron-readonly` only;
- primary MCP: exactly 18 selected tools;
- cron alias: exactly `routine_get`;
- terminal, file, browser, web, code execution, delegation, and computer-use tools disabled on Telegram and cron.

This lightweight check preserves the RF-06 `CRON_READONLY_OK` design. Re-run it after every Hermes upgrade, configuration edit, and deployment migration. Do not run a destructive routine acceptance on every health check.

## 5. Take an Encrypted Backup

Prerequisites:

- install `age` using an operator-managed package source (`brew install age` on the accepted macOS/Homebrew environment);
- keep the private recovery identity outside this repository;
- configure an existing external directory not located only beside the live database.

```bash
export FARIA_BACKUP_DIR="/operator/chosen/external/location"
export FARIA_BACKUP_RECIPIENT="age1publicrecipient"
household-mcp/.venv/bin/python scripts/operations/backup_faria.py
```

The script resolves the database from `--source`, then `FARIA_DB_PATH`, then `~/.faria/data/faria.db`. It requires the backup directory to exist, creates a consistent SQLite snapshot using `sqlite3.Connection.backup()`, verifies integrity and foreign keys, encrypts with `age`, publishes the artifact atomically, writes a non-sensitive checksum manifest, removes plaintext staging data, and retains the latest 14 FARIA backups.

A backup stored only on the same disk as the live database is not a durable external backup.

## 6. Verify a Backup

```bash
export FARIA_BACKUP_IDENTITY="/operator/private/recovery-key.txt"
household-mcp/.venv/bin/python scripts/operations/verify_restore.py \
  "$FARIA_BACKUP_DIR/faria-YYYYMMDDTHHMMSSZ.sqlite.age"
```

Verification checks the encrypted checksum manifest when present, decrypts only into restrictive temporary storage, runs SQLite integrity/foreign-key checks, verifies required tables and migration metadata, and deletes the plaintext temporary database. It never replaces the live database.

## 7. Manual Disaster Recovery

Do not overwrite the live database with an automated one-liner.

1. Stop/quiesce Household MCP and Hermes writers.
2. Create an emergency encrypted pre-restore backup if the current database remains readable.
3. Select a known-good backup and run `verify_restore.py`.
4. Decrypt the selected artifact into a restrictive operator-controlled temporary directory.
5. Re-run `PRAGMA integrity_check`, `PRAGMA foreign_key_check`, and migration checks against the decrypted database.
6. Move the current database aside with a timestamp; do not delete it.
7. Atomically place the restored database at the configured authoritative path.
8. Set the database directory to `0700` and database file to `0600` where POSIX permissions apply.
9. Restart Household MCP/Hermes through the normal gateway service.
10. Run `scripts/runtime/check-runtime.sh` and one harmless allowlisted conversational smoke test.
11. Retain the displaced database until household recovery is explicitly accepted.

## 8. Failure Procedures

- **Gateway failure:** check `hermes gateway status`, review existing Hermes logs, stop/start the installed service, then verify MCP and cron status.
- **9Router failure:** verify only the local `/v1/models` endpoint and 9Router container state. Do not pin operations to a physical provider model.
- **Database integrity failure:** stop writers, preserve the file and WAL/SHM sidecars, do not run ad-hoc repair against the only copy, and recover from a verified encrypted backup.
- **Backup failure:** treat any non-zero exit as no successful backup. Fix the missing source/destination, integrity failure, or `age` error and retry.
- **Restore verification failure:** do not use that artifact. Try another known-good backup and preserve failure evidence without exposing contents.

## 9. Secrets and Logs

Ownership:

- Hermes-managed: Telegram bot token, custom endpoint credential, allowlist/member mapping, runtime configuration;
- 9Router-managed: OpenRouter/provider credentials and physical model routing;
- operator-managed: backup encryption private identity and external backup destination access;
- repository: no runtime secrets and no private recovery key.

Use `hermes logs`, `hermes logs errors`, launchd status, and the existing local service stdout/stderr for troubleshooting. Do not paste full configuration, environment dumps, message content, financial data, credentials, Telegram IDs, private keys, or database contents into logs or tickets.

## 10. Upgrade Checklist

Before upgrading Hermes or FARIA:

1. create a successful encrypted backup;
2. verify that backup restores;
3. confirm a clean Git state;
4. run the runtime check;
5. record the installed Hermes version without credentials.

After upgrading:

1. verify gateway supervision;
2. test both MCP aliases and tool counts;
3. verify Telegram and cron tool restrictions;
4. verify Finance/Home Ops skill discovery;
5. verify cron scheduler status and `CRON_READONLY_OK`;
6. run one harmless allowlisted conversational smoke test.

Never auto-upgrade Hermes from repository scripts.

## 11. RF-07B Readiness Decisions

The operator must select or confirm these before remote deployment:

- hosting provider and Linux distribution/runtime;
- persistent volume/database path;
- external encrypted backup destination;
- dashboard domain/TLS requirement, if remote access is wanted;
- remote dashboard authentication;
- 9Router placement on the same or a separate host;
- Telegram/Hermes runtime placement;
- Docker or Podman availability and service supervision.

RF-07A does not choose or provision any of them.

## Related Documents

- `docs/05_operations/DEVELOPER_SETUP.md`
- `docs/05_operations/CONFIGURATION.md`
- `docs/05_operations/DEPLOYMENT.md`
- `scripts/runtime/README.md`
