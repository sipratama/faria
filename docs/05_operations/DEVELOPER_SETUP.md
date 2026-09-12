# Developer Setup — FARIA

> **Scope:** Accepted macOS development path through RF-04: runtime connectivity, Household MCP, repo-owned FARIA identity/Finance skill, Telegram finance workflows, and local household-member identity mapping. The dashboard is not included.

## 1. Prerequisites

- macOS with Docker available through OrbStack or an equivalent Docker runtime;
- a local 9Router instance publishing host port `20128`;
- the official Hermes managed installer;
- Python 3.11+ and `uv` for Household MCP;
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

The server uses local stdio transport and exposes exactly twelve constrained allocation/rules/savings/giving tools. Its default database is `~/.faria/data/faria.db`; set `FARIA_DB_PATH` only when an isolated database is required. Tests always use temporary databases.

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
```

Also set `mcp_servers.faria-household.sampling.enabled` to `false`, because this deterministic domain server never requests model sampling. Then verify:

```bash
hermes mcp test faria-household
hermes mcp list
```

Use a temporary `FARIA_DB_PATH` and synthetic future-period values for manual acceptance; never test against the personal database.

## 9. Repeat Non-Secret Checks

```bash
scripts/runtime/check-runtime.sh
```

See `scripts/runtime/README.md` for the recorded manual acceptance evidence and the still-unverified unauthorized-identity rejection check.

## 10. Activate FARIA Identity and Finance Skill

The repository owns the canonical runtime behavior:

```text
agent/prompts/SOUL.md
agent/skills/faria-finance/SKILL.md
```

Copy the canonical SOUL to the active FARIA profile's Hermes home, then configure that same profile's `skills.external_dirs` with the absolute local path to `agent/skills`. The absolute checkout path is operational configuration and must not be committed. Verify discovery:

```bash
hermes skills list --source local
hermes mcp test faria-household
```

The `faria-finance` skill remains naturally discoverable from ordinary household language; a slash command is not required. Hermes v0.21.2 does not reliably expose MCP toolset availability to external-skill discovery conditions, so the skill documents the twelve `faria-household` tools as a runtime prerequisite rather than using `requires_toolsets` frontmatter.

### Configure Household Member Identity

Use Hermes v0.21.2's supported `telegram.channel_prompts` configuration to inject trusted member context for each authorized private DM. Keep actual DM chat IDs only in Hermes-managed local configuration. Configure the owner as `owner` / `OWNER` / `Ayah Singgih` and, after spouse onboarding, configure the spouse as `spouse` / `SPOUSE` / `Mami Farah`.

For a Telegram private DM, Hermes resolves `channel_prompts` from the DM chat ID on every turn. This makes identity available in fresh sessions without depending on `USER.md`, model memory, Telegram display names, usernames, or self-claimed identity. The matching allowlist entry must already authorize the sender; the prompt itself grants no access.

## 11. Restrict and Refresh Telegram

Use `hermes tools enable|disable --platform telegram` so the effective Telegram surface contains only `skills` and the twelve configured `faria-household` tools. In particular, verify these are disabled:

```text
terminal, file, browser, web, code_execution, delegation, computer_use
```

Do not apply this restriction to the developer CLI.

Also use Hermes' per-platform skill configuration so Telegram enables `faria-finance` and disables unrelated installed skills. Hermes' essential `hermes-agent` operating skill cannot be disabled and may remain visible. Do not disable the developer CLI's skill catalog as part of this persistent configuration.

After SOUL, skill, MCP, toolset, or skill-visibility changes, run:

```bash
hermes gateway restart
hermes tools list --platform telegram
```

Use a fresh Telegram session for final acceptance. Run CLI pre-acceptance with an isolated `FARIA_DB_PATH` and synthetic future-period values; restore the normal MCP configuration and delete the temporary database afterward.

## 12. Related Documents

- `docs/05_operations/CONFIGURATION.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `AGENTS.md`
