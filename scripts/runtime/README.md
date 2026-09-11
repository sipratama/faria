# Runtime Verification — FARIA (RF-01)

> Verifies the Hermes → 9Router → model path, and the Telegram → Hermes Gateway → 9Router → model path. Does not cover Household MCP, SQLite, Monthly Allocation, or the dashboard app — those are later batches (see `AGENTS.md`).

## Before You Start

1. `infra/docker/compose.yaml` requires a locally built Hermes image — no public prebuilt image exists (see `docs/05_operations/DEVELOPER_SETUP.md`).
2. Copy `.env.example` to `.env` in the repo root and fill in real values. Never commit `.env`.
3. A 9Router instance must already be running and reachable from your host; RF-01 does not install or start 9Router itself.

## Automated Checks (A, B)

Run one of:

```powershell
scripts\runtime\check-runtime.ps1
```

```bash
scripts/runtime/check-runtime.sh
```

These check:

- **A — 9Router reachability**: `GET {ROUTER9_BASE_URL}/models`.
- **B — Hermes container running**: `docker ps` for `faria-hermes-gateway`.

Any check that cannot run reports `BLOCKED_BY_LOCAL_CONFIGURATION` with the exact missing prerequisite and the exact next command to run — it is never silently skipped or reported as passing.

## Manual Checks (C, D, E)

These require real credentials, a running model, and/or a second human identity, so they are not scripted.

### Check C — Normal Hermes Chat

Do not proceed to Telegram checks (D, E) if this fails.

```bash
docker exec -it faria-hermes-gateway hermes
```

Then, in the interactive session, send:

```text
Balas hanya dengan: FARIA runtime connected
```

Expected reply: `FARIA runtime connected`.

*Note:* current Hermes docs reference a `single_query_mode` setting for non-interactive contexts, but no verified one-shot CLI flag for scripting this prompt was found while researching RF-01 — hence the interactive `docker exec` approach above rather than a scripted equivalent.

### Check D — Telegram Gateway

1. Confirm both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` are set in `.env` with real values.
2. Start (or restart) the gateway so it picks up the Telegram configuration:
   ```bash
   docker compose -f infra/docker/compose.yaml --env-file .env up -d gateway
   ```
3. From an allowlisted household member's real Telegram account, send the bot:
   ```text
   status FARIA
   ```
4. Confirm a simple, successful reply is received.

### Check E — Unauthorized Identity Rejected

From a **second**, deliberately non-allowlisted Telegram account, send the bot any message.

Expected: the message is not processed as a valid FARIA request (ignored, or a rejection notice, depending on Hermes' default behavior) — the account must not receive normal FARIA responses.

Do not add this second account to `TELEGRAM_ALLOWED_USERS` to make the test "pass." If Hermes does not safely support this check without weakening the allowlist, skip it and record that as an open blocker rather than loosening `TELEGRAM_ALLOWED_USERS`.

## If Something Fails

Report the check name, the exact `BLOCKED_BY_LOCAL_CONFIGURATION` detail (or manual-check outcome), and the next concrete action — never mark RF-01 as fully ready when any of A–D could not actually be verified.
