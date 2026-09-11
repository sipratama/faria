# Configuration — FARIA

> **Scope:** RF-01 (Runtime Foundation) only. Real secrets live only in a local, gitignored `.env` — never in this document or in any committed file. Household MCP/SQLite/dashboard configuration will extend this document in a later batch, not replace it.

## 1. Environment Variables

| Variable | Required | Secret? | Purpose |
|---|---:|---:|---|
| `HERMES_IMAGE` | No (defaults to `hermes-agent:local`) | No | Locally built Hermes image tag — see `docs/05_operations/DEVELOPER_SETUP.md` |
| `ROUTER9_BASE_URL` | Yes | No | Base URL of the 9Router instance, as reachable from the Hermes container |
| `OPENAI_API_KEY` | Yes | Yes | 9Router's own credential — Hermes' fixed variable name for any custom OpenAI-compatible provider; **not** an OpenRouter key |
| `TELEGRAM_BOT_TOKEN` | Yes (for Telegram checks) | Yes | Telegram bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_ALLOWED_USERS` | Yes (for Telegram checks) | No* | Comma-separated numeric Telegram user IDs for the two allowlisted household members |

\* Not a credential, but still private runtime configuration under PRD `PR-004` — never commit real IDs.

See `.env.example` for the copyable template.

## 2. Hermes `config.yaml`

`infra/hermes/config.example.yaml` is the annotated reference (model/provider selection, approvals, terminal isolation, website blocklist). It lives inside the `hermes_data` Docker volume as the real `config.yaml` — never as a committed file with real values.

## 3. Precedence

Environment variables (from `.env`, loaded via `--env-file`) → `config.yaml` `${VAR}` substitution → Hermes built-in defaults.

## 4. Known Runtime Limitation

Hermes has no documented config key that fully disables its terminal/shell tool (verified against current official docs). RF-01 mitigates this with `approvals.mode: manual` and `terminal.backend: docker` in `config.example.yaml`, but this is an approval gate, not a hard removal of capability — it must not be treated as equivalent to Household MCP's future tool allowlist (`SYSTEM_ARCHITECTURE.md` `INV-02`).

## 5. Built-In API Server / Dashboard

Left disabled by default. `API_SERVER_HOST`/`API_SERVER_KEY` are intentionally not in `.env.example` — do not enable them without reviewing `docs/02_architecture/SYSTEM_ARCHITECTURE.md` (Security and Trust Boundaries) first.

## 6. Related Documents

- `docs/05_operations/DEVELOPER_SETUP.md`
- `.env.example`
- `infra/hermes/config.example.yaml`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/standards/08_SECURITY_STANDARD.md`
