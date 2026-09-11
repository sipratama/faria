# Observability and Reliability Standard

> **Purpose:** Define reusable rules for telemetry, failure handling, resilience, recovery, and operational visibility.
>
> Measurable reliability targets belong in `NON_FUNCTIONAL_REQUIREMENTS.md`. Operational procedures belong in `RUNBOOK.md`.

---

## 1. Core Principle

Reliable systems fail in understandable, bounded, and recoverable ways.

Observability exists to help answer:

- what failed?
- where?
- for whom?
- how often?
- why?
- what is the impact?
- can the system recover?

Do not collect telemetry without a clear operational or product purpose.

---

## 2. Reliability Ownership

Each important dependency or workflow SHOULD define:

- timeout behavior;
- retry ownership;
- idempotency;
- failure classification;
- degradation behavior;
- terminal failure;
- observability;
- recovery.

Reliability behavior MUST NOT emerge accidentally from framework defaults.

---

## 3. Structured Logging

Logs SHOULD be structured where ecosystem supports it.

Useful fields MAY include:

```text
timestamp
level
service
operation
correlationId
traceId
userId/tenantId when permitted
entityId
dependency
outcome
errorCode
durationMs
```

Do not add fields merely because they are available.

---

## 4. Logging Levels

A project SHOULD use consistent semantics.

Typical:

```text
DEBUG → developer diagnostic
INFO  → expected meaningful operational event
WARN  → abnormal but recoverable condition
ERROR → operation failed or intervention may be needed
```

Do not log routine expected validation failures as high-severity errors unless operationally meaningful.

---

## 5. Sensitive Logging

Logs MUST NOT contain:

- passwords;
- access/refresh tokens;
- API keys;
- private keys;
- session secrets;
- full card/payment credentials;
- unnecessary PII;
- sensitive request/response payloads.

Redaction SHOULD occur before log emission.

---

## 6. Correlation

Distributed or multi-step workflows SHOULD propagate correlation identifiers.

A correlation ID SHOULD remain stable across related work where useful.

Do not use business IDs as universal correlation IDs unless that is an intentional project convention.

---

## 7. Tracing

Distributed tracing SHOULD be used when cross-service/dependency latency or failure diagnosis materially benefits from it.

Trace spans SHOULD represent meaningful operations, such as:

```text
HTTP request
DB query group
external provider call
message consumption
background job
```

Do not create excessive low-value spans that increase noise/cost.

---

## 8. Metrics

Metrics SHOULD measure behavior that can drive decisions.

Categories MAY include:

### RED
- Rate
- Errors
- Duration

### USE
- Utilization
- Saturation
- Errors

### Business
- successful payment confirmations;
- enrollment completion;
- failed webhook processing;
- queue backlog.

Business metrics SHOULD NOT expose sensitive user data.

---

## 9. Metric Cardinality

Metric labels MUST avoid uncontrolled high cardinality.

Do not use raw:
- user IDs;
- order IDs;
- request IDs;
- URLs with arbitrary values

as metric dimensions.

Use logs/traces for high-cardinality investigation.

---

## 10. Health Checks

Where applicable, distinguish:

### Liveness
Can the process/runtime continue?

### Readiness
Can it safely serve traffic?

Readiness SHOULD consider only dependencies required to serve safely.

Do not make every optional third-party dependency a readiness blocker.

---

## 11. Alerts

Alerts SHOULD represent conditions requiring human attention.

Good alerts are:
- actionable;
- scoped;
- deduplicated;
- tied to impact.

Avoid alerting on every error log.

An alert SHOULD answer:

```text
What is wrong?
What is impacted?
How urgent?
Where should I look next?
```

---

## 12. SLO / Error Budget

Projects with meaningful availability objectives MAY define:

```text
SLI → measured behavior
SLO → desired target
Error Budget → tolerated unreliability
```

Examples:
- successful API responses;
- payment confirmation latency;
- job completion within deadline.

Do not create SLO bureaucracy for prototypes without operational need.

---

## 13. Timeouts

Every remote/network operation SHOULD have a finite timeout.

Timeout budget SHOULD consider:
- caller deadline;
- downstream timeout;
- retry count;
- expected user experience.

Avoid layered timeout settings that exceed upstream request deadlines.

---

## 14. Retries

Retries SHOULD be:
- bounded;
- targeted to transient failures;
- safe to repeat;
- observable.

Use backoff and jitter where appropriate.

Do not retry:
- validation failures;
- permission failures;
- deterministic business rejection.

Retry storms MUST be avoided.

---

## 15. Retry Ownership

Only one layer SHOULD generally own retries for a given failure domain.

Example:

```text
Controller
  ↓
Application
  ↓
Provider Adapter ← retry here
```

Avoid retry at:
- load balancer;
- HTTP client;
- service method;
- worker

simultaneously without deliberate design.

---

## 16. Idempotency

Duplicate-prone operations SHOULD be idempotent.

Candidates:
- webhooks;
- message consumers;
- scheduled jobs;
- user submit actions;
- payment initiation.

Idempotency strategy MUST be explicit.

---

## 17. Circuit Breakers

Circuit breakers MAY be used when repeated dependency failures can cause cascading impact.

They SHOULD define:
- failure threshold;
- open duration;
- recovery probing;
- fallback/degradation.

Do not use circuit breakers automatically for every dependency.

---

## 18. Bulkheads

Resource isolation MAY be used for:
- worker pools;
- dependency connections;
- tenant workloads;
- expensive background operations.

The goal is to prevent one workload from exhausting all capacity.

---

## 19. Rate Limiting

Rate limiting MAY protect:
- public APIs;
- expensive operations;
- login/OTP;
- third-party quota;
- abuse-prone workflows.

Rate limit behavior SHOULD be observable.

Do not use rate limiting as a substitute for capacity planning or authorization.

---

## 20. Backpressure

Async systems SHOULD define behavior when producers outpace consumers.

Options:
- queue buffering;
- producer throttling;
- load shedding;
- batch size adjustment;
- autoscaling.

Unbounded queues are not a reliability strategy.

---

## 21. Queue Lag

Message/worker systems SHOULD expose:
- backlog;
- oldest message age;
- processing rate;
- retry count;
- dead-letter volume.

A queue can appear "healthy" while users experience hours of delay.

---

## 22. Dead-Letter Handling

Dead-letter queues/failed job stores MUST have an operational process.

Define:
- why message was parked;
- alert/visibility;
- inspection;
- safe replay;
- retention.

Do not use DLQ merely to hide failed processing.

---

## 23. Graceful Degradation

Degradation MAY include:
- stale read;
- disabled optional feature;
- queued background action;
- reduced result set.

Degraded behavior MUST NOT silently violate critical business correctness.

---

## 24. Load Shedding

When overloaded, systems MAY reject low-priority work rather than fail unpredictably.

Load shedding SHOULD:
- preserve critical paths;
- return clear retry/error semantics;
- be observable.

---

## 25. Connection Pools

Database/HTTP/client pool limits SHOULD be configured intentionally.

Too-large pools may overload dependencies.

Monitor:
- utilization;
- wait time;
- exhaustion.

---

## 26. Graceful Shutdown

Services/workers SHOULD handle shutdown safely.

Where relevant:
- stop accepting new work;
- finish or safely abandon current work;
- release resources;
- commit/ack only completed messages;
- honor platform termination window.

---

## 27. Crash Recovery

Stateful workflows SHOULD be designed so process crash does not leave irrecoverable ambiguous state.

Use:
- persisted workflow state;
- idempotency;
- transaction boundary;
- retryable jobs.

Do not rely on in-memory state for critical recovery unless architecture explicitly accepts loss.

---

## 28. Partial Failure

Distributed workflows MUST expect partial failure.

Define:
- which steps are committed;
- what can retry;
- what requires compensation;
- what state is visible to user;
- how operators recover.

Avoid pretending multi-system work is atomic when it is not.

---

## 29. Compensation

Compensating actions MAY be used when rollback across systems is impossible.

Compensation SHOULD be:
- explicit;
- idempotent where practical;
- observable;
- safe to retry.

Compensation does not guarantee original state can always be restored perfectly.

---

## 30. Scheduled Jobs

Scheduled jobs SHOULD define:
- concurrency policy;
- missed schedule behavior;
- retry;
- idempotency;
- runtime limit;
- observability.

Do not assume only one scheduler instance will ever execute the job unless enforced.

---

## 31. Clock and Time Drift

Distributed systems SHOULD avoid relying on tightly synchronized clocks for correctness unless infrastructure guarantees are sufficient.

Use sequence/version/DB constraints when stronger ordering is required.

---

## 32. Dependency Failure Classification

Dependencies SHOULD distinguish at least:

```text
timeout
connection failure
rate limited
authentication failure
validation/provider rejection
server error
malformed response
```

Different categories may require different recovery.

---

## 33. Operational Dashboards

Dashboards SHOULD focus on useful signals:

- traffic;
- errors;
- latency;
- saturation;
- queue lag;
- deployment marker;
- business-critical outcomes.

Avoid dashboards with dozens of charts nobody uses.

---

## 34. Deployment Markers

Telemetry SHOULD make deployments/config changes visible where tooling supports it.

This improves incident correlation.

---

## 35. Runbook Links

Critical alerts SHOULD link to:
- runbook;
- dashboard;
- logs/traces;
- relevant service owner.

---

## 36. Incident Evidence

During incidents, preserve:
- timestamps;
- deployment versions;
- logs;
- traces;
- affected entities/users when permitted;
- dependency state.

Do not destroy evidence through immediate cleanup.

---

## 37. Reliability Testing

Risk-based tests SHOULD include where relevant:
- timeout;
- retry;
- duplicate delivery;
- dependency outage;
- queue backlog;
- DB restart;
- crash/restart;
- failover;
- recovery.

Fault injection MAY be used when maturity/risk justifies it.

---

## 38. Recovery Verification

Recovery is complete only when:
- health returns;
- critical user flow works;
- backlog recovers;
- error/latency stabilizes;
- data integrity is verified when relevant.

"Process restarted" is not sufficient proof.

---

## 39. Reliability Review Checklist

Review:
- finite timeout;
- retry ownership;
- idempotency;
- duplicate behavior;
- failure classification;
- degradation;
- queue/backpressure;
- telemetry;
- alerting;
- recovery;
- runbook.

---

## 40. Exceptions

Projects MAY use lighter reliability controls at early stages.

However, critical financial/security/data-integrity paths SHOULD retain explicit failure and recovery behavior.
