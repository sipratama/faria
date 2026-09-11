# Testing Standard

> **Purpose:** Define reusable rules for writing, structuring, maintaining, and evaluating automated tests.
>
> `TEST_STRATEGY.md` defines which test layers and evidence a project needs. This standard defines how tests should be implemented well.

---

## 1. Core Principle

Tests exist to provide confidence in behavior and change safety.

A test SHOULD fail when required behavior breaks and SHOULD remain stable when irrelevant implementation details change.

Test quality matters more than test count.

---

## 2. Test the Contract of the Unit

Tests SHOULD focus on observable behavior at the chosen boundary.

Examples:

Unit:
```text
Given valid pending order
When confirmPayment is executed
Then state becomes PAID
```

Integration:
```text
Given migration applied and unique constraint exists
When duplicate external payment ID is inserted
Then database rejects duplicate
```

Avoid tests whose only purpose is asserting private call sequence without behavioral value.

---

## 3. Arrange / Act / Assert

Tests SHOULD have a clear structure such as:

```text
Given / Arrange
When / Act
Then / Assert
```

Complex setup SHOULD be extracted only when doing so keeps intent visible.

Do not hide the central scenario behind generic helper abstractions.

---

## 4. Test Naming

Test names SHOULD describe:
- condition;
- action;
- expected result.

Examples:

```text
rejectsEnrollmentWhenCourseIsArchived
returnsConflictWhenPaymentAlreadyConfirmed
showsRetryActionWhenCourseLoadFails
```

Avoid:

```text
test1
happyPath
serviceTest
```

---

## 5. Determinism

Automated tests MUST be deterministic enough for repeatable CI use.

Control unstable inputs such as:
- time;
- randomness;
- network;
- external service;
- thread scheduling where possible.

Do not fix flaky tests by repeatedly rerunning until green.

---

## 6. Time

Time-sensitive business logic SHOULD use a controllable clock/time source.

Avoid tests depending on:
- actual current second;
- arbitrary sleep;
- timezone of developer machine.

Use explicit timestamps/timezones.

---

## 7. Randomness

Tests MAY use generated/random data, but failures MUST be reproducible.

If property/fuzz testing is used, preserve/report the failing seed/input.

Do not use randomness simply to avoid creating meaningful fixtures.

---

## 8. Unit Tests

Unit tests SHOULD be:
- fast;
- deterministic;
- focused;
- independent of real network/database unless the selected unit boundary includes them intentionally.

Best candidates:
- business rules;
- calculations;
- state transitions;
- validation;
- policies;
- pure transformations.

Do not mock every internal collaborator solely because a mocking framework is available.

---

## 9. Mocking

Mock boundaries where substitution is meaningful.

Good mock candidates:
- third-party client;
- clock;
- message publisher;
- external payment provider.

Be cautious mocking:
- domain value objects;
- simple data classes;
- the ORM so heavily that real query behavior is never tested.

Mocks SHOULD assert meaningful interactions, not incidental internal call order.

---

## 10. Fakes and Stubs

Fakes/stubs MAY provide clearer behavior than mocks for:
- repositories;
- storage;
- provider sandbox;
- in-memory queues.

A fake MUST not be assumed equivalent to production infrastructure for semantics such as:
- transactions;
- locking;
- SQL;
- broker ordering.

Use integration tests for infrastructure-specific behavior.

---

## 11. Integration Tests

Integration tests SHOULD use real implementation of the boundary being verified.

Examples:
- actual database engine;
- actual serialization;
- actual framework routing;
- actual migration;
- actual cache/broker where semantics matter.

Containerized/ephemeral infrastructure SHOULD be preferred when it improves repeatability.

---

## 12. Database Tests

Persistence tests SHOULD verify:
- mappings;
- constraints;
- transactions;
- important queries;
- locking/concurrency where relevant.

Do not rely solely on repository mocks for critical database behavior.

---

## 13. Migration Tests

Migration tests SHOULD verify upgrade paths for risky changes.

At minimum when relevant:
1. create/apply prior schema;
2. add representative existing data;
3. apply new migration;
4. verify schema/data;
5. run relevant application behavior.

Creating the latest schema from zero is not enough for migration compatibility.

---

## 14. Contract Tests

Contract tests SHOULD ensure:
- implementation matches OpenAPI/event schema;
- required fields/status codes are correct;
- producer/consumer compatibility is preserved.

Contract schema validation SHOULD complement, not replace, behavioral integration tests.

---

## 15. API Tests

API tests SHOULD verify externally meaningful behavior:
- authorization;
- validation;
- status;
- response/error schema;
- idempotency;
- state transition.

Avoid asserting unstable headers/internal implementation unless contract requires them.

---

## 16. Event Tests

Event tests SHOULD verify:
- event semantic trigger;
- schema;
- required metadata;
- duplicate handling;
- ordering/version behavior where relevant.

A producer test SHOULD not merely assert "publisher called" if payload semantics matter.

---

## 17. Frontend Component Tests

Component tests SHOULD focus on:
- visible content;
- interaction;
- validation;
- accessibility;
- async state.

Prefer querying elements by accessible/user-facing semantics where tool ecosystem supports it.

Avoid tests tightly coupled to CSS class names or DOM structure without behavioral reason.

---

## 18. End-to-End Tests

E2E SHOULD cover selected critical journeys, not every branch.

Good candidates:
- sign in;
- onboarding;
- core product outcome;
- checkout/payment;
- critical admin workflow;
- permission-sensitive operation.

E2E SHOULD NOT replace lower-level tests for detailed business rules.

---

## 19. Security Tests

Security-sensitive behavior SHOULD have explicit automated tests where practical.

Examples:
- role denied;
- other user's resource denied;
- other tenant denied;
- expired token denied;
- invalid webhook signature denied;
- path traversal input rejected.

Do not test only successful authorized paths.

---

## 20. Performance Tests

Performance tests MUST define:
- environment;
- workload;
- concurrency;
- data size;
- duration;
- success threshold.

Performance test result without workload context is not meaningful.

---

## 21. Regression Tests

A defect fix SHOULD add a regression test when practical.

The test SHOULD:
- fail before the fix;
- pass after the fix;
- represent the observed defect at the most meaningful stable layer.

Do not add overly broad E2E coverage if a focused unit/integration test proves the defect.

---

## 22. Test Data

Test data SHOULD be:
- minimal;
- explicit;
- valid for the scenario.

Builders/factories MAY reduce repetitive setup.

Avoid giant "default everything" fixtures that hide which fields matter.

---

## 23. Builders / Factories

Builders SHOULD provide sensible valid defaults while allowing scenario-specific overrides.

Example concept:

```text
anOrder()
  .pending()
  .withTotal(100)
```

Do not create builders so generic that invalid/impossible object state becomes easy.

---

## 24. Shared Fixtures

Shared fixtures MAY reduce expensive setup.

They MUST NOT create hidden coupling/order dependency between tests.

Tests SHOULD remain independently runnable.

---

## 25. Isolation

Tests MUST NOT depend on execution order unless a deliberate scenario framework explicitly defines it.

Database tests SHOULD reset/isolate state predictably.

Parallel execution SHOULD be considered when shared resources exist.

---

## 26. Cleanup

Cleanup MUST be safe even after test failure.

Prefer:
- transaction rollback;
- ephemeral database/container;
- isolated namespace/schema;
- deterministic teardown.

Do not leave production/sandbox financial resources unintentionally.

---

## 27. External Service Tests

Routine CI SHOULD NOT depend on unstable public production endpoints.

Use:
- stub/fake;
- local mock;
- provider sandbox;
- scheduled integration check

according to confidence needs.

Provider sandbox tests SHOULD be separated when rate/quota/flakiness makes them unsuitable for every commit.

---

## 28. Network Calls

Unexpected real network calls in unit tests SHOULD fail or be prevented where tooling permits.

This prevents:
- flakiness;
- data leakage;
- accidental cost;
- real side effects.

---

## 29. Assertions

Assertions SHOULD be specific enough to explain failure.

Prefer:

```text
expected payment status CONFIRMED but was PENDING
```

over generic:

```text
assertTrue(result)
```

when richer semantic assertions are available.

---

## 30. Over-Assertion

Tests SHOULD NOT assert every field when only a subset defines required behavior.

Over-assertion creates fragile tests and discourages safe evolution.

Assert the contract relevant to the scenario.

---

## 31. Snapshot Tests

Snapshot tests MAY be useful for stable structured output/UI.

They SHOULD NOT become the main testing mechanism for interactive/business behavior.

Snapshots MUST be reviewed when updated; do not accept large snapshot changes blindly.

---

## 32. Coverage

Coverage MAY identify untested areas.

Coverage percentage MUST NOT be treated as proof of quality.

Projects MAY set coverage gates when useful, but should prioritize:
- critical business paths;
- failure paths;
- security;
- migration/integration;
- changed code risk.

Do not add meaningless tests to satisfy a number.

---

## 33. Mutation Testing

Mutation testing MAY be used for high-value logic to evaluate assertion strength.

It is optional and SHOULD be applied where benefit justifies runtime/tooling cost.

---

## 34. Property-Based Testing

Property-based testing MAY be valuable for:
- parsers;
- calculations;
- state invariants;
- serialization;
- boundary conditions.

Properties MUST represent meaningful invariants.

---

## 35. Concurrency Tests

Concurrency-sensitive logic SHOULD be tested with scenarios that can actually expose races where practical.

Do not rely only on sequential unit tests for:
- duplicate payment;
- inventory decrement;
- unique reservation;
- optimistic lock.

Database/integration-level concurrency tests MAY be necessary.

---

## 36. Flaky Tests

Flaky tests are defects.

A flaky test SHOULD be:
1. investigated;
2. fixed;
3. temporarily quarantined only when necessary;
4. assigned ownership/review if quarantined.

Do not normalize "rerun failed CI."

---

## 37. Slow Tests

Slow tests SHOULD be categorized and placed appropriately in the pipeline.

Do not weaken meaningful integration/E2E tests solely because they are slower.

Instead consider:
- parallelization;
- reduced setup;
- targeted execution;
- scheduled suites.

---

## 38. Test Categories / Tags

Projects MAY classify tests such as:

```text
unit
integration
contract
e2e
security
performance
slow
```

Categories SHOULD map to clear execution environments/pipelines.

---

## 39. Local Developer Feedback

Developers SHOULD have a fast command for meaningful pre-commit/iteration feedback.

Example:

```text
test:unit
test:changed
```

The exact command is project-specific.

Fast feedback does not remove broader CI gates.

---

## 40. CI Behavior

Tests in CI SHOULD:
- produce useful failure output;
- preserve relevant reports/artifacts;
- avoid hidden retries that mask flakiness;
- use consistent environment versions.

CI/CD specifics belong in `13_CI_CD_RELEASE.md`.

---

## 41. Failed Test Policy

Do not:
- delete a meaningful test because new code fails it;
- weaken assertion without changed requirement;
- skip tests permanently without reason.

If expected behavior changed:
1. update authoritative requirement;
2. update test;
3. update implementation.

---

## 42. Test Review

Review tests for:
- scenario intent;
- correct layer;
- deterministic setup;
- meaningful assertion;
- over-mocking;
- brittle implementation coupling;
- missing failure/security path;
- readability.

Production code and tests should be reviewed as one behavior change.

---

## 43. Test Documentation

Complex test fixtures/environments SHOULD explain:
- why they exist;
- how to run them;
- dependencies;
- limitations.

Do not document obvious individual test functions separately.

---

## 44. AI-Generated Tests

AI-generated tests MUST be held to the same quality standard.

Reviewers/agents MUST ensure AI tests do not:
- assert current implementation instead of requirement;
- mock away the behavior under test;
- pass trivially;
- duplicate existing coverage without value;
- hide failures through broad exception handling.

---

## 45. Completion Evidence

For non-trivial work, report:
- commands run;
- test categories;
- result;
- relevant environment;
- tests not run and why.

Do not claim a suite passed when only compilation or a subset ran.

---

## 46. Testing Review Checklist

Ask:
- Does this test prove required behavior?
- Is it at the appropriate layer?
- Will it catch regression?
- Is setup deterministic?
- Are assertions meaningful?
- Is real infrastructure needed?
- Is security/failure path covered?
- Is the test brittle?
- Is the test actually executed in CI?

---

## 47. Exceptions

Projects MAY adapt test layers/tooling to architecture and maturity.

High-risk changes SHOULD receive stronger evidence even if baseline project testing is lighter.
