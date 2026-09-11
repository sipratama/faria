# Test Strategy — <PROJECT_NAME>

> **Document role:** Authoritative source for the project's testing approach, test layers, environments, evidence expectations, and risk-based verification strategy.
>
> Detailed feature scenarios belong in feature specs. Implementation conventions belong in `09_TESTING_STANDARD.md`.

---

## 1. Objectives

Testing should provide confidence that:

- product requirements behave as specified;
- important failure paths are controlled;
- contracts remain compatible;
- persistence changes are safe;
- security boundaries are enforced;
- architecture invariants remain intact;
- releases can be verified and recovered.

Testing is risk-driven, not test-count-driven.

---

## 2. Test Principles

1. Test observable behavior over implementation detail.
2. Put tests at the lowest layer that gives meaningful confidence.
3. Use integration tests where framework/database behavior matters.
4. Use contract tests at system boundaries.
5. Reserve E2E for critical user journeys and integration confidence.
6. Defect fixes should gain regression coverage when practical.
7. Flaky tests are defects, not accepted background noise.
8. Do not use coverage percentage as the sole quality signal.

---

## 3. Test Pyramid / Portfolio

| Layer | Purpose | Typical Scope | Required? |
|---|---|---|---|
| Unit | Business logic and isolated behavior | Function/class/domain | Yes |
| Component | UI/component interaction | Frontend component | As applicable |
| Integration | DB/framework/external adapter behavior | Module boundary | Yes where relevant |
| Contract | API/event compatibility | Producer/consumer boundary | Yes for contracts |
| Architecture | Dependency/boundary rules | Codebase | Where supported |
| E2E | Critical user journeys | Full stack | Selected flows |
| Security | Security controls | Critical paths | Risk-based |
| Performance | NFR verification | Hot paths | Risk-based |
| Smoke | Deployment sanity | Production-like env | Release-dependent |

---

## 4. Requirement Traceability

Important tests should reference stable identifiers where practical:

```text
FR-PAYMENT-004
NFR-PERF-001
CAP-AUTH-001
```

Formal traceability matrices are not required unless the project profile demands them.

---

## 5. Unit Testing

Use for:
- deterministic domain logic;
- validation;
- state transitions;
- mapping;
- calculation;
- policy decisions.

Avoid testing:
- trivial getters/setters;
- framework internals;
- private implementation details solely to increase coverage.

---

## 6. Integration Testing

Integration tests should verify behavior where real infrastructure semantics matter, such as:

- database constraints and transactions;
- ORM mappings;
- migrations;
- HTTP serialization;
- authentication middleware;
- broker semantics;
- object storage;
- cache behavior.

Prefer ephemeral/containerized dependencies when practical.

---

## 7. Contract Testing

### REST

Verify implementation against OpenAPI where feasible.

Important checks:
- request validation;
- response schema;
- status codes;
- error model;
- compatibility.

### Events

Verify:
- schema;
- required metadata;
- serialization;
- compatibility;
- duplicate delivery behavior where relevant.

Contracts should not drift silently from implementation.

---

## 8. Frontend Testing

### Unit / Component
Verify:
- rendering states;
- interaction;
- validation;
- accessibility behavior;
- state transitions.

### E2E
Prioritize:
- authentication;
- onboarding;
- primary product outcome;
- payment or destructive operations;
- permission-sensitive flows;
- critical admin workflows.

Do not create E2E coverage for every visual branch if lower-level tests provide sufficient confidence.

---

## 9. Backend Testing

Prioritize:
- domain/application logic;
- authorization;
- transaction behavior;
- persistence constraints;
- idempotency;
- retries/failure mapping;
- external integration adapters;
- concurrency-sensitive behavior.

---

## 10. Database and Migration Testing

For schema changes:
- apply migrations to a realistic prior schema state;
- verify forward migration;
- verify application compatibility;
- test rollback/recovery where the migration strategy supports it;
- test important constraints;
- assess existing production data impact.

An empty-database migration alone is not sufficient evidence for risky changes.

---

## 11. Security Testing

Risk-based coverage may include:
- authorization matrix tests;
- authentication/session expiration;
- injection prevention;
- file upload validation;
- CSRF where applicable;
- SSRF-sensitive integrations;
- callback/webhook verification;
- secret scanning;
- dependency scanning;
- SAST/DAST;
- manual review / penetration testing.

Reference `THREAT_MODEL.md`.

---

## 12. Performance Testing

Performance tests verify defined NFRs.

Specify:
- workload;
- dataset;
- concurrency;
- warm/cold conditions;
- duration;
- thresholds;
- environment.

Do not compare performance numbers from materially different environments without qualification.

---

## 13. Reliability Testing

Consider:
- dependency timeout;
- retry behavior;
- duplicate event delivery;
- broker unavailability;
- database interruption;
- cache loss;
- partial failure;
- process restart;
- poison messages;
- degraded third-party service.

Use fault injection only when appropriate to project maturity/risk.

---

## 14. Test Data

Rules:
- do not use real production secrets;
- avoid unnecessary real PII;
- generate deterministic test fixtures where practical;
- clearly separate seeded demo data from test assertions;
- reset/cleanup state predictably.

---

## 15. External Services

Preferred order:
1. deterministic local fake/stub for unit/fast integration;
2. provider sandbox for integration confidence;
3. contract verification;
4. controlled end-to-end verification.

Tests should not become flaky because an unrelated public service is unstable.

---

## 16. Environments

| Environment | Test Purpose |
|---|---|
| Local | Fast development feedback |
| CI | Repeatable automated verification |
| Ephemeral/Test | Integration and migration |
| Staging | Production-like system validation |
| Production | Smoke/synthetic/observability only as appropriate |

Adjust to actual project topology.

---

## 17. CI Test Gates

Suggested order:
1. formatting/lint/static checks;
2. unit tests;
3. component tests;
4. integration/contract tests;
5. build/package;
6. security scans;
7. selected E2E;
8. deployment smoke.

Exact gates belong in CI/CD standard.

---

## 18. Flaky Test Policy

A flaky test should be:
- investigated;
- fixed promptly;
- quarantined only temporarily with owner/reason;
- not repeatedly rerun until green as a normal strategy.

---

## 19. Test Evidence

For non-trivial changes, completion evidence should include:
- commands executed;
- result;
- relevant environment;
- tests intentionally not run and why.

AI agents must not claim tests passed if they were not executed.

---

## 20. Release Verification

Release verification should be selected based on risk:
- smoke test;
- critical journey E2E;
- migration verification;
- health/readiness;
- key metrics;
- rollback readiness.

Reference `RELEASE_CHECKLIST.md`.

---

## 21. Exceptions

| Area | Exception | Risk | Owner | Review |
|---|---|---|---|---|
| `<AREA>` | `<EXCEPTION>` | `<RISK>` | `<OWNER>` | `<DATE>` |

---

## 22. Related Documents

- Feature Specs: `../01_features/`
- NFR: `../02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`
- Threat Model: `./THREAT_MODEL.md`
- Testing Standard: `../standards/09_TESTING_STANDARD.md`
- CI/CD Standard: `../standards/13_CI_CD_RELEASE.md`
- Release Checklist: `../06_delivery/RELEASE_CHECKLIST.md`

---

## 23. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
