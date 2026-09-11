# Developer Setup — FARIA

> **Scope:** RF-01 runtime connectivity only. This is the accepted macOS development path; it does not install Household MCP, SQLite business persistence, Monthly Allocation, or the dashboard.

## 1. Prerequisites

- macOS with Docker available through OrbStack or an equivalent Docker runtime;
- a local 9Router instance publishing host port `20128`;
- the official Hermes managed installer;
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

Only one household member has currently been configured and tested. Second household member onboarding remains an operational prerequisite before shared household use.

## 7. Repeat Non-Secret Checks

```bash
scripts/runtime/check-runtime.sh
```

See `scripts/runtime/README.md` for the recorded manual acceptance evidence and the still-unverified unauthorized-identity rejection check.

## 8. Related Documents

- `docs/05_operations/CONFIGURATION.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `AGENTS.md`
