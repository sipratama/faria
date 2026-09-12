# ADR-0001 — Local Read-Only Dashboard API

## Metadata

| Field | Value |
|---|---|
| ADR | `ADR-0001` |
| Status | Accepted |
| Date | `2026-09-12` |
| Decision Owners | sipratama |
| Related Requirements | `CAP-DASH-001`, RF-05 |
| Supersedes | N/A |
| Superseded By | N/A |

## 1. Context

The Next.js dashboard needs deterministic household and agent-monitoring reads, but browser code must not access SQLite or consume the local stdio MCP transport. Household MCP must remain the only authority for financial mutations, and RF-05 is local development only.

## 2. Decision Drivers

1. Preserve the SQLite and Household MCP ownership boundaries.
2. Keep the dashboard read-only and purpose-built.
3. Minimize local operational and security complexity.

## 3. Considered Options

### Browser or Next.js reads SQLite directly

Rejected because it duplicates data access and exposes persistence details outside the owning Python package.

### Convert Household MCP to HTTP

Rejected because Hermes depends on the existing stdio MCP contract and the dashboard is not an MCP client.

### Separate read-only HTTP entry point in the Household MCP package

Accepted because it reuses the database/query layer while separating dashboard HTTP reads from the unchanged stdio mutation interface.

## 4. Decision

RF-05 uses this direction:

```text
Browser → Next.js → loopback-only FastAPI dashboard API → query layer → SQLite
```

The FastAPI process exposes exactly `GET /health`, `GET /api/dashboard`, and `GET /api/activities`, binds to `127.0.0.1`, and has no financial mutation routes. Next.js uses a server-only API base URL and proxies browser polling through its same-origin GET route.

## 5. Consequences

- The stdio Household MCP server and its twelve-tool Telegram allowlist remain unchanged.
- The local environment runs one additional Python process and one Next.js process.
- RF-05 does not provide remote authentication, TLS, public hosting, or live Hermes/9Router/usage integration.
- The dashboard API must not be exposed to a LAN or the internet before later authentication and deployment hardening.

## 6. Architecture Invariants

- `INV-05` — Dashboard reads cross a purpose-built, read-only application API; browser and Next.js code never access SQLite directly.
- `INV-06` — The RF-05 dashboard API binds only to loopback and exposes no state-changing HTTP methods.

## 7. Validation

- Backend route tests verify the exact three-route GET surface and reject mutation methods.
- Frontend tests verify health, persona activation, activity, pending-confirmation, and outage states.
- Synthetic local acceptance traces an MCP mutation through AgentActivity, API, and rendered dashboard.

## 8. Decision History

| Date | Status | Change |
|---|---|---|
| `2026-09-12` | Accepted | RF-05 implementation validated the local read-only boundary |
