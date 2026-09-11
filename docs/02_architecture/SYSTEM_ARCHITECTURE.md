# System Architecture — FARIA

> **Document role:** Authoritative source for the system's high-level technical structure, boundaries, runtime interactions, and architectural invariants.
>
> Product behavior belongs in the PRD and feature specs. Decision rationale belongs in ADRs (none yet). Exact public interfaces belong in machine-readable contracts (not created yet). Detailed coding conventions belong in engineering standards.

---

## Document Metadata

| Field | Value |
|---|---|
| Project | FARIA |
| Status | Draft |
| Version | `0.2` |
| Architecture Owner | sipratama |
| Last Updated | `2026-09-12` |

---

## 1. Architecture Summary

### System Purpose

FARIA is a private household AI operating system. A conversational agent runtime (Hermes) interprets Telegram messages from an allowlisted household, orchestrates a small set of household-domain skills/personas, and reads/writes authoritative household state through a constrained Household MCP tool boundary backed by SQLite. A web dashboard gives the household visibility into agent/persona activity.

### Architecture Style

Modular monolith (single Hermes runtime with multiple skills/personas) + a separate constrained domain-tool service (Household MCP) + a separate dashboard web app.

### Primary Runtime Components

- Telegram (external, human interface)
- Hermes Agent Runtime (conversational orchestration, skills, cron)
- 9Router (model gateway)
- OpenRouter (model provider)
- Household MCP server (domain tool boundary)
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
          | read via application/API boundary
+-------------------+
|     Dashboard     |
| (Agent Control    |
|  Center)          |
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

### Planned V1 Components

| Component | Responsibility | Technology | Production Deployment Unit |
|---|---|---|---|
| Household MCP | Constrained domain tool server for authoritative state | Custom MCP server | TBD before implementation/deployment |
| Dashboard | Agent Control Center web UI | React / Next.js | TBD before deployment |
| SQLite | Authoritative structured data | SQLite file | Host/volume and backup mechanism TBD before production use |

The logical relationships among Hermes, Household MCP, SQLite, and the dashboard remain as documented throughout this architecture. RF-01A does not choose production packaging for them.

---

## 5. Frontend Architecture

The dashboard is a React/Next.js web app. It:

- displays persona status (Idle/Working/Scheduled/Error), current/last task, last activity, next scheduled task, health, model alias, basic AI usage/cost, and pending confirmations;
- reads household/agent-activity state only through an application/API boundary — it must not read the SQLite file directly.

Exact component structure and client-state-management choices are not fixed yet (see Open Architecture Questions); no speculative structure is defined here. 2D/3D visualization is explicitly out of scope for V1 (see Product Brief Non-Goals).

### Frontend Boundaries

- The dashboard does not own authoritative business rules or authorization; it reflects state exposed by the backend/API boundary.

---

## 6. Backend Architecture

### Responsibilities

- **Hermes Runtime**: conversational orchestration, intent recognition, presenting drafts, invoking Household MCP tools, running scheduled routines (Hermes Cron).
- **Household MCP**: the only component authorized to validate and mutate authoritative household state in SQLite.

### Module / Domain Boundaries (logical, within Hermes)

| Module | Responsibility | Owns Data? | May Depend On |
|---|---|---:|---|
| Finance Agent (skill) | Monthly allocation, household budget, personal allowances | No | Household MCP |
| Giving Agent (skill) | Zakat penghasilan, sedekah | No | Household MCP |
| Home Ops Agent (skill) | Routines, maintenance, reminders | No | Household MCP |
| Planner Agent (skill) | Cross-cutting scheduling/summary | No | Household MCP, other skills |
| Household MCP | All of the above domain state | Yes | SQLite |

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
| Household / Member profile | Household MCP | SQLite |
| MonthlyAllocation / AllocationItem | Household MCP | SQLite |
| SavingsGoal / SavingsContribution | Household MCP | SQLite |
| GivingRecord (zakat/sedekah) | Household MCP | SQLite |
| HouseholdRoutine | Household MCP | SQLite |
| AgentActivity (dashboard feed) | Household MCP (ownership TBD, see Open Architecture Questions) | SQLite |

---

## 8. Data Architecture

### Primary Datastores

| Store | Purpose | Data Type |
|---|---|---|
| SQLite | Authoritative household financial/operational state | Transactional |

No cache or message broker exists in V1.

### Schema Management

Persistent schema changes are managed through version-controlled migrations. Exact migration tooling is not yet selected (see Open Architecture Questions).

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

Household MCP tools (constrained, function-call-style interface for the LLM — not open REST) plus a conventional application/API boundary between the dashboard and backend state. The exact dashboard API style (REST vs. RPC) is not fixed yet (see Open Architecture Questions).

### Contract Source

Household MCP tool contracts, expected to include operations such as `create_monthly_allocation`, `get_current_allocation`, `confirm_monthly_allocation`, `create_savings_goal`, `record_savings_contribution`, `get_savings_progress`, `record_zakat`, `record_sedekah`, `create_household_routine`, `complete_household_routine`, and `get_household_summary`. Exact parameter/response shapes are refined during implementation, not invented here.

### API Principles

- the LLM never receives raw SQL or shell access;
- every state-changing tool call is scoped to one domain operation;
- material financial changes require the confirmation step (PRD PR-001) before any Household MCP write occurs.

### Error Model

To be defined at implementation time; must distinguish "not yet confirmed" from "failed to persist" so Hermes never claims a change succeeded when it did not.

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

The allowlist check happens before Hermes processes a message; Household MCP additionally scopes every tool call to allowed operations, so authorization is not delegated to the LLM's judgment alone.

### Identity Flow

```text
Telegram user
  ↓
Allowlist check (Hermes)
  ↓
Hermes skill processing
  ↓
Household MCP tool authorization
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
- the LLM never receives raw SQL access to authoritative household state; authoritative reads/writes use only Household MCP's constrained tools;
- Hermes terminal execution uses a Docker sandbox with the egress firewall enabled in the accepted local topology; its broader general-purpose tool/skill surface remains a security-hardening concern before routine shared-household use;
- material financial state changes require explicit human confirmation before persistence;
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

Safe to retry read-only Household MCP calls (e.g. `get_current_allocation`). Write operations (e.g. `confirm_monthly_allocation`) must be idempotent per period to tolerate retries/duplicate confirmation attempts.

### Idempotency

Confirming the same allocation twice for the same period must not create duplicate authoritative records (see `docs/01_features/monthly-allocation.md`, BR-03).

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

The dashboard's persona health signal (Idle/Working/Scheduled/Error) is the primary V1 health signal; no separate liveness/readiness endpoint design is specified yet.

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

For the accepted local runtime, Hermes configuration and credentials live under its managed `~/.hermes` runtime state, while 9Router owns its OpenRouter credential and physical model fallback list. FARIA repository configuration will be introduced only when an implemented FARIA component consumes it. Secrets are never hard-coded or committed.

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

---

## 20. Architecture Decision Records

No ADRs exist yet. The technical direction in this document (Hermes, 9Router, OpenRouter, Household MCP, SQLite, and isolated tool execution) reflects an accepted product decision provided during initialization (see Product Brief, Section 9/Fixed Technical Direction) rather than a locally deliberated architecture trade-off. RF-01A aligns the local runtime description with observed operation; it does not make a new material architecture decision.

---

## 21. Known Constraints

### Technical Constraints

- SQLite (not PostgreSQL); no Redis/Kafka; single Hermes runtime (no independent multi-agent architecture) for V1.

### Operational Constraints

- The proven development topology is macOS-specific; production hosting and process supervision are not yet finalized.
- Only one household member is currently configured and tested in the Telegram allowlist. Second-member onboarding and testing remain prerequisites before shared household use.

### Legacy / Integration Constraints

- None — greenfield project.

### Runtime Constraints Discovered During RF-01

- The accepted Hermes topology is a managed macOS installation with a launchd-supervised gateway, not a FARIA-owned application container.
- Hermes exposes general-purpose tools and skills beyond FARIA's intended household scope. Docker terminal isolation and the egress firewall reduce risk but do not replace a future FARIA-specific tool/skill restriction review (see AQ-07 and `docs/05_operations/CONFIGURATION.md`).
- Rejection of a non-allowlisted Telegram identity has not yet been tested; this is an operational security follow-up, not a claim of acceptance.

---

## 22. Known Architecture Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Single SQLite file/host is a single point of failure | Household financial data loss if the host fails without backup | Encrypted external backup (destination TBD) before production use |
| Model/provider behind the `faria-household-main` combo may change | Inconsistent response quality/latency | Keep Hermes decoupled from a specific physical model through the 9Router-owned combo |
| Hermes exposes tools/skills beyond FARIA's intended household scope | A household request could reach unnecessary general-purpose capability | Keep terminal execution sandboxed with egress filtering and define tighter FARIA tool/skill restrictions in a later hardening batch |

---

## 23. Open Architecture Questions

| ID | Question | Decision Needed By | Owner |
|---|---|---|---|
| AQ-01 | Final production hosting and runtime packaging (including XCodePod.Cloud vs. paid VPS and host-managed vs. containerized processes) | Before deployment | Household |
| AQ-02 | Exact Household MCP tool contract shapes | Before Household MCP implementation | Implementation |
| AQ-03 | Migration/schema tooling for SQLite | Before first schema is created | Implementation |
| AQ-04 | Encrypted backup destination and mechanism | Before production use | Household |
| AQ-05 | Dashboard framework specifics beyond "React/Next.js" (state management, exact API style) | Before dashboard implementation | Implementation |
| AQ-06 | Whether personas ever become independent agents | Only if real requirements justify it | Household / Implementation |
| AQ-07 | How Hermes tools and skills will be restricted to FARIA's intended household scope beyond Docker terminal isolation and egress filtering | Before routine shared-household use | Implementation |

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
| 0.2 | `2026-09-12` | Aligned local runtime topology and RF-01 acceptance with the verified managed Hermes/launchd/9Router setup | sipratama |
| 0.1 | `2026-09-11` | Initial draft | sipratama |
