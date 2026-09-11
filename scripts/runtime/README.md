# Runtime Verification — FARIA (RF-01)

> RF-01 READY: runtime connectivity is proven for the accepted macOS development topology. This evidence does not cover Household MCP, SQLite, Monthly Allocation, or the dashboard.

## Accepted Topology

```text
Telegram
   ↓
Hermes Gateway (macOS launchd)
   ↓
Hermes Runtime (managed local install)
   ↓
9Router (local Docker/OrbStack :20128)
   ↓
faria-household-main
   ↓
OpenRouter → selected model
```

Hermes tool execution follows a separate path:

```text
Hermes Runtime → Docker terminal sandbox → egress firewall
```

Docker is not the host for Hermes itself in this accepted topology.

## Repeatable Non-Secret Checks

Run on the macOS host:

```bash
scripts/runtime/check-runtime.sh
```

The script checks:

- **A — 9Router endpoint reachable:** `http://127.0.0.1:20128/v1/models` responds; an unauthenticated `401` or `403` still proves endpoint reachability without reading a credential;
- **B — Hermes installed:** `hermes --version` succeeds;
- **C — gateway supervised:** `hermes gateway status` confirms the current launchd service definition is running, without recording its runtime-specific PID.

The script never reads or prints the Hermes credential store. Pass an alternative non-secret models URL as its first argument only when the local 9Router port differs.

## Recorded Manual Acceptance Evidence

The following user-provided RF-01A observations are accepted evidence from the real local environment:

| Path | Prompt | Observed result | Status |
|---|---|---|---|
| macOS host → 9Router | Reach `http://127.0.0.1:20128` | Endpoint reachable | PASS |
| Docker container → host 9Router | Reach `host.docker.internal:20128` | Endpoint reachable | PASS |
| Hermes CLI → 9Router → `faria-household-main` → model | `Balas hanya dengan: FARIA runtime connected` | `FARIA runtime connected` | PASS |
| Telegram → Hermes Gateway → 9Router → `faria-household-main` → model | `Balas hanya dengan: FARIA Telegram connected` | `FARIA Telegram connected` | PASS |
| Hermes Gateway service | `hermes gateway status` | Service definition matched; gateway supervised by launchd | PASS |

These smoke tests prove connectivity only. They do not establish latency, reliability, security, or model-quality guarantees.

## Manual Recheck

For normal chat, run `hermes` on the host and repeat the CLI prompt above.

For Telegram, use an explicitly allowlisted account and repeat the Telegram prompt above. Never paste the bot token, API credentials, or numeric Telegram IDs into this repository or test output.

## Outstanding Operational Checks

- onboard and test the second household member before shared household use;
- verify that a deliberately non-allowlisted Telegram identity is rejected or ignored.

Only one allowlisted household member is currently configured and tested. Do not weaken the allowlist to make the rejection test easier. These follow-ups do not block RF-02 engineering work.
