# Architecture Standard

> **Purpose:** Define reusable rules for system/module boundaries, dependency direction, architectural decisions, and controlled evolution.
>
> `SYSTEM_ARCHITECTURE.md` describes the actual architecture of a project. ADRs explain material project-specific decisions.

---

## 1. Architecture Principle

Architecture exists to make change safer and responsibilities clearer.

Projects SHOULD choose the simplest architecture that satisfies:
- product needs;
- current risk;
- expected scale;
- team capability;
- operational constraints.

Complexity MUST be justified by real constraints, not architectural fashion.

---

## 2. Explicit Boundaries

Important responsibilities MUST have explicit ownership.

Examples:
- identity;
- catalog;
- orders;
- payments;
- notifications;
- reporting.

A boundary SHOULD define:
- responsibility;
- public interaction surface;
- owned data;
- allowed dependencies.

Avoid modules that exist only as arbitrary technical folders without meaningful responsibility.

---

## 3. Dependency Direction

Dependencies MUST follow the project's documented architecture.

If the project uses layered/hexagonal/clean architecture, dependency direction SHOULD prevent core business logic from depending directly on delivery/infrastructure details.

Example:

```text
Transport
   ↓
Application
   ↓
Domain
   ↑
Ports
   ↑
Infrastructure
```

This example is not mandatory for every project.

The chosen rule MUST be documented and consistently applied.

---

## 4. Domain Logic

Business invariants SHOULD live in a layer/module that is not coupled unnecessarily to:
- HTTP;
- UI;
- ORM-specific behavior;
- message broker APIs;
- vendor SDKs.

Simple CRUD behavior MAY remain simpler when no meaningful domain logic exists.

Do not force domain-driven patterns onto trivial applications.

---

## 5. Module Communication

Modules SHOULD communicate through explicit supported boundaries.

Avoid:
- arbitrary access to another module's internals;
- cross-module table writes;
- circular dependencies;
- shared mutable global state.

Within a modular monolith, supported calls MAY be in-process.

Across services, supported calls MAY use APIs/events.

The architecture determines the boundary, not the desire to use distributed technology.

---

## 6. Data Ownership

Mutable authoritative data SHOULD have one clear owner.

Other modules SHOULD:
- query through supported interfaces;
- consume replicated/read models;
- react to events;

rather than mutate another module's owned data directly.

Shared reference data MAY be handled differently when explicitly documented.

---

## 7. Distributed Systems

A project MUST NOT become distributed solely for organizational aesthetics or hypothetical scale.

Before extracting a service, consider:
- independent scaling;
- independent deployment requirement;
- data ownership;
- failure isolation;
- team ownership;
- latency;
- operational burden;
- transaction complexity;
- observability requirements.

A modular monolith is a valid production architecture.

---

## 8. Synchronous vs Asynchronous

Use synchronous interaction when:
- caller needs immediate outcome;
- consistency expectation requires it;
- failure handling is simpler and acceptable.

Use asynchronous interaction when:
- work can complete later;
- decoupling is valuable;
- buffering is needed;
- fan-out is real;
- long-running work should not block request path.

Async processing introduces:
- retries;
- duplicates;
- ordering questions;
- eventual consistency;
- observability needs.

Those costs MUST be explicitly handled.

---

## 9. External Dependencies

Vendor/framework SDKs SHOULD be isolated when:
- replacement risk is meaningful;
- API is unstable;
- domain code would otherwise become vendor-specific;
- testing benefits from a boundary.

Do not wrap every library automatically.

Thin wrappers with no meaningful boundary MAY add noise rather than isolation.

---

## 10. Framework Boundaries

Frameworks SHOULD support the application architecture, not define business semantics.

Avoid:
- business rules encoded only in annotations/config magic;
- persistence entities becoming the only domain model when that harms behavior clarity;
- HTTP status codes leaking deep into domain logic;
- frontend component framework concerns driving backend domain design.

---

## 11. Cross-Cutting Concerns

Cross-cutting concerns SHOULD be handled consistently:

- authentication;
- authorization;
- logging;
- tracing;
- validation;
- error mapping;
- configuration;
- transactions.

Avoid ad hoc reimplementation in every feature.

However, centralized abstractions MUST NOT hide feature-specific behavior that reviewers need to see.

---

## 12. Architecture Invariants

Projects SHOULD define critical invariants in `SYSTEM_ARCHITECTURE.md`.

Examples:

```text
INV-01 — Only the payment module may mutate payment state.
INV-02 — Domain modules do not depend on HTTP controllers.
INV-03 — REST schemas come from the OpenAPI contract.
```

Implementation MUST preserve accepted invariants.

---

## 13. ADR Requirements

Create an ADR for decisions that are:
- expensive to reverse;
- cross-cutting;
- strategic;
- architecture-boundary changing;
- introducing major infrastructure/provider dependencies;
- changing persistence/integration/deployment/security strategy.

Do not create ADRs for:
- routine class design;
- minor refactors;
- obvious implementation detail;
- temporary debugging choices.

---

## 14. Architecture Fitness

Where practical, important architecture rules SHOULD be automated through:

- package/module dependency checks;
- lint rules;
- ArchUnit-like tests;
- build boundaries;
- workspace dependency constraints;
- contract checks.

Rules that cannot be automated SHOULD be explicit enough for review.

---

## 15. API Boundaries

Internal code MUST NOT bypass a public module/service contract merely because direct access is easier when doing so violates ownership.

Machine-readable public contracts belong in `contracts/`.

Detailed rules belong in `06_API_INTEGRATION_STANDARD.md`.

---

## 16. Persistence Boundaries

Database technology SHOULD NOT leak across the entire application when doing so prevents business logic from being tested/reasoned independently.

However, applications MAY use framework-native persistence directly for simple CRUD areas where additional abstraction adds no value.

The standard favors appropriate boundaries, not ceremony.

---

## 17. Shared Libraries

Shared libraries SHOULD contain genuinely reusable stable concepts.

Avoid shared "common" modules that become dumping grounds for:
- unrelated helpers;
- DTOs from every domain;
- generic constants;
- cross-domain business logic.

A shared abstraction increases coupling and SHOULD earn its existence.

---

## 18. Configuration Boundaries

Configuration SHOULD influence operational variability.

Do not turn product rules into arbitrary runtime configuration unless the product actually requires configurability.

Security-critical configuration MUST use safe defaults.

---

## 19. Failure Boundaries

Architecture SHOULD define how failures cross boundaries.

Each integration SHOULD make clear:
- timeout behavior;
- retry ownership;
- error translation;
- fallback/degradation;
- idempotency expectations;
- observability.

Do not let every caller invent different failure behavior for the same dependency.

---

## 20. Transaction Boundaries

Transactions SHOULD align with consistency boundaries.

Avoid holding database transactions open across:
- slow remote calls;
- user interaction;
- message broker operations;

unless architecture explicitly uses a mechanism that makes this safe/intentional.

Distributed atomic transactions SHOULD NOT be introduced by default.

---

## 21. Evolution

Architecture changes SHOULD be incremental when risk is high.

Prefer migration paths such as:

```text
Introduce new boundary
        ↓
Move one behavior
        ↓
Verify
        ↓
Move remaining behavior
        ↓
Remove old path
```

over large unverified rewrites.

---

## 22. Rewrites

A rewrite requires explicit justification.

Before rewriting, assess:
- actual failure of current design;
- migration cost;
- feature freeze cost;
- test coverage;
- production risk;
- incremental alternatives.

"Cleaner technology" alone is insufficient justification.

---

## 23. Architecture Review Checklist

Ask:

- Is responsibility clear?
- Is data ownership clear?
- Are dependencies one-directional where intended?
- Are cross-boundary calls explicit?
- Does this add distributed-system cost?
- Is failure behavior defined?
- Are contracts affected?
- Is an ADR required?
- Can important invariants be automated?

---

## 24. Exceptions

Architecture standards MAY be overridden by an accepted project-specific ADR.

The ADR SHOULD state:
- why;
- scope;
- consequences;
- migration/exit considerations where relevant.
