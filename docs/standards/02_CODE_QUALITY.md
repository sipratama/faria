# Code Quality Standard

> **Purpose:** Define language-agnostic expectations for readable, maintainable, reviewable code.
>
> Language/framework-specific conventions MAY add stricter rules.

---

## 1. Quality Model

Good code should be:

- correct;
- understandable;
- cohesive;
- appropriately simple;
- testable;
- observable where operationally relevant;
- consistent with surrounding architecture;
- easy to change safely.

Code quality is not measured by abstraction count, pattern count, or cleverness.

---

## 2. Prefer Clarity

Code MUST favor clear intent over condensed cleverness.

Prefer:

```text
calculateFinalPrice(order)
```

over opaque multi-purpose expressions.

Names SHOULD reveal:
- business meaning;
- responsibility;
- unit where relevant;
- state where relevant.

Avoid names such as:
- `data`;
- `obj`;
- `tmp`;
- `manager`;
- `helper`;
- `util`;

when a more specific domain name exists.

---

## 3. Single Responsibility at the Right Scale

Functions/classes/modules SHOULD have a coherent reason to change.

This does **not** mean every function must be tiny or every class must represent one statement.

Avoid:
- god services;
- catch-all utility modules;
- components handling unrelated workflows;
- classes that combine transport, business rules, persistence, and external calls without architectural reason.

---

## 4. Functions

Functions SHOULD:

- have one coherent purpose;
- expose required inputs explicitly;
- minimize hidden side effects;
- return predictable outputs;
- avoid excessive boolean mode flags.

Prefer:

```text
approveOrder(...)
rejectOrder(...)
```

over:

```text
updateOrder(order, true, false, true)
```

when the operations represent distinct domain intent.

---

## 5. Complexity

Complexity SHOULD be reduced where it improves correctness and comprehension.

Prefer:
- guard clauses;
- explicit states;
- small decision tables;
- strategy/policy objects when variability is real.

Avoid deep nesting where a simpler flow exists.

Do not introduce a design pattern only because it is well known.

---

## 6. Duplication

Not all duplication is harmful.

Remove duplication when repeated code represents the **same concept that should change together**.

Do not create premature shared abstractions for superficially similar code with different business meaning.

Prefer small intentional duplication over incorrect coupling.

---

## 7. Abstraction

An abstraction SHOULD exist because:

- a stable concept exists;
- multiple consumers need the same behavior;
- a boundary requires isolation;
- testing/replacement benefits are real;
- architecture calls for it.

An abstraction SHOULD NOT exist solely for hypothetical future flexibility.

---

## 8. Domain Language

Business concepts SHOULD use terminology consistent with product/domain documentation.

If the domain says:

```text
Enrollment
Payment Attempt
Course
Learner
```

code SHOULD avoid arbitrary synonyms such as:

```text
RegistrationThing
TxnObj
TrainingItem
UserStudent
```

unless the concepts are genuinely different.

---

## 9. State Modeling

Important state SHOULD be explicit.

Prefer:
- enums/value types;
- state objects;
- well-defined transitions;

over ambiguous combinations of booleans.

Avoid:

```text
isActive=true
isDeleted=false
isPending=true
isCompleted=true
```

if those values can represent impossible states.

---

## 10. Null / Optional Values

Absence SHOULD be modeled deliberately.

Code SHOULD distinguish:
- required value;
- optional value;
- unknown value;
- empty collection;
- not-yet-loaded state.

Do not use `null`, empty string, zero, or magic values interchangeably unless the contract explicitly defines that meaning.

---

## 11. Error Handling

Errors SHOULD preserve useful semantics.

Do not:
- swallow unexpected failures silently;
- convert every error into a generic success/fallback;
- expose stack traces/internal implementation to users;
- catch broad exceptions without a defined recovery purpose.

Errors SHOULD be translated at appropriate boundaries.

---

## 12. Validation

Validation SHOULD occur at the boundary that owns the invariant.

Examples:

- shape/format validation at transport/input boundary;
- domain invariant in domain/application behavior;
- referential/uniqueness integrity also protected by database constraints where appropriate.

Do not rely exclusively on frontend validation for authoritative rules.

---

## 13. Side Effects

Side effects SHOULD be visible in design and naming.

Code that:
- writes data;
- sends messages;
- invokes external services;
- modifies files;
- mutates global state

SHOULD NOT be hidden inside functions that appear to be simple queries/calculations.

---

## 14. Immutability

Prefer immutable data where it improves reasoning and reduces accidental mutation.

Mutation MAY be used when:
- framework/language conventions make it appropriate;
- performance requires it;
- lifecycle is clear.

Avoid uncontrolled shared mutable state.

---

## 15. Collections

Collection behavior SHOULD be clear about:

- ordering;
- uniqueness;
- mutability;
- empty behavior;
- maximum expected size.

Do not load unbounded datasets into memory without understanding scale.

---

## 16. Magic Values

Meaningful constants SHOULD have explicit names.

Avoid unexplained:

```text
86400
3
"X1"
"ACTIVE"
```

when the value encodes a business/technical rule.

Configuration SHOULD be used only when variability is operationally real.

---

## 17. Comments

Comments SHOULD explain:
- why;
- constraints;
- non-obvious tradeoffs;
- workaround context.

Comments SHOULD NOT merely restate readable code.

Bad:

```text
// increment counter
counter++;
```

Useful:

```text
// Provider retries can duplicate callbacks; increment only after idempotency check.
```

TODOs SHOULD include enough context to be actionable and SHOULD NOT replace issue tracking for significant work.

---

## 18. Dead Code

Dead code SHOULD be removed rather than commented out.

Do not keep unused implementation "in case we need it later."

Version control preserves history.

---

## 19. Formatting

Formatting SHOULD be automated using project-standard tools.

Contributors SHOULD NOT manually introduce formatting conventions that conflict with the formatter.

Generated formatting-only noise SHOULD be minimized in unrelated changes.

---

## 20. Static Analysis

Projects SHOULD use appropriate:
- compiler warnings;
- linters;
- type checking;
- static analyzers;
- architecture checks;

when ecosystem/tooling supports them.

New code SHOULD NOT introduce avoidable warnings in required checks.

---

## 21. Type Safety

Where the language supports meaningful type safety:

- prefer domain-specific types over ambiguous primitives for critical concepts;
- distinguish IDs for unrelated aggregates where practical;
- represent money/time/units deliberately;
- avoid unchecked casts where safer alternatives exist.

Do not turn every primitive into a wrapper unless it improves correctness.

---

## 22. Time

Time handling SHOULD be explicit about:
- timezone;
- clock source;
- storage representation;
- comparison semantics.

Business logic that depends on current time SHOULD be testable through an injectable/controllable clock where practical.

---

## 23. Money and Numeric Precision

Financial values MUST use a representation appropriate for exact decimal arithmetic.

Floating-point types MUST NOT be used for authoritative monetary calculations when rounding errors are unacceptable.

Currency MUST be explicit when multiple currencies are possible.

---

## 24. Security-Sensitive Code

Security-sensitive implementation MUST prioritize correctness and established libraries over clever custom logic.

Detailed rules belong in `08_SECURITY_STANDARD.md`.

---

## 25. Testability

Code SHOULD be structured so important behavior can be tested without unnecessary external dependencies.

Do not introduce dependency injection, interfaces, or indirection everywhere solely for mocking.

Create seams where architectural boundaries or meaningful substitution require them.

---

## 26. Generated Code

Generated code SHOULD:
- be clearly identifiable;
- come from a reproducible source/generator;
- not be manually edited unless the generation strategy explicitly permits it.

Source contracts/templates SHOULD be updated instead of patching generated output.

---

## 27. Review Checklist

Review code for:

- correct behavior;
- clear naming;
- unnecessary complexity;
- broken domain language;
- inappropriate coupling;
- hidden side effects;
- unbounded operations;
- weak error handling;
- impossible states;
- stale/dead code;
- meaningful testability.

---

## 28. Exceptions

Performance-critical or framework-constrained code MAY deviate from readability defaults when:

- the benefit is measured or required;
- the reason is documented;
- tests protect behavior;
- the complexity remains localized.
