# Backend Engineering Standard

> **Purpose:** Define reusable implementation expectations for backend applications and services.
>
> This standard is technology-neutral. Project-specific architecture, language, and framework choices remain authoritative.

---

## 1. Backend Responsibilities

The backend SHOULD own authoritative behavior for:

- business rules;
- server-side authorization;
- state transitions;
- persistence coordination;
- integrations;
- validation that protects system invariants;
- background processing;
- security-sensitive decisions.

Frontend behavior MUST NOT be treated as the only enforcement boundary for authoritative rules.

---

## 2. Layer / Module Structure

Backend structure MUST follow the project's documented architecture.

A common structure MAY be:

```text
delivery / transport
application
domain
infrastructure
```

but this template does not require that structure universally.

The important rule is:

> responsibility and dependency direction must be explicit.

---

## 3. Controllers / Handlers

Transport handlers SHOULD:

- parse transport input;
- perform boundary-level validation;
- establish request context;
- invoke application behavior;
- translate result/error to transport response.

They SHOULD NOT contain large business workflows.

Avoid controllers that directly:
- build complex database queries;
- mutate several aggregates;
- call multiple vendors;
- encode authorization/business decisions inline.

---

## 4. Application Services / Use Cases

Application behavior SHOULD coordinate:

- domain rules;
- repositories;
- transactions;
- external ports;
- events;
- authorization context where appropriate.

A use case SHOULD describe meaningful application intent.

Prefer:

```text
EnrollLearner
CreateOrder
ConfirmPayment
PublishCourse
```

over generic:

```text
EntityService.update()
Manager.process()
```

where meaningful intent exists.

---

## 5. Domain Rules

Important business invariants SHOULD be centralized in appropriate domain/application logic.

Avoid duplicating the same rule independently in:
- controller;
- UI;
- job;
- event consumer.

Multiple entry points SHOULD converge on the same authoritative rule.

---

## 6. DTOs and Boundary Models

External request/response models SHOULD be separated from internal domain models when:
- compatibility differs;
- external shape differs;
- exposing internal model creates coupling;
- validation/security concerns differ.

Do not create redundant mapping layers for trivial cases without benefit.

---

## 7. Validation

Use layered validation:

### Transport Validation
Examples:
- required field;
- syntax;
- size;
- enum shape.

### Business Validation
Examples:
- allowed state transition;
- ownership;
- availability;
- campaign window;
- balance/business invariant.

### Persistence Integrity
Examples:
- uniqueness;
- foreign keys;
- check constraints.

Critical invariants SHOULD have defense at the appropriate authoritative layer.

---

## 8. Error Model

Backend errors SHOULD distinguish meaningful categories such as:

- validation;
- authentication;
- authorization;
- not found;
- conflict;
- business rule violation;
- dependency unavailable;
- unexpected internal error.

Transport mapping SHOULD be consistent.

Internal exception details MUST NOT be exposed directly to clients.

Detailed API error schema belongs in the API contract.

---

## 9. Transactions

Transaction boundaries SHOULD align with one business consistency unit.

Avoid:
- one transaction per repository method when a use case needs atomicity;
- long transactions around remote calls;
- hidden nested transaction behavior that changes semantics unexpectedly.

When remote side effects must coordinate with committed data, use an explicit reliability pattern where appropriate, such as:
- outbox;
- state machine;
- retryable workflow;
- compensating action.

---

## 10. Idempotency

Operations exposed to duplicate execution SHOULD define idempotency behavior.

Typical candidates:
- payment initiation;
- webhook processing;
- message consumers;
- retryable commands;
- order submission.

Idempotency MUST define what constitutes the same operation.

A retry mechanism alone does not provide idempotency.

---

## 11. Concurrency

Concurrency-sensitive behavior MUST be deliberate.

Consider:
- optimistic locking;
- unique constraints;
- atomic update;
- pessimistic locking;
- compare-and-set;
- serialized processing.

Do not rely on "unlikely simultaneous requests" for integrity-critical behavior.

---

## 12. Database Access

Queries SHOULD:

- retrieve only required data when practical;
- avoid obvious N+1 behavior;
- avoid unbounded result sets;
- use pagination for large collections;
- use indexes based on real access patterns;
- keep transaction semantics clear.

Detailed persistence rules belong in `07_DATA_PERSISTENCE_STANDARD.md`.

---

## 13. Pagination

Collection endpoints SHOULD use a defined pagination model when datasets can grow materially.

The project SHOULD define:
- page/offset or cursor;
- stable ordering;
- maximum page size;
- continuation semantics.

Do not expose unlimited "get all" for potentially large datasets.

---

## 14. Caching

Cache only when there is a clear performance/cost benefit.

For every cache, define:
- authoritative source;
- key;
- TTL;
- invalidation;
- acceptable staleness;
- behavior on cache failure.

Cache MUST NOT become undocumented authoritative state.

---

## 15. External Integrations

External calls MUST define:
- timeout;
- error mapping;
- authentication;
- retry policy where safe;
- observability;
- data validation.

Do not assume third-party success response guarantees downstream business success unless the provider contract says so.

Detailed integration rules belong in `06_API_INTEGRATION_STANDARD.md`.

---

## 16. Retry

Retries SHOULD occur only for failures that are:
- transient;
- safe to retry;
- bounded.

Use:
- max attempts;
- backoff;
- jitter where appropriate.

Do not retry:
- validation failures;
- authorization failures;
- deterministic business rejection.

Retry ownership SHOULD be clear to avoid retry amplification across layers.

---

## 17. Background Jobs

Jobs SHOULD be:

- idempotent or safely resumable where duplicate execution is possible;
- observable;
- bounded;
- explicit about retry/terminal failure;
- safe under process restart.

Long-running jobs SHOULD expose meaningful status when users/operators depend on completion.

---

## 18. Messaging / Events

Consumers SHOULD assume duplicate delivery unless infrastructure guarantees otherwise and architecture relies on that guarantee.

Consumers SHOULD:
- validate schema;
- preserve idempotency;
- handle poison messages;
- avoid infinite retry;
- expose failure/lag signals.

Event schema rules belong in `06_API_INTEGRATION_STANDARD.md`.

---

## 19. Timeouts

Every remote/network interaction SHOULD have an explicit timeout.

Timeouts SHOULD reflect:
- upstream request budget;
- dependency behavior;
- retry strategy.

Do not inherit infinite/default timeouts without review.

---

## 20. Authentication

Authentication mechanism MUST follow project architecture.

Backend code MUST NOT trust:
- arbitrary client identity fields;
- role values sent by the client;
- unsigned/unverified tokens;
- frontend-only session state.

Identity must be established through the trusted authentication boundary.

---

## 21. Authorization

Authorization MUST be enforced server-side for protected operations.

Rules SHOULD consider:
- role;
- resource ownership;
- tenant;
- scope;
- object state;
- privileged/admin boundary.

Avoid scattered ad hoc authorization if a shared policy model can express the same rule clearly.

Detailed security rules belong in `08_SECURITY_STANDARD.md`.

---

## 22. Sensitive Data

Backend code MUST:
- minimize sensitive data exposure;
- avoid logging secrets/tokens;
- mask/redact where needed;
- use approved encryption/security mechanisms;
- limit data returned to required fields.

---

## 23. Configuration

Operational configuration SHOULD come from the documented configuration system.

Backend code MUST NOT:
- hard-code production credentials;
- depend on developer-local paths;
- hide environment behavior in source constants when configuration is required.

---

## 24. Observability

Important backend paths SHOULD expose enough signals to answer:

- what operation failed?
- which dependency?
- how often?
- which request/correlation ID?
- what business outcome is affected?

Use structured logging where ecosystem supports it.

Detailed rules belong in `10_OBSERVABILITY_RELIABILITY.md`.

---

## 25. Health Endpoints

Services SHOULD distinguish where relevant:

- liveness;
- readiness.

Readiness MAY depend on critical startup/runtime dependencies.

Do not expose sensitive internal diagnostics publicly.

---

## 26. Testing

Backend behavior SHOULD be tested at appropriate layers:

- domain/application unit tests;
- persistence/integration tests;
- contract tests;
- authorization tests;
- migration tests;
- critical E2E.

Detailed implementation rules belong in `09_TESTING_STANDARD.md`.

---

## 27. API Compatibility

Backend implementations MUST remain synchronized with the machine-readable API contract where one exists.

Do not add undocumented response fields/semantics that consumers must depend on.

Breaking changes require explicit version/rollout strategy.

---

## 28. Framework Usage

Prefer framework-native mechanisms when they are:
- well-understood;
- secure;
- observable;
- aligned with project architecture.

Avoid custom infrastructure code that duplicates mature framework capabilities without reason.

At the same time, do not let framework convenience bypass architecture invariants.

---

## 29. Backend Review Checklist

Review:
- business rule location;
- authorization;
- transaction boundary;
- duplicate/concurrency behavior;
- external timeout/retry;
- query scale;
- error mapping;
- sensitive logging;
- contract compatibility;
- observability;
- test evidence.

---

## 30. Exceptions

Project-specific architecture MAY simplify or strengthen these defaults.

Deviations that materially alter system boundaries or consistency/reliability behavior SHOULD be recorded in an ADR.
