# Developer Setup — FARIA

> **Scope:** Accepted macOS development path through RF-05: runtime connectivity, Household MCP, repo-owned FARIA identity/Finance skill, Telegram finance workflows, local household-member identity mapping, and the read-only Agent Control Center.

## 1. Prerequisites

- macOS with Docker available through OrbStack or an equivalent Docker runtime;
- a local 9Router instance publishing host port `20128`;
- the official Hermes managed installer;
- Python 3.11+ and `uv` for Household MCP;
- Node.js 22+ and npm for the Next.js dashboard;
- a Telegram BotFather token and explicit household-user allowlist for gateway setup.

Keep all API credentials, bot tokens, and Telegram user IDs outside this repository.

## 2. Install Hermes

Use the official Hermes managed installer/setup flow rather than building a FARIA-owned container image. Verify the resulting installation:

```bash
hermes --version
```

The RF-01 acceptance environment used Hermes Agent v0.21.2, installed as `~/.local/bin/hermes` with its managed source under `~/.hermes/hermes-agent`. These paths are observations from the accepted environment, not repository-managed installation targets.

## 3. Connect Hermes to 9Router

Ensure 9Router is running and reachable from the macOS host at:

```text
http://127.0.0.1:20128
```

Run:

```bash
hermes model
```

Configure:

| Setting | Value |
|---|---|
| Provider type | Custom OpenAI-compatible endpoint |
| API base URL | `http://127.0.0.1:20128/v1` |
| Compatibility mode | Auto-detect |
| Logical model | `faria-household-main` |
| Display name | `FARIA Household` |

9Router must expose the `faria-household-main` logical combo. Its OpenRouter credentials and physical primary/fallback models remain 9Router-owned runtime configuration. Hermes stores the custom endpoint credential outside this repository.

## 4. Isolate Terminal Execution

During Hermes setup, select Docker as the terminal backend and enable the egress firewall. Docker isolates Hermes tool/terminal execution; Hermes itself remains a managed macOS process in this topology.

## 5. Verify Normal Chat

Start Hermes from the host:

```bash
hermes
```

Send:

```text
Balas hanya dengan: FARIA runtime connected
```

Expected response:

```text
FARIA runtime connected
```

This is connectivity evidence only; it is not a performance, reliability, or model-quality benchmark.

## 6. Configure Telegram

After normal chat succeeds, run:

```bash
hermes setup gateway
```

Use manual setup, store the BotFather token in Hermes-managed configuration, and configure only explicit household user IDs. Then verify:

```bash
hermes gateway status
```

On the accepted macOS topology, the gateway is supervised by launchd through `~/Library/LaunchAgents/ai.hermes.gateway.plist`. PIDs are runtime-specific and are not configuration.

From an allowlisted account, send:

```text
Balas hanya dengan: FARIA Telegram connected
```

Expected response:

```text
FARIA Telegram connected
```

Only the owner account is currently configured and tested. The spouse account must be added to the same explicit allowlist before its identity mapping can be configured and tested.

## 7. Install and Test Household MCP

From the repository root:

```bash
cd household-mcp
uv sync
uv run pytest
```

The server uses local stdio transport and exposes exactly eighteen constrained finance/routine tools. Its default database is `~/.faria/data/faria.db`; set `FARIA_DB_PATH` only when an isolated database is required. Tests always use temporary databases.

## 8. Register Household MCP with Hermes

After automated tests pass, register the environment's console entry point with the supported Hermes CLI:

```bash
hermes mcp add faria-household \
  --command "$(pwd)/.venv/bin/faria-household-mcp"
```

The command above is run from `household-mcp/`. The resulting absolute path belongs only in Hermes-managed local configuration and must not be committed. Configure `mcp_servers.faria-household.tools.include` to exactly:

```text
monthly_allocation_get
monthly_allocation_save_draft
monthly_allocation_confirm
monthly_allocation_discard_draft
financial_rules_get
zakat_calculate
savings_goal_list
savings_goal_create
savings_goal_get
savings_contribution_record
giving_list
giving_record
routine_list
routine_get
routine_create
routine_scheduler_link
routine_complete
routine_cancel
```

Also set `mcp_servers.faria-household.sampling.enabled` to `false`, because this deterministic domain server never requests model sampling. Then verify:

```bash
hermes mcp test faria-household
hermes mcp list
```

Use a temporary `FARIA_DB_PATH` and synthetic future-period values for manual acceptance; never test against the personal database.

## 9. Run the Local Agent Control Center

The dashboard API and Next.js process are local development services. Never bind or proxy them to a LAN or the internet before the later deployment/authentication hardening phase.

From `household-mcp/`, start the read-only API against the intended database:

```bash
FARIA_DB_PATH=/path/to/isolated-faria.db uv run faria-dashboard-api
```

The console entry point always binds to `127.0.0.1:8000` and exposes only:

```text
GET /health
GET /api/dashboard
GET /api/activities
```

From `web/`, install and start Next.js:

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:3000`. The browser polls the same-origin Next.js route every ten seconds; only the Next.js server calls the Python API. Stop the API to verify the explicit unavailable state. Use a temporary SQLite database and synthetic values for acceptance.

Run frontend checks with:

```bash
npm run lint
npm run type-check
npm test
npm run build
```

## 10. Repeat Non-Secret Checks

```bash
scripts/runtime/check-runtime.sh
```

See `scripts/runtime/README.md` for the recorded manual acceptance evidence and the still-unverified unauthorized-identity rejection check.

## 11. Activate FARIA Identity and Skills

The repository owns the canonical runtime behavior:

```text
agent/prompts/SOUL.md
agent/skills/faria-finance/SKILL.md
agent/skills/faria-home-ops/SKILL.md
```

Copy the canonical SOUL to the active FARIA profile's Hermes home, then configure that same profile's `skills.external_dirs` with the absolute local path to `agent/skills`. The absolute checkout path is operational configuration and must not be committed. Verify discovery:

```bash
hermes skills list --source local
hermes mcp test faria-household
```

The `faria-finance` and `faria-home-ops` skills remain naturally discoverable from ordinary household language; slash commands are not required. Hermes v0.21.2 does not reliably expose MCP toolset availability to external-skill discovery conditions, so each skill documents its `faria-household` prerequisites instead of using `requires_toolsets` frontmatter.

### Configure Household Member Identity

Use Hermes v0.21.2's supported `telegram.channel_prompts` configuration to inject trusted member context for each authorized private DM. Keep actual DM chat IDs only in Hermes-managed local configuration. Configure the owner as `owner` / `OWNER` / `Ayah Singgih` and, after spouse onboarding, configure the spouse as `spouse` / `SPOUSE` / `Mami Farah`.

For a Telegram private DM, Hermes resolves `channel_prompts` from the DM chat ID on every turn. This makes identity available in fresh sessions without depending on `USER.md`, model memory, Telegram display names, usernames, or self-claimed identity. The matching allowlist entry must already authorize the sender; the prompt itself grants no access.

## 12. Restrict and Refresh Telegram

Use supported Hermes configuration/tool commands so the effective Telegram surface contains only `skills`, `cronjob`, and the eighteen configured primary `faria-household` tools. Explicitly scope Telegram to the primary alias so it does not inherit the cron read-only alias. In particular, verify these are disabled:

```text
terminal, file, browser, web, code_execution, delegation, computer_use
```

Do not apply this restriction to the developer CLI.

Also use Hermes' per-platform skill configuration so Telegram enables `faria-finance` and `faria-home-ops` and disables unrelated installed skills. Hermes' essential `hermes-agent` operating skill cannot be disabled and may remain visible. Do not disable the developer CLI's skill catalog as part of this persistent configuration.

After SOUL, skill, MCP, toolset, or skill-visibility changes, run:

```bash
hermes gateway restart
hermes tools list --platform telegram
```

Use a fresh Telegram session for final acceptance. Run CLI pre-acceptance with an isolated `FARIA_DB_PATH` and synthetic future-period values; restore the normal MCP configuration and delete the temporary database afterward.

## 13. Configure and Verify Household Cron

Hermes v0.21.2 supports one-shot timestamps, five-field cron schedules, pause/resume/remove, manual run, attached skills, per-job `enabled_toolsets`, pinned cron models, and `origin` delivery. Configure local runtime state without committing `~/.hermes/config.yaml`:

```bash
hermes config set timezone Asia/Jakarta
hermes config set cron.model faria-household-main
hermes config set platform_toolsets.telegram '["skills", "cronjob", "faria-household"]'
hermes config set platform_toolsets.cron '["skills", "faria-household-cron-readonly"]'
```

From `household-mcp/`, register the same implementation under a read-only alias and restrict it:

```bash
hermes mcp add faria-household-cron-readonly \
  --command "$(pwd)/.venv/bin/faria-household-mcp"
hermes config set mcp_servers.faria-household-cron-readonly.tools.include '["routine_get"]'
hermes config set mcp_servers.faria-household-cron-readonly.sampling.enabled false
```

Verify effective surfaces and discovery:

```bash
hermes mcp test faria-household
hermes mcp test faria-household-cron-readonly
hermes mcp list
hermes skills list --source local
hermes tools list --platform telegram
hermes tools list --platform cron
hermes cron status
hermes cron list
```

Routine cron jobs must use `deliver=origin`, attach `faria-home-ops`, and explicitly set per-job toolsets to `skills` and `mcp-faria-household-cron-readonly`. The self-contained prompt reads `routine_get` and emits only `[SILENT]` unless authoritative state is `ACTIVE`.

For local acceptance, temporarily point both aliases to an isolated `FARIA_DB_PATH`, create only synthetic routines/jobs, and restore the normal MCP configuration afterward. Safe cleanup is:

```bash
hermes cron list
hermes cron remove <synthetic-job-id>
hermes cron status
```

Delete the temporary database only after every synthetic job is removed. Restart the gateway with the installed supported command, then confirm a synthetic recurring job remains listed before final cleanup. Never use the household's real database for acceptance and never commit cron job IDs, Telegram IDs, `jobs.json`, or runtime SQLite files.

## 14. Related Documents

- `docs/05_operations/CONFIGURATION.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `AGENTS.md`
