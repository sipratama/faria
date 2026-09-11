# System Architecture — <PROJECT_NAME>

> **Document role:** Authoritative source for the system's high-level technical structure, boundaries, runtime interactions, and architectural invariants.
>
> Product behavior belongs in the PRD and feature specs. Decision rationale belongs in ADRs. Exact public interfaces belong in machine-readable contracts. Detailed coding conventions belong in engineering standards.

---

## Document Metadata

| Field | Value |
|---|---|
| Project | `<PROJECT_NAME>` |
| Status | Draft / Review / Locked |
| Version | `0.1` |
| Architecture Owner | `<OWNER>` |
| Last Updated | `<YYYY-MM-DD>` |

---

## 1. Architecture Summary

### System Purpose

<Describe what the system does in technical/product terms in 2–4 sentences.>

### Architecture Style

`<MODULAR MONOLITH / HEXAGONAL / LAYERED / MICROSERVICES / EVENT-DRIVEN / OTHER>`

### Primary Runtime Components

- `<FRONTEND>`
- `<BACKEND>`
- `<DATABASE>`
- `<CACHE>`
- `<MESSAGE BROKER>`
- `<EXTERNAL SERVICE>`

Only list components that actually exist or are explicitly planned.

---

## 2. Architecture Objectives

The architecture should optimize for:

1. `<OBJECTIVE>`
2. `<OBJECTIVE>`
3. `<OBJECTIVE>`

Examples:

- rapid product iteration;
- clear domain boundaries;
- predictable deployment;
- secure handling of user data;
- horizontal scalability for stateless workloads;
- low operational complexity.

### Non-Objectives

The architecture is not currently optimized for:

- `<NON_OBJECTIVE>`
- `<NON_OBJECTIVE>`

This section prevents premature complexity.

---

## 3. System Context

Describe actors and external systems.

```text
+-----------------+
|      User       |
+--------+--------+
         |
         v
+-----------------+
|   Web / App UI  |
+--------+--------+
         |
         v
+-----------------+        +------------------+
|     Backend     |------->| External Service |
+--------+--------+        +------------------+
         |
         v
+-----------------+
|    Database     |
+-----------------+
```

Replace this diagram with the actual system context.

### External Actors

| Actor | Interaction |
|---|---|
| `<ACTOR>` | `<INTERACTION>` |

### External Systems

| System | Purpose | Protocol | Criticality |
|---|---|---|---|
| `<SYSTEM>` | `<PURPOSE>` | HTTPS / Kafka / SMTP / etc. | Low / Medium / High |

---

## 4. Container / Runtime View

Describe independently deployable or operationally meaningful components.

| Component | Responsibility | Technology | Deployment Unit |
|---|---|---|---|
| `<WEB>` | `<RESPONSIBILITY>` | `<TECH>` | `<UNIT>` |
| `<API>` | `<RESPONSIBILITY>` | `<TECH>` | `<UNIT>` |
| `<WORKER>` | `<RESPONSIBILITY>` | `<TECH>` | `<UNIT>` |

### Deployment Relationships

```text
<Client>
   |
   v
<Frontend>
   |
   v
<Backend/API>
   |        \
   v         v
<DB>      <Broker>
             |
             v
          <Worker>
```

Use diagrams only when they clarify a real boundary.

---

## 5. Frontend Architecture

Complete when the project contains a frontend.

### Responsibilities

The frontend owns:

- rendering and interaction;
- client-side navigation;
- presentation state;
- input collection and local validation;
- consuming server contracts;
- accessibility and responsive behavior.

The frontend does **not** own authoritative security or business rules unless explicitly stated.

### Structure

```text
src/
├── app/
├── features/
├── components/
├── services/
├── hooks/
├── state/
├── types/
└── utils/
```

Replace with the actual structure.

### State Strategy

| State Type | Owner / Mechanism |
|---|---|
| Server state | `<TOOL / PATTERN>` |
| Local UI state | `<TOOL / PATTERN>` |
| Form state | `<TOOL / PATTERN>` |
| Global client state | `<TOOL / PATTERN OR NONE>` |

### Frontend Boundaries

- `<BOUNDARY>`
- `<BOUNDARY>`

---

## 6. Backend Architecture

### Responsibilities

The backend owns:

- authoritative business rules;
- authentication/authorization enforcement;
- domain state transitions;
- persistence coordination;
- external integration orchestration;
- server-side validation;
- reliability controls;
- audit-relevant behavior.

### Module / Domain Boundaries

| Module | Responsibility | Owns Data? | May Depend On |
|---|---|---:|---|
| `<MODULE>` | `<RESPONSIBILITY>` | Yes / No | `<DEPENDENCIES>` |

### Dependency Direction

```text
Transport / Delivery
        ↓
Application
        ↓
Domain
        ↑
Ports / Interfaces
        ↑
Infrastructure
```

Replace this if the project uses another architecture.

The chosen dependency rule should be explicit and consistently enforced.

---

## 7. Domain and Data Ownership

### Domain Boundaries

Describe the important domain boundaries and who owns each state transition.

### Data Ownership

| Data / Aggregate | Owning Module | Authoritative Store |
|---|---|---|
| `<DATA>` | `<MODULE>` | `<STORE>` |

Avoid shared ownership of the same mutable data where possible.

---

## 8. Data Architecture

### Primary Datastores

| Store | Purpose | Data Type |
|---|---|---|
| `<POSTGRESQL>` | `<PURPOSE>` | Transactional |
| `<REDIS>` | `<PURPOSE>` | Cache / ephemeral |
| `<OBJECT STORAGE>` | `<PURPOSE>` | Files |

### Schema Management

Persistent schema changes are managed through version-controlled migrations.

### Transactions

Define transaction boundaries and consistency expectations.

- `<RULE>`
- `<RULE>`

### Data Retention

`<POLICY OR LINK>`

### Backup / Recovery Assumptions

`<POLICY OR LINK>`

Detailed entity definitions belong in `DATA_MODEL.md` and migrations.

---

## 9. API Architecture

### API Style

`<REST / GRAPHQL / RPC / MIXED>`

### Contract Source

`<contracts/openapi/openapi.yaml>`

### API Principles

- explicit versioning strategy;
- stable error model;
- predictable pagination where needed;
- idempotency for relevant mutating operations;
- authentication and authorization at server boundaries;
- backward-compatible evolution where practical.

### Error Model

Describe the common error envelope and how domain errors map to transport errors.

Do not duplicate the full OpenAPI definition here.

---

## 10. Event and Async Architecture

Complete when asynchronous communication exists.

### Broker

`<KAFKA / RABBITMQ / SQS / NONE>`

### Event Contract Source

`<contracts/asyncapi/asyncapi.yaml>`

### Event Principles

- event names describe facts, not commands, unless intentionally modeled otherwise;
- consumers should tolerate retries;
- idempotency strategy must be explicit;
- ordering assumptions must be documented;
- poison messages and dead-letter behavior must be defined;
- schema evolution must be backward compatible where required.

### Key Events

| Event | Producer | Consumers | Delivery Semantics |
|---|---|---|---|
| `<EVENT>` | `<MODULE>` | `<CONSUMERS>` | At-least-once / etc. |

---

## 11. Authentication and Authorization

### Authentication

`<SESSION / JWT / OIDC / KEYCLOAK / CLERK / OTHER>`

### Authorization Model

`<RBAC / ABAC / OWNERSHIP / POLICY-BASED / MIXED>`

### Enforcement Boundary

Authoritative authorization is enforced at:

`<BACKEND / GATEWAY / SERVICE>`

### Identity Flow

```text
User
  ↓
Identity Provider
  ↓
Application
  ↓
Authorization Check
  ↓
Protected Resource
```

Reference detailed security decisions through ADRs or the threat model.

---

## 12. Security and Trust Boundaries

Identify the major trust boundaries.

Examples:

```text
Internet
  |
  | trust boundary
  v
Frontend / Edge
  |
  | trust boundary
  v
Backend
  |
  | trust boundary
  v
Database / Internal Services
```

### Security Invariants

- secrets are not stored in source code;
- client input is untrusted;
- authorization is not delegated only to the UI;
- sensitive values are not written to logs;
- external callbacks are validated;
- privileged operations are auditable where required.

Add project-specific invariants.

Detailed threats belong in `THREAT_MODEL.md`.

---

## 13. Caching

Complete when caching exists.

| Cache | Purpose | Key Strategy | TTL | Invalidation |
|---|---|---|---|---|
| `<CACHE>` | `<PURPOSE>` | `<KEY>` | `<TTL>` | `<STRATEGY>` |

Caching must not become an undocumented source of truth.

State which data may be stale and for how long.

---

## 14. Reliability and Failure Handling

### Timeouts

All remote calls should have explicit timeout behavior.

### Retries

Retry only failures that are safe and meaningful to retry.

### Idempotency

Define idempotency requirements for operations vulnerable to duplicate execution.

### Circuit Breaking / Degradation

`<STRATEGY OR N/A>`

### Partial Failure

Describe behavior when dependencies fail.

| Dependency | Failure Behavior | User Impact | Recovery |
|---|---|---|---|
| `<DEPENDENCY>` | `<BEHAVIOR>` | `<IMPACT>` | `<RECOVERY>` |

---

## 15. Observability

### Logs

Structured logs should include enough context to correlate important operations without exposing sensitive data.

### Metrics

Track system and business signals relevant to reliability.

### Tracing

Use distributed tracing when cross-service or external-call visibility is materially useful.

### Correlation

Define the request/correlation identifier strategy.

### Health

Document:

- liveness;
- readiness;
- dependency health;
- background worker health.

---

## 16. Deployment Architecture

### Environments

| Environment | Purpose | Data |
|---|---|---|
| Local | Developer execution | Local/mock |
| Test | Automated testing | Ephemeral |
| Staging | Pre-production verification | Non-production |
| Production | Live users | Production |

Adjust to project reality.

### Runtime Platform

`<DOCKER / KUBERNETES / OPENSHIFT / VERCEL / VPS / SERVERLESS / OTHER>`

### Deployment Diagram

```text
Internet
   |
   v
<Edge / LB>
   |
   +------> <Frontend>
   |
   +------> <Backend>
               |
        +------+------+
        |             |
        v             v
      <DB>         <Broker>
```

### Configuration

Runtime configuration comes from environment-specific configuration and secret management, not hard-coded values.

See `docs/05_operations/CONFIGURATION.md`.

---

## 17. Scalability

Document real expected pressure points.

### Expected Load

| Dimension | Current / Initial | Expected Growth |
|---|---:|---:|
| Users | `<N>` | `<N>` |
| Requests/sec | `<N>` | `<N>` |
| Events/sec | `<N>` | `<N>` |
| Stored data | `<SIZE>` | `<SIZE>` |

### Scaling Strategy

- `<STATELESS HORIZONTAL SCALING>`
- `<DB INDEX / REPLICA / PARTITIONING IF NEEDED>`
- `<WORKER SCALING>`
- `<CDN / CACHE>`

Do not introduce distributed architecture only for hypothetical scale.

---

## 18. Performance Assumptions

High-level performance targets belong in `NON_FUNCTIONAL_REQUIREMENTS.md`.

This document should explain the architectural strategy used to meet them.

Examples:

- read-heavy paths may use caching;
- long-running work moves to background processing;
- large files use object storage;
- expensive queries require indexing and measurement.

---

## 19. Architecture Invariants

These are rules that must remain true unless an ADR explicitly changes them.

### INV-01 — `<INVARIANT>`

<Example: Domain modules must not depend directly on HTTP controllers.>

### INV-02 — `<INVARIANT>`

<Example: Public API schemas are defined in OpenAPI before implementation changes are considered complete.>

### INV-03 — `<INVARIANT>`

<Example: Only the payment module may mutate authoritative payment state.>

Architecture invariants are especially important for AI-assisted development.

---

## 20. Architecture Decision Records

Material decisions are stored under:

```text
docs/02_architecture/adr/
```

Relevant ADRs:

| ADR | Decision | Status |
|---|---|---|
| `ADR-0001` | `<DECISION>` | Accepted |

Do not duplicate ADR rationale in this document. Summarize and link.

---

## 21. Known Constraints

### Technical Constraints

- `<CONSTRAINT>`

### Operational Constraints

- `<CONSTRAINT>`

### Legacy / Integration Constraints

- `<CONSTRAINT>`

---

## 22. Known Architecture Risks

| Risk | Impact | Mitigation |
|---|---|---|
| `<RISK>` | `<IMPACT>` | `<MITIGATION>` |

Project-level risk ownership belongs in `docs/06_delivery/RISKS.md`.

---

## 23. Open Architecture Questions

| ID | Question | Decision Needed By | Owner |
|---|---|---|---|
| AQ-01 | `<QUESTION>` | `<MILESTONE>` | `<OWNER>` |

When resolved, create an ADR if the decision is architecturally material.

---

## 24. Change Rules

Update this document when:

- a system boundary changes;
- a deployable component is added or removed;
- ownership of domain data changes;
- integration topology changes materially;
- security or trust boundaries change;
- persistence architecture changes;
- reliability architecture changes.

Do not update this document for routine internal refactoring that preserves the architecture.

---

## 25. Related Documents

- Product Brief: `../00_product/PRODUCT_BRIEF.md`
- PRD: `../00_product/PRD.md`
- Feature Specs: `../01_features/`
- Data Model: `./DATA_MODEL.md`
- NFR: `./NON_FUNCTIONAL_REQUIREMENTS.md`
- ADRs: `./adr/`
- Test Strategy: `../04_engineering/TEST_STRATEGY.md`
- Threat Model: `../04_engineering/THREAT_MODEL.md`
- Deployment: `../05_operations/DEPLOYMENT.md`
- Standards: `../standards/`

---

## 26. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
