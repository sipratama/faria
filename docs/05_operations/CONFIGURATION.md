# Configuration — FARIA

> **Scope:** Runtime configuration through RF-03B. Hermes and 9Router remain externally managed; FARIA owns the canonical SOUL/Finance skill and Household MCP owns one optional runtime setting.

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

## 2. FARIA Repository Configuration

Household MCP is the first repository-owned process. It supports one optional environment variable:

| Setting | Default | Purpose |
|---|---|---|
| `FARIA_DB_PATH` | `~/.faria/data/faria.db` | Override the SQLite path for isolated development/manual acceptance |

The default and any personal database must remain outside the Git repository. The process creates the parent directory and database with owner-only permissions. No repository `.env`, Compose file, or committed Hermes config is required.

Do not duplicate Hermes or 9Router secrets into this repository for convenience.

### Hermes MCP Registration

Register the local stdio server as `faria-household` through `hermes mcp add`. In Hermes-managed `config.yaml`, restrict `tools.include` to the four RF-02 tool names documented in `docs/01_features/monthly-allocation.md` and set `sampling.enabled: false`. A machine-specific absolute command path is expected locally but must never be copied into repository configuration or documentation as a concrete private path.

The optional `confirmation_reference` tool field is an untrusted audit label. It does not replace the Telegram allowlist and does not prove which user confirmed an allocation.

### FARIA Identity and Skill Discovery

`agent/prompts/SOUL.md` is the canonical FARIA identity. Synchronize it to the active FARIA profile's Hermes-home `SOUL.md`; this copy is runtime state, not a second independently maintained source.

Configure `skills.external_dirs` in the active Hermes profile with the machine-local absolute path to this repository's `agent/skills`. Do not commit that absolute path. Automatic skill discovery remains enabled so ordinary Indonesian allocation messages can select `faria-finance`.

### Household Member Identity

The two conversational aliases are `owner` → Ayah Singgih and `spouse` → Mami Farah. Resolve the current speaker only through local Hermes runtime configuration after Telegram allowlist authorization.

Hermes v0.21.2 supports per-chat ephemeral prompts through `telegram.channel_prompts`. For each authorized private DM, use its private chat ID as the local configuration key and inject only the member code, role, and display name. The prompt is applied on every turn and is not persisted into transcript history, so fresh sessions retain the correct runtime identity. Never commit real Telegram IDs or copy the private mapping into repository documentation.

Display identity is not authorization identity. The explicit Telegram numeric-ID allowlist remains the authorization boundary, and a display name, username, or message such as `Saya Mami Farah` cannot replace the trusted runtime mapping. If no mapping exists, FARIA knows the two household aliases but must not guess the current speaker. Do not use profile-wide `USER.md` or model memory for speaker resolution.

### Telegram Tool Surface

Configure `platform_toolsets.telegram` through supported `hermes tools --platform telegram` commands. Its native toolset is only `skills`; the enabled `faria-household` MCP server contributes exactly the four tools in its `tools.include` allowlist. The developer CLI retains its separate tool configuration.

Configure `skills.platform_disabled.telegram` through Hermes' per-platform skill configuration so unrelated installed skills are hidden from household Telegram sessions. `faria-finance` remains enabled; Hermes' essential `hermes-agent` skill may also remain visible. This restriction is Telegram-specific and does not remove developer CLI skills.

The Telegram surface must not include `terminal`, `file`, `browser`, `web`, `code_execution`, `delegation`, or `computer_use`. Re-run `hermes tools list --platform telegram` after Hermes upgrades or profile changes to detect configuration drift.

## 3. 9Router Configuration

FARIA owns only these architectural expectations:

- Hermes reaches 9Router through the custom OpenAI-compatible endpoint;
- 9Router exposes the logical combo `faria-household-main` (`FARIA Household`);
- Hermes remains decoupled from any single physical OpenRouter model.

9Router owns its OpenRouter credential and the physical primary/fallback model list. Those values may change without changing FARIA's architecture.

## 4. Security Boundary and Follow-Ups

- only explicitly allowlisted Telegram identities may interact with FARIA;
- Docker remains the Hermes terminal sandbox backend for developer CLI use; Telegram has no terminal toolset;
- the Telegram model surface is restricted to skills plus the four allowlisted `faria-household` tools;
- the owner is configured in both the explicit allowlist and local DM identity mapping; spouse onboarding/testing remains outstanding;
- rejection of a non-allowlisted Telegram identity has not yet been tested.
- stdio MCP calls do not currently carry trustworthy per-Telegram-user identity into Household MCP; Telegram allowlisting remains the external authentication boundary.

Spouse onboarding and an actual rejection test from a non-allowlisted identity remain required before shared household use is considered accepted.

## 5. Related Documents

- `docs/05_operations/DEVELOPER_SETUP.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/standards/08_SECURITY_STANDARD.md`
