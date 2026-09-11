# Developer Setup — FARIA

> **Scope:** RF-01 (Runtime Foundation) only — the Hermes → 9Router → model path and the Telegram → Hermes Gateway path. Household MCP, SQLite business schema, Monthly Allocation, and the dashboard app are not part of this setup yet (see `AGENTS.md`).

## 1. Prerequisites

| Tool | Notes |
|---|---|
| Docker Desktop (Windows/macOS) or Docker Engine (Linux) | Runs the Hermes container |
| A running 9Router instance, reachable from your host | RF-01 does not install or configure 9Router itself |
| A Telegram bot token from [@BotFather](https://t.me/BotFather) | Needed only for the Telegram checks |
| The numeric Telegram user IDs of the two allowlisted household members | See `docs/05_operations/CONFIGURATION.md` |

## 2. One-Time: Build the Hermes Image

No public prebuilt Hermes Agent image exists (verified against official docs, 2026-09-11). Build one locally, **outside this repository**:

```bash
git clone https://github.com/NousResearch/hermes-agent /path/outside/faria
cd /path/outside/faria
docker build -t hermes-agent:local .
```

## 3. Configure

1. Copy `.env.example` to `.env` in the repository root and fill in real values. Never commit `.env`.
2. Use `infra/hermes/config.example.yaml` as the reference for `config.yaml` — it lives inside the `hermes_data` Docker volume (`/opt/data/config.yaml`), not in this repository. On first run Hermes creates its own defaults there; edit that file to match the example (model/provider, approvals, terminal isolation, website blocklist).

## 4. Run

From the repository root:

```bash
docker compose -f infra/docker/compose.yaml --env-file .env up -d gateway
```

## 5. Verify

```powershell
scripts\runtime\check-runtime.ps1
```

or

```bash
scripts/runtime/check-runtime.sh
```

Then follow the manual checks (normal chat, Telegram, unauthorized identity) in `scripts/runtime/README.md`.

## 6. Related Documents

- `docs/05_operations/CONFIGURATION.md`
- `scripts/runtime/README.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `AGENTS.md`
