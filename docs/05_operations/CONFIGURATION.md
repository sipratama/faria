# Configuration — FARIA

> **Scope:** Runtime configuration through RF-06. Hermes and 9Router remain externally managed; FARIA owns the canonical SOUL/Finance/Home Ops skills, Household MCP persistence, and the local read-only dashboard boundary.

## 1. Hermes-Managed Configuration

The accepted Hermes v0.21.2 managed installation reports these active paths on macOS:

| Path | Purpose |
|---|---|
| `~/.hermes/config.yaml` | Hermes model selection, provider endpoint, terminal backend, and other non-secret runtime settings |
| `~/.hermes/.env` | Provider credentials, Telegram bot token, and private Telegram allowlist values |
| `~/Library/LaunchAgents/ai.hermes.gateway.plist` | launchd service definition generated/managed by Hermes gateway setup |

Confirm the paths for the installed Hermes version without printing their contents:

```bash
hermes config path
hermes config env-path
```

Prefer the supported interactive flows:

```bash
hermes model
hermes setup gateway
```

The custom provider endpoint is `http://127.0.0.1:20128/v1`, and the selected logical model is `faria-household-main`. Hermes stores the endpoint credential under a generated environment key; the key name and value are Hermes-managed and must not be copied into FARIA.

The Telegram bot token and explicit allowlist also remain in Hermes-managed configuration. Real numeric Telegram IDs are private operational configuration even though they are not authentication credentials.

Set the FARIA household timezone explicitly to `Asia/Jakarta`; do not rely on the host timezone. Pin scheduled jobs to the logical model path with `cron.model: faria-household-main`. `cron.model_provider` may remain unset when Hermes resolves the same configured custom provider as `model.default`; no physical OpenRouter model belongs in repository documentation.

## 2. FARIA Repository Configuration

The repository-owned Python and Next.js processes support these optional environment variables:

| Setting | Default | Purpose |
|---|---|---|
| `FARIA_DB_PATH` | `~/.faria/data/faria.db` | Shared Household MCP/Dashboard API SQLite path; override for isolated acceptance |
| `FARIA_DASHBOARD_API_URL` | `http://127.0.0.1:8000` | Server-only Next.js base URL for the read-only Dashboard API |

The default and any personal database must remain outside the Git repository. The process creates the parent directory and database with owner-only permissions. No repository `.env`, Compose file, or committed Hermes config is required.

Do not duplicate Hermes or 9Router secrets into this repository for convenience.

`FARIA_DASHBOARD_API_URL` must not use a `NEXT_PUBLIC_` prefix. The RF-05 API host is fixed to `127.0.0.1`; do not expose it through a public bind, reverse proxy, tunnel, or network address. Remote access requires the later authentication/deployment phase.

### Hermes MCP Registration

Register the local stdio server as `faria-household` through `hermes mcp add`. In Hermes-managed `config.yaml`, restrict `tools.include` to exactly the eighteen RF-06 tool names documented in the finance and routine feature specs and set `sampling.enabled: false`. A machine-specific absolute command path is expected locally but must never be copied into repository configuration or documentation as a concrete private path.

Register a second local alias, `faria-household-cron-readonly`, pointing to the same stdio server implementation. Its `tools.include` contains only `routine_get`, and sampling remains disabled. This alias does not duplicate backend code; it limits fresh cron sessions so finance writes and routine mutations are unavailable.

The optional `confirmation_reference` tool field is an untrusted audit label. It does not replace the Telegram allowlist and does not prove which user confirmed an allocation.

### FARIA Identity and Skill Discovery

`agent/prompts/SOUL.md` is the canonical FARIA identity. Synchronize it to the active FARIA profile's Hermes-home `SOUL.md`; this copy is runtime state, not a second independently maintained source.

Configure `skills.external_dirs` in the active Hermes profile with the machine-local absolute path to this repository's `agent/skills`. Do not commit that absolute path. Automatic skill discovery remains enabled so ordinary Indonesian allocation messages can select `faria-finance` and routine/reminder messages can select `faria-home-ops`.

### Household Member Identity

The two conversational aliases are `owner` → Ayah Singgih and `spouse` → Mami Farah. Resolve the current speaker only through local Hermes runtime configuration after Telegram allowlist authorization.

Hermes v0.21.2 supports per-chat ephemeral prompts through `telegram.channel_prompts`. For each authorized private DM, use its private chat ID as the local configuration key and inject only the member code, role, and display name. The prompt is applied on every turn and is not persisted into transcript history, so fresh sessions retain the correct runtime identity. Never commit real Telegram IDs or copy the private mapping into repository documentation.

Display identity is not authorization identity. The explicit Telegram numeric-ID allowlist remains the authorization boundary, and a display name, username, or message such as `Saya Mami Farah` cannot replace the trusted runtime mapping. If no mapping exists, FARIA knows the two household aliases but must not guess the current speaker. Do not use profile-wide `USER.md` or model memory for speaker resolution.

### Telegram Tool Surface

Configure `platform_toolsets.telegram` through supported Hermes configuration/tool commands with only `skills`, `cronjob`, and the primary `faria-household` MCP server. The primary server contributes exactly the eighteen tools in its `tools.include` allowlist. Explicitly naming it prevents Telegram from inheriting the cron-only alias. The developer CLI retains its separate tool configuration.

Configure `skills.platform_disabled.telegram` through Hermes' per-platform skill configuration so unrelated installed skills are hidden from household Telegram sessions. `faria-finance` and `faria-home-ops` remain enabled; Hermes' essential `hermes-agent` skill may also remain visible. This restriction is Telegram-specific and does not remove developer CLI skills.

The Telegram surface must not include `terminal`, `file`, `browser`, `web`, `code_execution`, `delegation`, or `computer_use`. Re-run `hermes tools list --platform telegram` after Hermes upgrades or profile changes to detect configuration drift.

### Hermes Cron Surface

Configure `platform_toolsets.cron` to only `skills` plus the `faria-household-cron-readonly` MCP alias. Per routine job, set `enabled_toolsets` even more explicitly to `skills` and `mcp-faria-household-cron-readonly`. The `mcp-` prefix is Hermes' runtime toolset name for that configured server.

Routine jobs use canonical five-field cron or offset-aware one-shot timestamps, attach `faria-home-ops`, and deliver to `origin`. Every persisted prompt is self-contained and contains only the routine UUID plus instructions to call `routine_get`, return `[SILENT]` unless state is `ACTIVE`, and avoid external/financial actions.

Hermes-managed runtime state owns actual cron jobs, origin/thread delivery metadata, and job IDs. Never commit `~/.hermes/cron/jobs.json`, job IDs, Telegram IDs, credentials, or local executable paths. The dashboard derives next routine from SQLite and never reads this runtime state.

## 3. 9Router Configuration

FARIA owns only these architectural expectations:

- Hermes reaches 9Router through the custom OpenAI-compatible endpoint;
- 9Router exposes the logical combo `faria-household-main` (`FARIA Household`);
- Hermes remains decoupled from any single physical OpenRouter model.

9Router owns its OpenRouter credential and the physical primary/fallback model list. Those values may change without changing FARIA's architecture.

## 4. Security Boundary and Follow-Ups

- only explicitly allowlisted Telegram identities may interact with FARIA;
- Docker remains the Hermes terminal sandbox backend for developer CLI use; Telegram has no terminal toolset;
- the Telegram model surface is restricted to Finance/Home Ops skills, cronjob management, and the eighteen allowlisted `faria-household` tools;
- cron execution is restricted to skills plus read-only `routine_get`; finance writes and system tools are unavailable;
- the owner is configured in both the explicit allowlist and local DM identity mapping; spouse onboarding/testing remains outstanding;
- rejection of a non-allowlisted Telegram identity has not yet been tested.
- stdio MCP calls do not currently carry trustworthy per-Telegram-user identity into Household MCP; Telegram allowlisting remains the external authentication boundary.
- the dashboard is local-only and read-only; it adds no Telegram capability and no financial HTTP operation.
- automatic scheduler reconciliation is not running; `PENDING_SCHEDULE` is inspected/retried through controlled conversation.

Spouse onboarding and an actual rejection test from a non-allowlisted identity remain required before shared household use is considered accepted.

## 5. Related Documents

- `docs/05_operations/DEVELOPER_SETUP.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/standards/08_SECURITY_STANDARD.md`
