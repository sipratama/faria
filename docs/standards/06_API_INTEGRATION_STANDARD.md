# API and Integration Standard

> **Purpose:** Define reusable engineering rules for HTTP APIs, events/messages, webhooks, third-party integrations, and compatibility at system boundaries.
>
> Exact interface definitions belong in machine-readable contracts such as OpenAPI, AsyncAPI, GraphQL schema, or JSON Schema. This standard defines how those contracts should be designed, evolved, implemented, and operated.

---

## 1. Core Principle

A system boundary is a contract.

Consumers MUST NOT depend on undocumented behavior.

Producers MUST NOT change externally consumed behavior silently.

Contract evolution SHOULD prefer compatibility and explicit migration over synchronized breaking changes.

---

## 2. Contract Ownership

Every public or cross-component interface SHOULD have a clear owner.

Examples:
- REST API → owning backend/module;
- event → producer owns semantic definition;
- webhook receiver → receiving application owns validation/processing contract;
- external provider adapter → internal application owns normalized boundary.

Ownership includes:
- semantics;
- compatibility;
- documentation;
- version evolution;
- deprecation.

---

## 3. Machine-Readable Contracts

Where practical, interfaces MUST use machine-readable definitions.

Recommended:

```text
REST          → OpenAPI
Async events  → AsyncAPI + JSON Schema
GraphQL       → GraphQL schema
Structured files → JSON Schema / equivalent
```

Markdown MAY explain intent and examples but SHOULD NOT be the only authoritative representation for structured public contracts.

---

## 4. Contract-First Changes

For new or changed externally consumed behavior:

1. define/update the contract;
2. assess compatibility;
3. implement provider/consumer changes;
4. verify contract behavior;
5. roll out using an appropriate compatibility strategy.

Implementation and contract MAY be changed in the same commit, but they MUST remain synchronized.

---

## 5. Naming

Names SHOULD use stable domain terminology.

Avoid:
- framework-specific names leaking into public contracts;
- implementation class names;
- ambiguous abbreviations;
- inconsistent synonyms for the same concept.

Examples:

Prefer:

```text
paymentStatus
orderId
courseId
```

over:

```text
paymentFlg
ordNoObj
courseEntityPk
```

---

## 6. REST Resource Design

REST APIs SHOULD model meaningful resources/actions consistently.

Prefer noun-oriented resource paths:

```text
/orders
/orders/{orderId}
/courses/{courseId}/enrollments
```

Use action endpoints only when an operation does not naturally map to CRUD/resource state.

Example:

```text
/orders/{orderId}/cancel
```

MAY be clearer than forcing a generic update when cancellation has meaningful rules.

---

## 7. HTTP Methods

Use standard semantics:

| Method | Expected Meaning |
|---|---|
| GET | Read, safe/idempotent |
| POST | Create or non-idempotent command unless idempotency is added |
| PUT | Replace/upsert according to documented semantics |
| PATCH | Partial update |
| DELETE | Remove/cancel according to documented resource semantics |

Do not use GET for state-changing operations.

---

## 8. Status Codes

Status codes SHOULD communicate transport-level outcome consistently.

Typical categories:

```text
200/201/204 → success
400 → malformed/invalid request
401 → unauthenticated
403 → authenticated but forbidden
404 → resource not found
409 → state/conflict
422 → semantically invalid request where project uses it
429 → rate limited
5xx → server/dependency failure
```

Projects MAY choose a smaller consistent subset.

Do not return `200 OK` for every business/system failure with an opaque success flag unless compatibility requires it.

---

## 9. Error Contract

Public APIs SHOULD define a stable error envelope.

Useful fields MAY include:

```text
code
message
fieldErrors
correlationId
details
```

Rules:
- error `code` SHOULD be machine-stable;
- `message` MAY be human-readable;
- internal exception names MUST NOT be exposed as public contracts;
- stack traces MUST NOT be returned;
- sensitive details MUST NOT be included.

Clients SHOULD NOT be required to parse human-readable messages for logic.

---

## 10. Request Validation

APIs MUST validate:
- required fields;
- type/format;
- size limits;
- enumerations;
- malformed identifiers.

Business validation SHOULD return a predictable documented error.

Validation MUST NOT rely solely on generated client code.

---

## 11. Response Design

Responses SHOULD:
- include only data consumers need;
- use consistent field naming;
- avoid leaking internal persistence structure;
- distinguish absent/nullable/empty semantics;
- avoid polymorphic ambiguity unless schema documents it.

Do not expose entire ORM/domain entities automatically.

---

## 12. Pagination

Potentially large collections MUST use bounded retrieval.

A project SHOULD standardize one pagination style where practical.

### Offset/Page

Useful for:
- simple administrative lists;
- relatively stable datasets.

### Cursor

Useful for:
- large or frequently changing datasets;
- infinite scrolling;
- stable continuation.

Contracts MUST define:
- ordering;
- page size/default/max;
- continuation metadata;
- behavior when data changes between pages.

---

## 13. Filtering and Sorting

Filter/sort fields SHOULD be explicitly allowed.

Do not expose arbitrary raw database fields or query language unless intentionally designed.

Sorting SHOULD define deterministic tie-breaking for paginated results.

---

## 14. Idempotency for APIs

Duplicate-sensitive operations SHOULD support idempotency where retries are realistic.

Examples:
- payment creation;
- order submission;
- provisioning;
- external callback processing.

An idempotency design SHOULD define:
- key source;
- key scope;
- request equivalence;
- retention duration;
- replay response;
- conflicting reuse behavior.

Do not equate request IDs with idempotency unless the system actually persists/deduplicates them.

---

## 15. API Versioning

Do not version automatically without a need.

Version when a public interface requires independently managed breaking evolution.

Possible strategies:

```text
/v1/...
header/media type
schema version
provider-specific version
```

Choose one project strategy and document it.

Additive compatible changes SHOULD NOT require a new major API version by default.

---

## 16. Breaking Changes

Breaking changes include more than deleting endpoints.

Examples:
- removing/renaming fields;
- changing field type;
- changing nullable to required;
- narrowing allowed values;
- changing status/error semantics;
- changing units/meaning;
- changing pagination ordering;
- changing authorization assumptions.

Breaking changes MUST have an explicit migration/deprecation plan.

---

## 17. Deprecation

Deprecated interfaces SHOULD define:
- replacement;
- announcement mechanism;
- target removal milestone/date if known;
- consumer migration requirements.

Do not keep deprecated paths indefinitely without ownership.

---

## 18. Backward Compatibility

Consumers SHOULD tolerate compatible additive evolution where appropriate.

Examples:
- unknown JSON fields;
- newly added optional fields;
- new event metadata.

Consumers SHOULD NOT deserialize contracts so rigidly that harmless additive evolution breaks them unless strictness is required for safety.

---

## 19. Contract Testing

Provider implementation SHOULD be verified against authoritative contracts.

Consumer/provider contract tests MAY be used when multiple independently deployed consumers require stronger guarantees.

Schema validation alone does not prove business semantics; feature/integration tests remain necessary.

---

## 20. External Provider Boundaries

Third-party APIs SHOULD be isolated behind an application-owned integration boundary when vendor semantics would otherwise leak widely.

Internal code SHOULD consume normalized concepts where practical.

Example:

```text
PaymentGateway
  ├── MidtransAdapter
  └── StripeAdapter
```

Only create such abstraction when the boundary is meaningful; do not wrap every SDK mechanically.

---

## 21. External Timeouts

Every external network call MUST have a finite timeout.

Timeouts SHOULD consider:
- upstream request budget;
- provider SLA/behavior;
- retry policy;
- user experience.

Default/infinite library timeouts MUST NOT be accepted blindly.

---

## 22. External Retries

Retry only failures likely to be transient and safe to repeat.

Retry policy SHOULD define:
- attempts;
- backoff;
- jitter;
- retryable failure categories;
- maximum total time.

Do not retry:
- invalid input;
- forbidden operations;
- deterministic provider rejection.

Avoid retry multiplication across gateway, client, and worker layers.

---

## 23. Circuit Breaking and Degradation

Circuit breakers MAY be used when repeated calls to a failing dependency create meaningful cascading risk.

Fallback/degraded behavior MUST NOT silently return incorrect authoritative data.

Examples of safer degradation:
- display temporarily unavailable;
- queue non-critical work;
- serve explicitly stale cached data where permitted.

---

## 24. Webhooks

Webhook receivers MUST treat incoming requests as untrusted.

Where provider supports it:
- verify signature/authenticity;
- validate timestamp/replay window;
- validate body/schema;
- use constant-time signature comparison via established libraries;
- preserve raw body when signature scheme requires it.

Webhook processing SHOULD be idempotent.

A successful HTTP acknowledgment SHOULD reflect provider contract expectations, not necessarily full downstream workflow completion.

---

## 25. Webhook Replay

If replay is possible:
- duplicate events MUST be safe;
- event/provider ID SHOULD be retained where useful;
- stale replay policy SHOULD be defined;
- signature verification MUST still apply.

Do not trust a callback only because its payload references an existing internal order.

---

## 26. Event Semantics

Events SHOULD describe meaningful facts.

Examples:

```text
OrderCreated
PaymentConfirmed
CoursePublished
```

Commands MAY be used intentionally:

```text
GenerateCertificate
SendNotification
```

Do not blur commands and facts when consumers need different semantics.

---

## 27. Event Ownership

The producer owns the event semantic contract.

Consumers MUST NOT reinterpret a producer event into undocumented meanings.

If consumers need different semantics, introduce:
- a new event;
- a projection;
- a translation boundary.

---

## 28. Event Envelope

Projects SHOULD standardize important metadata.

Typical fields:

```text
eventId
eventType
occurredAt
schemaVersion
correlationId
causationId
producer
tenantId (when applicable)
```

Do not include fields without actual operational/semantic use.

---

## 29. Event Payload

Events SHOULD contain enough stable information for intended consumers while avoiding unnecessary coupling.

Choose deliberately between:
- notification/event with identifier;
- event-carried state transfer.

Large full entity snapshots SHOULD NOT be emitted by default.

Sensitive data SHOULD be minimized.

---

## 30. Delivery Semantics

Distributed messaging commonly provides at-least-once effects in practice.

Consumers SHOULD assume duplicate delivery unless the architecture explicitly guarantees otherwise.

"Exactly once" claims MUST describe the actual boundary and guarantee.

Do not use the phrase casually.

---

## 31. Event Idempotency

Consumers handling duplicate-sensitive side effects MUST be idempotent.

Possible mechanisms:
- processed event table;
- unique constraint;
- idempotency key;
- state/version check;
- naturally idempotent operation.

Mechanism SHOULD match risk and scale.

---

## 32. Ordering

If logic depends on message ordering, the contract/architecture MUST define:
- ordering key;
- scope;
- what happens when order is violated;
- partitioning implications.

Do not assume global broker ordering.

---

## 33. Event Schema Evolution

Event schema changes SHOULD be backward compatible.

Prefer:
- adding optional/defaultable fields;
- preserving old semantic meaning;
- versioning when semantic break is unavoidable.

Consumers SHOULD tolerate unknown additive fields where serializer permits it.

---

## 34. Poison Messages

Consumers MUST NOT retry invalid/poison messages forever.

Define:
- retry threshold;
- dead-letter/parking mechanism;
- alert/visibility;
- replay process.

---

## 35. Correlation and Causation

Cross-boundary workflows SHOULD preserve correlation identifiers where useful for tracing.

Events MAY use causation identifiers to represent which prior command/event triggered them.

Do not overload business IDs as universal trace IDs.

---

## 36. Sensitive Data in Integration Payloads

Transmit only necessary sensitive data.

Contracts SHOULD identify sensitive fields.

Use:
- secure transport;
- least-privilege credentials;
- redaction in logs;
- encryption where risk requires it.

---

## 37. Authentication Between Systems

Machine-to-machine authentication SHOULD use appropriate mechanisms such as:
- OAuth2 client credentials;
- mTLS;
- signed requests;
- provider API credentials.

Credentials MUST be scoped and stored through approved secret management.

Do not share one broad privileged credential across unrelated integrations when avoidable.

---

## 38. Rate Limits and Quotas

External/public APIs SHOULD define behavior when rate limits or provider quotas matter.

Clients/integrations SHOULD:
- honor provider retry-after semantics where supported;
- avoid uncontrolled retry storms;
- monitor quota consumption for critical dependencies.

---

## 39. Large Payloads

Large file/media transfer SHOULD use a mechanism appropriate to size and access model.

Avoid proxying large binary payloads through application memory when object storage/direct upload is safer and simpler.

Define:
- maximum size;
- content validation;
- timeout;
- storage/access policy.

---

## 40. Integration Observability

Important integrations SHOULD provide:
- dependency name;
- operation;
- latency;
- outcome category;
- correlation;
- retry count where relevant.

Sensitive payloads MUST NOT be logged solely for debugging convenience.

---

## 41. Sandbox and Test Environments

External integrations SHOULD use provider sandbox/mock environments for development/test where possible.

Tests MUST NOT accidentally perform real production financial/destructive operations.

Production credentials MUST NOT be used in routine CI.

---

## 42. Consumer Resilience

Consumers SHOULD avoid tight assumptions about:
- field order;
- unknown additive fields;
- non-semantic formatting;
- incidental provider error text.

Depend on documented semantics, not examples alone.

---

## 43. API Documentation

Public/internal API documentation SHOULD provide:
- contract;
- authentication;
- examples;
- error model;
- pagination;
- idempotency where applicable;
- version/deprecation policy.

Generated reference documentation SHOULD derive from authoritative contracts where possible.

---

## 44. Integration Review Checklist

Review:
- authoritative contract updated;
- compatibility assessed;
- authentication;
- timeout;
- retry ownership;
- idempotency;
- error mapping;
- sensitive data;
- rate/quota behavior;
- observability;
- schema evolution;
- test evidence.

---

## 45. Exceptions

Material exceptions that change integration strategy SHOULD be documented through project architecture/ADR.

Provider-specific limitations MAY require deviations, but they SHOULD be isolated and explicit.
