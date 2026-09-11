# Non-Functional Requirements — <PROJECT_NAME>

> **Document role:** Authoritative source for **measurable cross-cutting quality requirements and operational constraints**.
>
> This document states required outcomes and thresholds. Architecture documents explain how the system is designed to meet them. Engineering standards define implementation practices.

---

## Document Metadata

| Field | Value |
|---|---|
| Project | `<PROJECT_NAME>` |
| Status | Draft / Review / Locked |
| Version | `0.1` |
| Owner | `<OWNER>` |
| Last Updated | `<YYYY-MM-DD>` |

---

## 1. How to Use This Document

A useful NFR should be:

- measurable or objectively verifiable;
- relevant to actual product risk;
- scoped to a workload, path, or environment;
- clear about target vs hard requirement;
- testable through automated or operational evidence where practical.

Avoid vague statements such as:

> The system must be fast, secure, scalable, and highly available.

Prefer:

> For authenticated API reads under the defined normal load, p95 server response time must remain below 300 ms excluding third-party latency.

Do not invent aggressive targets without product or operational justification.

---

## 2. Requirement Format

Use stable IDs:

```text
NFR-<CATEGORY>-<NUMBER>
```

Examples:

```text
NFR-PERF-001
NFR-AVAIL-001
NFR-SEC-001
NFR-OBS-001
```

Each requirement should define:

- requirement;
- scope;
- target/threshold;
- verification method;
- priority;
- rationale where useful.

---

## 3. Performance

### NFR-PERF-001 — API Response Time

**Requirement**  
`<REQUIREMENT>`

**Scope**  
`<ENDPOINTS / WORKLOAD>`

**Target**
- p50: `<VALUE>`
- p95: `<VALUE>`
- p99: `<VALUE>`

**Load Assumption**  
`<RPS / CONCURRENT USERS / DATA SIZE>`

**Verification**  
`<LOAD TEST / APM / BENCHMARK>`

**Priority**  
P0 / P1 / P2

---

### NFR-PERF-002 — Frontend Experience

Possible signals:

- Largest Contentful Paint;
- Interaction to Next Paint;
- route transition;
- initial JS budget;
- image/media budget.

Use only relevant metrics and define target device/network conditions.

---

## 4. Capacity and Scalability

### NFR-SCALE-001 — Initial Capacity

| Dimension | Required Capacity | Growth Horizon |
|---|---:|---|
| Concurrent users | `<N>` | `<PERIOD>` |
| Requests/sec | `<N>` | `<PERIOD>` |
| Events/sec | `<N>` | `<PERIOD>` |
| Data volume | `<SIZE>` | `<PERIOD>` |
| File/object volume | `<SIZE>` | `<PERIOD>` |

### Scaling Requirement

`<REQUIREMENT>`

Avoid requiring horizontal scaling if a simpler deployment meets realistic demand.

---

## 5. Availability

### NFR-AVAIL-001 — Service Availability

**Target**  
`<e.g. 99.9% monthly>`

**Scope**  
`<USER-FACING SERVICE / CRITICAL API>`

**Excluded Conditions**
- `<PLANNED MAINTENANCE OR NONE>`

**Measurement Source**  
`<SYNTHETIC / LB / APM / EXTERNAL MONITOR>`

Do not set availability targets without understanding operational cost.

---

## 6. Reliability and Resilience

### NFR-REL-001 — Dependency Failure

**Requirement**  
`<EXPECTED BEHAVIOR WHEN A CRITICAL DEPENDENCY FAILS>`

### NFR-REL-002 — Duplicate Processing

**Requirement**  
`<IDEMPOTENCY EXPECTATION>`

### NFR-REL-003 — Data Integrity

**Requirement**  
`<NO LOST/CORRUPTED AUTHORITATIVE STATE UNDER DEFINED FAILURE CONDITIONS>`

### NFR-REL-004 — Background Processing

Define:
- retry expectation;
- dead-letter or terminal-failure behavior;
- visibility/alerting requirement;
- maximum acceptable processing delay.

---

## 7. Recovery and Disaster Recovery

### NFR-DR-001 — Recovery Point Objective

**RPO**  
`<VALUE>`

### NFR-DR-002 — Recovery Time Objective

**RTO**  
`<VALUE>`

### Backup Requirements

- frequency: `<VALUE>`;
- retention: `<VALUE>`;
- encryption: `<YES/NO>`;
- restore test cadence: `<VALUE>`.

Use `N/A` explicitly when DR requirements are intentionally not established for the current phase.

---

## 8. Security

Security architecture and controls belong in threat model and standards. NFRs define required outcomes.

### NFR-SEC-001 — Authentication

`<REQUIREMENT>`

### NFR-SEC-002 — Authorization

`<REQUIREMENT>`

### NFR-SEC-003 — Transport Security

`<REQUIREMENT>`

### NFR-SEC-004 — Sensitive Data

`<REQUIREMENT>`

### NFR-SEC-005 — Vulnerability / Dependency Response

`<REQUIREMENT AND RESPONSE WINDOW IF APPLICABLE>`

Verification may include automated scans, integration tests, review, or penetration testing depending on risk.

---

## 9. Privacy

### NFR-PRIV-001 — Data Minimization

`<REQUIREMENT>`

### NFR-PRIV-002 — Retention

`<REQUIREMENT>`

### NFR-PRIV-003 — Deletion / Export

`<REQUIREMENT>`

### NFR-PRIV-004 — Telemetry

`<REQUIREMENT FOR PII/SENSITIVE DATA IN LOGS/ANALYTICS>`

---

## 10. Observability

### NFR-OBS-001 — Request Correlation

`<REQUIREMENT>`

### NFR-OBS-002 — Critical Failure Visibility

`<REQUIREMENT>`

### NFR-OBS-003 — Business-Critical Signals

`<REQUIREMENT>`

### NFR-OBS-004 — Alert Quality

Alerts for critical production conditions should be actionable and should identify the affected service/path where practical.

Avoid defining observability as "log everything."

---

## 11. Maintainability

### NFR-MAINT-001 — Architecture Boundaries

`<REQUIREMENT>`

### NFR-MAINT-002 — Automated Verification

`<REQUIRED BUILD/LINT/TEST/ARCHITECTURE CHECKS>`

### NFR-MAINT-003 — Change Safety

`<BACKWARD COMPATIBILITY / MIGRATION / REVIEW EXPECTATION>`

Do not use arbitrary code coverage percentages unless they serve a concrete quality objective.

---

## 12. Testability

### NFR-TEST-001 — Deterministic Testability

Critical business behavior should be testable without depending on unstable external systems.

### NFR-TEST-002 — External Dependencies

`<MOCK / SANDBOX / CONTRACT TEST EXPECTATION>`

### NFR-TEST-003 — Production-Like Verification

`<STAGING / EPHEMERAL ENV / CONTAINERIZED DEPENDENCY EXPECTATION>`

---

## 13. Compatibility

### Supported Clients / Platforms

| Platform | Minimum / Supported Version | Notes |
|---|---|---|
| Browser | `<VERSIONS>` | `<NOTES>` |
| Mobile OS | `<VERSIONS OR N/A>` | `<NOTES>` |
| API consumers | `<VERSION POLICY>` | `<NOTES>` |

### Backward Compatibility

`<POLICY>`

Compatibility requirements should reflect real consumers.

---

## 14. Accessibility

Complete for user-facing products.

### NFR-A11Y-001

**Target**  
`<e.g. WCAG 2.2 AA where applicable>`

### Required Behaviors

- keyboard accessibility;
- visible focus;
- semantic structure;
- sufficient contrast;
- screen-reader-compatible labels/status where relevant;
- motion reduction where applicable.

Define verification approach.

---

## 15. Localization and Internationalization

Use when relevant.

| Concern | Requirement |
|---|---|
| Language | `<SUPPORTED LANGUAGES>` |
| Locale | `<FORMAT RULES>` |
| Time zone | `<RULE>` |
| Currency | `<RULE>` |
| Text expansion | `<EXPECTATION>` |

---

## 16. Data Consistency

### NFR-DATA-001

`<STRONG/EVENTUAL CONSISTENCY REQUIREMENT FOR CRITICAL DATA>`

### NFR-DATA-002

`<MAXIMUM STALENESS OR SYNCHRONIZATION EXPECTATION>`

Reference `DATA_MODEL.md` for ownership and lifecycle.

---

## 17. Auditability

Use for admin, financial, security-sensitive, or regulated operations.

### NFR-AUDIT-001

`<WHICH ACTIONS MUST BE AUDITABLE>`

### Retention

`<AUDIT RETENTION>`

### Integrity

`<PROTECTION AGAINST UNAUTHORIZED MODIFICATION>`

---

## 18. Operational Requirements

### Configuration

`<ENVIRONMENT/SECRET CONFIG EXPECTATIONS>`

### Deployability

`<DEPLOYMENT EXPECTATION>`

### Rollback

`<ROLLBACK/RECOVERY EXPECTATION>`

### Zero-Downtime

`<REQUIRED / NOT REQUIRED / TARGET>`

Avoid imposing enterprise-grade operations on prototypes without justification.

---

## 19. Cost Constraints

Use when cloud/API/model cost is material.

### NFR-COST-001

**Requirement**  
`<BUDGET / UNIT COST / COST GROWTH EXPECTATION>`

**Measurement**  
`<HOW COST IS OBSERVED>`

---

## 20. Compliance

| Regulation / Policy | Applicability | Requirement |
|---|---|---|
| `<STANDARD>` | Required / Candidate / N/A | `<REQUIREMENT>` |

Do not claim compliance merely because a control exists.

---

## 21. NFR Summary Matrix

| ID | Category | Requirement | Target | Priority | Verification |
|---|---|---|---|---|---|
| `NFR-...` | `<CATEGORY>` | `<SHORT>` | `<TARGET>` | P0/P1/P2 | `<METHOD>` |

This matrix is an index; detailed requirements remain in their category sections.

---

## 22. Exceptions and Tradeoffs

Document intentionally accepted deviations.

| NFR | Exception | Reason | Expiry / Review |
|---|---|---|---|
| `<ID>` | `<EXCEPTION>` | `<RATIONALE>` | `<DATE/MILESTONE>` |

Material architectural tradeoffs should also be reflected in ADRs.

---

## 23. Related Documents

- System Architecture: `./SYSTEM_ARCHITECTURE.md`
- Data Model: `./DATA_MODEL.md`
- ADRs: `./adr/`
- Feature Specs: `../01_features/`
- Test Strategy: `../04_engineering/TEST_STRATEGY.md`
- Threat Model: `../04_engineering/THREAT_MODEL.md`
- Operations: `../05_operations/`
- Engineering Standards: `../standards/`

---

## 24. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
