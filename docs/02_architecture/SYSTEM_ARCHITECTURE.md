# System Architecture — FARIA

> **Document role:** Authoritative source for the system's high-level technical structure, boundaries, runtime interactions, and architectural invariants.
>
> Product behavior belongs in the PRD and feature specs. Decision rationale belongs in ADRs. Exact public interfaces belong in executable API models. Detailed coding conventions belong in engineering standards.

---

## Document Metadata

| Field | Value |
|---|---|
| Project | FARIA |
| Status | Draft |
| Version | `0.7` |
| Architecture Owner | sipratama |
| Last Updated | `2026-09-12` |

---

## 1. Architecture Summary

### System Purpose

FARIA is a private household AI operating system. A conversational agent runtime (Hermes) interprets Telegram messages from an allowlisted household, orchestrates a small set of household-domain skills/personas, and reads/writes authoritative household state through a constrained Household MCP tool boundary backed by SQLite. A web dashboard gives the household visibility into agent/persona activity.

### Architecture Style

Modular monolith (single Hermes runtime with multiple skills/personas) + a constrained domain-tool service (Household MCP) + a separate read-only dashboard API and Next.js web app.

### Primary Runtime Components

- Telegram (external, human interface)
- Hermes Agent Runtime (conversational orchestration, skills, cron)
- 9Router (model gateway)
- OpenRouter (model provider)
- Household MCP server (domain tool boundary)
- Dashboard API (read-only local HTTP boundary)
- SQLite (authoritative structured store)
- Dashboard (React/Next.js web app, Agent Control Center)
- Encrypted external backup destination (provider TBD)

---

## 2. Architecture Objectives

The architecture should optimize for:

1. Keeping the household's financial state trustworthy and auditable, never solely inferred by an LLM.
2. Letting the household interact conversationally without exposing unrestricted capability to the LLM.
3. Staying portable/deployable on a single always-on host without unnecessary infrastructure.

### Non-Objectives

The architecture is not currently optimized for:

- Multi-tenant SaaS scalability.
- High-throughput/high-concurrency workloads (single household, low request volume).
- Independent multi-agent orchestration between personas (V1 uses one runtime with multiple skills).

---

## 3. System Context

```text
+-------------------+
|  Household Owner  |
|  + Spouse         |
+---------+---------+
          | Telegram private group (allowlisted)
          v
+-------------------+
|   Hermes Runtime  |
| (skills + cron)   |
+---------+---------+
          |
          +--------> 9Router
          |            |
          |            v
          |          faria-household-main
          |            |
          |            v
          |          OpenRouter
          v
+-------------------+
|  Household MCP    |
+---------+---------+
          v
+-------------------+        +------------------+
|      SQLite       |------->|  Encrypted       |
| (authoritative)   |        |  Backup (TBD)   |
+-------------------+        +------------------+
          ^
          | fixed read queries
+---------+---------+
|   Dashboard API   |
+---------+---------+
          ^
          | server-side HTTP
+---------+---------+
| Next.js Dashboard |
+---------+---------+
          ^
          | local browser
+---------+---------+
| Household viewers |
+-------------------+
```

### External Actors

| Actor | Interaction |
|---|---|
| Household Owner | Sends/receives Telegram messages, views dashboard |
| Spouse | Sends/receives Telegram messages, views dashboard |

### External Systems

| System | Purpose | Protocol | Criticality |
|---|---|---|---|
| Telegram Bot API | Conversational interface | HTTPS | High |
| OpenRouter (via 9Router) | LLM inference | HTTPS | High |
| Encrypted backup destination (TBD) | Durable off-host copy of SQLite data | TBD | High |

---

## 4. Runtime View

### Accepted Local Development Runtime (RF-01)

| Component | Responsibility | Technology | Local Execution Unit |
|---|---|---|---|
| Hermes Runtime | Conversational orchestration and model/tool invocation | Hermes Agent managed install | macOS host process |
| Hermes Gateway | Telegram connectivity | Hermes Gateway | macOS launchd service |
| 9Router | Logical model routing and physical model fallback | 9Router | Local Docker/OrbStack container publishing host port `20128` |
| Hermes terminal sandbox | Isolated tool/terminal execution with egress firewall | Docker | Ephemeral sandbox container(s) managed by Hermes |

```text
Telegram
   |
   v
Hermes Gateway (launchd)
   |
   v
Hermes Runtime (managed macOS install)
   |
   v
9Router (Docker/OrbStack :20128)
   |
   v
faria-household-main ---> OpenRouter ---> selected primary/fallback model

Hermes Runtime ---> Docker terminal sandbox ---> egress firewall
```

Docker isolates Hermes terminal/tool execution and runs 9Router; it does not host Hermes itself in the accepted local development topology.

### Implemented and Planned V1 Components

| Component | Responsibility | Technology | Current / Planned Execution Unit |
|---|---|---|---|
| Household MCP (through RF-04 implemented locally) | Twelve constrained allocation/rules/savings/giving tools over stdio | Python 3.11, official MCP SDK, stdlib SQLite | Hermes-managed local stdio process; production unit TBD |
| Dashboard API (RF-05 implemented locally) | Purpose-built read-only household/monitoring queries | FastAPI / Uvicorn | macOS process bound to `127.0.0.1:8000` |
| Dashboard (RF-05 implemented locally) | Read-only Agent Control Center web UI | React / Next.js | Node process bound to loopback; production unit TBD |
| SQLite | Authoritative structured data | SQLite file | Host/volume and backup mechanism TBD before production use |

The logical relationships among Hermes, Household MCP, SQLite, and the dashboard remain as documented throughout this architecture. RF-05 adds the local `Browser -> Next.js -> Dashboard API -> query layer -> SQLite` read path without choosing production packaging.

---

## 5. Frontend Architecture

The dashboard is a React/Next.js web app. It:

- displays observable persona status (Idle/Working/Error), current task, last activity, health, model alias, pending allocation drafts, and a small household snapshot;
- reads household/agent-activity state only through an application/API boundary — it must not read the SQLite file directly.
- polls a same-origin Next.js GET route every ten seconds; the Next.js server calls the local Python API using a server-only base URL.
- labels Home Ops and Planner as not activated, and Gateway/9Router/AI usage as not monitored or not connected rather than fabricating status.

RF-05 uses React component state only for polling/error UX and introduces no client state framework, WebSocket, SSE, or direct database access. 2D/3D visualization remains explicitly out of scope.

### Frontend Boundaries

- The dashboard does not own authoritative business rules or authorization; it reflects state exposed by the backend/API boundary.

---

## 6. Backend Architecture

### Responsibilities

- **Hermes Runtime**: conversational orchestration, intent recognition, presenting drafts, invoking Household MCP tools, running scheduled routines (Hermes Cron).
- **Household MCP**: the only component authorized to validate and mutate authoritative household state in SQLite.
- **Dashboard API**: a separate FastAPI entry point in the Household MCP package, authorized only for fixed dashboard queries over SQLite.

### Module / Domain Boundaries (logical, within Hermes)

| Module | Responsibility | Owns Data? | May Depend On |
|---|---|---:|---|
| Finance Agent (repo skill: `agent/skills/faria-finance/`) | Monthly allocation, financial rules, savings goals/contributions, zakat, sedekah | No | Household MCP |
| Giving Agent (logical persona; currently covered by Finance skill) | Zakat penghasilan, sedekah | No | Household MCP |
| Home Ops Agent (skill) | Routines, maintenance, reminders | No | Household MCP |
| Planner Agent (skill) | Cross-cutting scheduling/summary | No | Household MCP, other skills |
| Household MCP | All of the above domain state | Yes | SQLite |
| Dashboard query/API layer | No authoritative state; read projection only | No | Household MCP-owned query/database layer |

**Important:** Finance Agent, Giving Agent, Home Ops Agent, and Planner Agent are logical personas/skills running inside **one Hermes runtime** in V1 — they are **not** independent autonomous LLM agents. The dashboard may visually represent them as separate staff members, but there is one runtime, one model-gateway path, and one authoritative store behind all four. This may evolve into genuinely independent agents later if real requirements justify it (see Open Architecture Questions, AQ-06).

### Dependency Direction

```text
Telegram (transport)
        ↓
Hermes skills (application)
        ↓
Household MCP (ports/interface to domain state)
        ↓
SQLite (infrastructure)
```

---

## 7. Domain and Data Ownership

### Domain Boundaries

Household MCP owns all authoritative household domain state (allocations, savings, giving records, routines). Hermes skills own no persistent state themselves — they orchestrate and present, but do not write directly to SQLite.

### Data Ownership

| Data / Aggregate | Owning Module | Authoritative Store |
|---|---|---|
| Household / Member profile | Hermes runtime configuration in RF-03B; conceptual Household MCP domain later | No SQLite table yet |
| HouseholdFinancialRules | Household MCP | SQLite |
| MonthlyAllocation / AllocationItem | Household MCP | SQLite |
| SavingsGoal / SavingsContribution | Household MCP | SQLite |
| GivingRecord (zakat/sedekah) | Household MCP | SQLite |
| HouseholdRoutine | Household MCP | SQLite |
| AgentActivity (dashboard feed) | Household MCP | SQLite |
| AgentPersonaState (current monitoring projection) | Household MCP | SQLite |

---

## 8. Data Architecture

### Primary Datastores

| Store | Purpose | Data Type |
|---|---|---|
| SQLite | Authoritative household financial/operational state | Transactional |

No cache or message broker exists in V1.

### Schema Management

Household MCP applies ordered, explicit SQL migrations and records each version plus checksum in SQLite. RF-02 intentionally uses a minimal in-process migration runner rather than a framework.

### Transactions

A confirmed allocation and its line items must be persisted atomically; a draft never partially becomes authoritative.

### Data Retention

Indefinite while the household uses FARIA (see PRD, Data and Privacy Expectations).

### Backup / Recovery Assumptions

The SQLite file must have an encrypted external backup; the application server's local disk is not the sole durable copy. Backup destination/mechanism is an open decision (see Open Architecture Questions).

### Why SQLite (not LLM memory) is authoritative

Hermes/LLM memory is probabilistic and not guaranteed to persist or remain accurate across sessions or model changes. Financial correctness requires a deterministic, auditable, queryable store. SQLite is sufficient for single-household V1 scale and needs no separate database server.

Detailed entity definitions belong in `DATA_MODEL.md`.

---

## 9. API Architecture

### API Style

Household MCP tools remain the constrained mutation interface for Hermes. RF-05 adds a separate local REST-style read boundary for the dashboard, as recorded in `adr/ADR-0001-local-read-only-dashboard-api.md`.

### Contract Source

RF-04 exposes exactly twelve tools: four `monthly_allocation_*` tools plus `financial_rules_get`, `zakat_calculate`, `savings_goal_list`, `savings_goal_create`, `savings_goal_get`, `savings_contribution_record`, `giving_list`, and `giving_record`. The three finance feature specifications own their behavior.

RF-05 exposes exactly three dashboard API operations:

- `GET /health`
- `GET /api/dashboard`
- `GET /api/activities`

There are no POST, PUT, PATCH, or DELETE dashboard routes.

### API Principles

- the LLM never receives raw SQL or shell access;
- every state-changing tool call is scoped to one domain operation;
- draft writes may persist non-authoritative working state;
- material financial changes require an explicit prior human confirmation step before allocation confirmation, savings-goal creation, contribution recording, or giving recording;
- MonthlyAllocation is PLAN only; its confirmation has no automatic SavingsContribution/GivingRecord side effect.

### Error Model

Household MCP distinguishes validation, not-found, invalid-state, and conflict failures. MCP callers must treat tool errors as failed operations and must not claim persistence succeeded.

---

## 10. Event and Async Architecture

Not applicable for V1 — no message broker or asynchronous event contract exists. Hermes Cron handles scheduled/recurring work deterministically without requiring an event bus.

---

## 11. Authentication and Authorization

### Authentication

Telegram identity, restricted by an explicit allowlist (not Telegram-native auth alone).

### Authorization Model

Ownership-based — both allowlisted household members have full access to the shared household context; no differentiated roles in V1.

### Enforcement Boundary

The allowlist check happens before Hermes processes a Telegram message. Household MCP additionally scopes every call to twelve allowed domain operations and enforces validation/state invariants. The current stdio MCP transport does not provide trustworthy per-Telegram-user identity to Household MCP, so an actor/reference supplied to a tool is audit-only and is not an authentication boundary.

### Identity Flow

```text
Telegram user
  ↓
Allowlist check (Hermes)
  ↓
Local runtime member mapping for authorized Telegram DMs
  ↓
Hermes skill processing
  ↓
Household MCP constrained tool boundary
  ↓
SQLite (protected resource)
```

---

## 12. Security and Trust Boundaries

```text
Internet
  |
  | trust boundary
  v
Telegram Bot API
  |
  | trust boundary (allowlist)
  v
Hermes Runtime
  |
  | trust boundary (tool contract)
  v
Household MCP
  |
  | trust boundary
  v
SQLite / Backup
```

### Security Invariants

- secrets (Telegram bot token, OpenRouter/9Router keys) are not committed to source and remain in Hermes-managed or 9Router-managed runtime configuration outside this repository;
- only allowlisted Telegram identities are processed;
- household display aliases are personalization only: current-speaker context is injected from a local Telegram DM mapping after authorization, and message text, Telegram display names, or usernames cannot override it;
- the LLM never receives raw SQL access to authoritative household state; authoritative reads/writes use only Household MCP's constrained tools;
- the household Telegram surface exposes only the repo-owned Finance skill (plus Hermes' non-disableable operating skill) and the twelve allowlisted `faria-household` MCP tools; terminal, file, browser, web, code execution, delegation, and computer-use toolsets remain unavailable there, while the developer CLI is configured separately;
- material financial state changes require explicit human confirmation before becoming authoritative; Household MCP constrains state transitions while Hermes/orchestration remains responsible for interpreting confirmation before calling confirm/create/record tools;
- 9Router and Household MCP are not publicly exposed beyond what Hermes/dashboard need;
- privileged/state-changing Household MCP calls should be auditable (who/when/what).

This summary is the V1 trust-boundary reference. A dedicated Threat Model document (`docs/04_engineering/THREAT_MODEL.md`) is deferred until FARIA's trust boundaries grow beyond this single-household scope.

---

## 13. Caching

Not applicable for V1 — no cache layer exists.

---

## 14. Reliability and Failure Handling

### Timeouts

Hermes → 9Router → OpenRouter calls must have explicit timeout behavior (exact values TBD at implementation).

### Retries

Read-only tools are safe to retry. Repeating `monthly_allocation_confirm` for the same allocation is idempotent. Contribution/giving retries linked to the same allocation reference return the existing record when the amount matches and fail on conflicting amounts.

### Idempotency

Confirming the same allocation twice must not create duplicate authoritative records. Linked ACTUAL savings/giving retries are protected by database uniqueness plus application conflict handling.

### Partial Failure

| Dependency | Failure Behavior | User Impact | Recovery |
|---|---|---|---|
| Household MCP unavailable | Hermes reports failure, does not claim persistence succeeded | User must retry | Retry once MCP is reachable |
| OpenRouter/9Router unavailable | Hermes cannot generate a response | User sees no/delayed reply | Retry once model gateway is reachable |

---

## 15. Observability

### Logs

Structured logs for allocation draft/confirm events and Household MCP tool calls, without logging secrets or unnecessary full financial detail.

### Metrics

Basic AI usage/cost per persona for the dashboard; `allocation_confirmed` counts.

### Health

RF-05 persists active Finance/Giving state as Idle/Working/Error and exposes application/database liveness through `GET /health`. Gateway, 9Router, and AI usage are explicitly not monitored by this endpoint.

---

## 16. Deployment Architecture

### Environments

| Environment | Purpose | Data |
|---|---|---|
| Local | Developer execution | Local/mock |
| Production | Live household usage on a single always-on host | Production |

No separate staging environment is planned yet given single-household scale.

### Local Development Platform

The accepted RF-01 development environment is macOS: Hermes is installed through its official managed installer, the gateway is supervised by launchd, 9Router runs in Docker/OrbStack, and Hermes uses Docker as its terminal sandbox backend with the egress firewall enabled.

### Future Production Platform

Production hosting and packaging remain open. RF-01A does not choose XCodePod versus a paid VPS, containerized versus host-managed Hermes, Docker Compose, systemd, reverse proxy, domain, TLS termination, or backup provider. Those decisions belong to a later deployment batch.

### Configuration

For the accepted local runtime, Hermes configuration and credentials live under its managed `~/.hermes` runtime state, while 9Router owns its OpenRouter credential and physical model fallback list. The canonical FARIA identity is `agent/prompts/SOUL.md`, synchronized operationally to the active profile's `SOUL.md`; the repo skill root is added through Hermes `skills.external_dirs`. Authorized Telegram DMs receive a local-only `telegram.channel_prompts` member context keyed by their private DM chat ID. That context provides the conversational alias after the allowlist check; it does not authorize the sender. Household MCP and the dashboard API read `FARIA_DB_PATH` as an optional database-path override and otherwise use `~/.faria/data/faria.db`. Next.js reads `FARIA_DASHBOARD_API_URL` server-side, defaulting to `http://127.0.0.1:8000`. Machine-specific paths remain outside committed configuration. Secrets and Telegram IDs are never hard-coded or committed.

---

## 17. Scalability

Expected load is a single household (2 users) — negligible request volume. No horizontal scaling, load balancing, or distributed architecture is justified for V1; introducing it would be premature complexity.

---

## 18. Performance Assumptions

No formal performance targets are defined for V1 (see `docs/02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`, not activated). Conversational latency is bounded mainly by the OpenRouter model call; no caching or precomputation is needed at this scale.

---

## 19. Architecture Invariants

### INV-01 — Household MCP is the only writer of authoritative state

Only Household MCP may write authoritative household domain state; Hermes skills must not write to SQLite directly.

### INV-02 — No unrestricted LLM data access

The LLM/agent must never be given raw SQL or shell execution access.

### INV-03 — Confirmation before persistence

A financial allocation (or other material state change) must not be persisted as authoritative without an explicit prior human confirmation step.

### INV-04 — Personas remain logical skills in V1

Finance/Giving/Home Ops/Planner personas remain logical skills within one Hermes runtime unless a future ADR explicitly changes this to independent agents.

### INV-05 — Dashboard reads use a purpose-built API

Browser and Next.js code never access SQLite directly; dashboard data crosses the read-only Dashboard API and query layer.

### INV-06 — RF-05 dashboard is local and read-only

The Dashboard API binds to loopback and exposes only the three documented GET operations. Remote authentication and public deployment remain deferred.

---

## 20. Architecture Decision Records

- `ADR-0001` accepts a separate loopback-only read-only Dashboard API in the existing Household MCP package.

---

## 21. Known Constraints

### Technical Constraints

- SQLite (not PostgreSQL); no Redis/Kafka; single Hermes runtime (no independent multi-agent architecture) for V1.

### Operational Constraints

- The proven development topology is macOS-specific; production hosting and process supervision are not yet finalized.
- The owner DM is configured in the Telegram allowlist and local conversational identity mapping. Spouse onboarding and testing remain prerequisites before shared household use.

### Legacy / Integration Constraints

- None — greenfield project.

### Runtime Constraints Discovered During RF-01

- The accepted Hermes topology is a managed macOS installation with a launchd-supervised gateway, not a FARIA-owned application container.
- RF-03 restricts the Telegram model surface to skills plus `faria-household`; broader developer tools remain limited to the separately configured CLI surface.
- Rejection of a non-allowlisted Telegram identity has not yet been tested; this is an operational security follow-up, not a claim of acceptance.
- Hermes stdio MCP does not currently propagate a trustworthy Telegram-user identity to Household MCP; Telegram allowlisting remains the external authentication boundary, and `confirmation_reference` is audit-only.

---

## 22. Known Architecture Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Single SQLite file/host is a single point of failure | Household financial data loss if the host fails without backup | Encrypted external backup (destination TBD) before production use |
| Model/provider behind the `faria-household-main` combo may change | Inconsistent response quality/latency | Keep Hermes decoupled from a specific physical model through the 9Router-owned combo |
| Future Hermes configuration drift broadens Telegram tools | A household request could reach unnecessary general-purpose capability | Re-check `hermes tools list --platform telegram` after runtime upgrades and keep only skills plus `faria-household` |

---

## 23. Open Architecture Questions

| ID | Question | Decision Needed By | Owner |
|---|---|---|---|
| AQ-01 | Final production hosting and runtime packaging (including XCodePod.Cloud vs. paid VPS and host-managed vs. containerized processes) | Before deployment | Household |
| AQ-02 | Exact Household MCP tool contract shapes | Resolved in RF-02; see monthly-allocation feature spec | Implementation |
| AQ-03 | Migration/schema tooling for SQLite | Resolved in RF-02: ordered SQL files + checksum metadata | Implementation |
| AQ-04 | Encrypted backup destination and mechanism | Before production use | Household |
| AQ-05 | RESOLVED in RF-05 — Next.js App Router with minimal React state and a separate FastAPI read-only API | Implementation | Implementation |
| AQ-06 | Whether personas ever become independent agents | Only if real requirements justify it | Household / Implementation |
| AQ-07 | Telegram tool restriction approach | Resolved in RF-03: per-platform Hermes toolsets expose skills plus `faria-household`; CLI remains separate | Implementation |

When resolved, create an ADR if the decision is architecturally material.

---

## 24. Change Rules

Update this document when: Household MCP's role, Hermes's single-runtime model, SQLite's authoritative role, or the confirmation boundary change; when a new deployable component or trust boundary is introduced; when the hosting/backup decision is finalized.

Do not update this document for routine internal refactoring that preserves the architecture.

---

## 25. Related Documents

- Product Brief: `../00_product/PRODUCT_BRIEF.md`
- PRD: `../00_product/PRD.md`
- Feature Specs: `../01_features/`
- Data Model: `./DATA_MODEL.md`
- Standards: `../standards/`

---

## 26. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.7 | `2026-09-12` | Added the RF-05 local read-only Dashboard API, Next.js boundary, monitoring ownership, and invariants | sipratama |
| 0.6 | `2026-09-12` | Added RF-04 financial rules, savings/giving persistence, twelve-tool boundary, and PLAN-versus-ACTUAL semantics | sipratama |
| 0.5 | `2026-09-12` | Added local Telegram DM member-context mapping and separated display identity from authorization | sipratama |
| 0.4 | `2026-09-12` | Added the repo-owned FARIA identity/Finance skill and restricted Telegram tool/skill surface from RF-03 | sipratama |
| 0.3 | `2026-09-12` | Recorded the RF-02 Household MCP, SQLite migration strategy, tool surface, and confirmation/identity boundaries | sipratama |
| 0.2 | `2026-09-12` | Aligned local runtime topology and RF-01 acceptance with the verified managed Hermes/launchd/9Router setup | sipratama |
| 0.1 | `2026-09-11` | Initial draft | sipratama |
