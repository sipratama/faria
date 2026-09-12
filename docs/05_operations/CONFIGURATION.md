# Configuration — FARIA

> **Scope:** RF-01 runtime connectivity plus RF-02 Household MCP runtime configuration. Hermes and 9Router remain externally managed; Household MCP has one optional repository-owned runtime setting.

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

## 3. 9Router Configuration

FARIA owns only these architectural expectations:

- Hermes reaches 9Router through the custom OpenAI-compatible endpoint;
- 9Router exposes the logical combo `faria-household-main` (`FARIA Household`);
- Hermes remains decoupled from any single physical OpenRouter model.

9Router owns its OpenRouter credential and the physical primary/fallback model list. Those values may change without changing FARIA's architecture.

## 4. Security Boundary and Follow-Ups

- only explicitly allowlisted Telegram identities may interact with FARIA;
- Docker is the Hermes terminal sandbox backend and the egress firewall is enabled in the accepted setup;
- Hermes still exposes general-purpose tools and skills beyond FARIA's intended household scope, so tighter tool/skill restriction remains a later security-hardening task;
- one household member is configured and tested; spouse onboarding/testing remains outstanding;
- rejection of a non-allowlisted Telegram identity has not yet been tested.
- stdio MCP calls do not currently carry trustworthy per-Telegram-user identity into Household MCP; Telegram allowlisting remains the external authentication boundary.

These operational checks do not block RF-02 engineering work, but they must be completed before shared household use is considered accepted.

## 5. Related Documents

- `docs/05_operations/DEVELOPER_SETUP.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/standards/08_SECURITY_STANDARD.md`
