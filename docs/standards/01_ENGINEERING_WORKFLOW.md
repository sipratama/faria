# Engineering Workflow Standard

> **Purpose:** Define how engineering work moves from request to verified change.
>
> This standard governs workflow and change discipline. It does not define detailed backend, frontend, security, or testing implementation rules.

---

## 1. Core Principle

Every non-trivial change SHOULD move through:

```text
Understand
   ↓
Locate Source of Truth
   ↓
Define Change Boundary
   ↓
Implement
   ↓
Verify
   ↓
Synchronize Documentation
   ↓
Report Evidence
```

Speed does not justify skipping requirement, architecture, contract, data, or security implications.

---

## 2. Start With the Problem

Before coding, contributors MUST determine:

- requested behavior or defect;
- relevant capability/requirement IDs where available;
- authoritative feature/product source;
- affected code boundaries;
- affected contracts/data;
- applicable standards;
- verification required.

For small obvious changes, this may be lightweight.

For non-trivial changes, it SHOULD be explicit in the working notes, issue, PR, or agent plan.

---

## 3. Scope Discipline

A change MUST stay within its requested objective.

Contributors MUST NOT:

- add adjacent features without scope;
- silently refactor unrelated modules;
- replace technologies opportunistically;
- rewrite architecture solely because another pattern is preferred;
- turn a defect fix into a broad cleanup unless required to fix the defect safely.

Incidental cleanup MAY be included when:
- it is local;
- it reduces risk;
- it does not change external behavior;
- it does not materially enlarge review scope.

---

## 4. Requirement Discipline

Observable behavior changes MUST remain synchronized with their authoritative requirements.

When behavior changes:

- update PRD if product capability/scope changes;
- update feature spec if detailed behavior changes;
- preserve existing requirement IDs when semantics remain the same;
- create new IDs for genuinely new requirements;
- never reuse retired IDs for different behavior.

Implementation MUST NOT become the only place where product behavior is defined.

---

## 5. Architecture Discipline

Before crossing or changing a module/system boundary:

1. read current System Architecture;
2. read relevant accepted ADRs;
3. identify architecture invariants;
4. determine whether a new ADR is required.

A material architecture change MUST NOT be hidden inside routine implementation work.

---

## 6. Contract Discipline

Externally consumed or cross-component interfaces MUST be treated as contracts.

Changes to:
- HTTP APIs;
- events/messages;
- persistent formats;
- shared schemas;
- integration callbacks

MUST be reviewed for compatibility.

Breaking changes MUST have an explicit rollout/migration strategy.

---

## 7. Data Change Discipline

Persistent data changes MUST use the project's version-controlled schema/migration mechanism.

Contributors MUST consider:
- existing production data;
- deployment ordering;
- rollback/roll-forward;
- backward compatibility;
- constraints/indexes;
- large backfill risk.

Detailed rules belong in `07_DATA_PERSISTENCE_STANDARD.md`.

---

## 8. Work Units

A change SHOULD be reviewable as one coherent unit.

Good units:
- one feature slice;
- one defect;
- one refactor with clear boundary;
- one architecture migration step;
- one infrastructure capability.

Avoid combining unrelated concerns because they happened in the same working session.

---

## 9. Branching

The template does not mandate one branching model.

Projects MAY use:
- trunk-based development;
- short-lived feature branches;
- release branches where justified.

Regardless of model:

- branches SHOULD be short-lived;
- integration SHOULD happen frequently;
- long-running divergence SHOULD be avoided;
- protected branches SHOULD require project-appropriate checks.

---

## 10. Commit Standard

Commits SHOULD represent meaningful coherent changes.

Recommended Conventional Commit types:

```text
feat:
fix:
docs:
refactor:
test:
perf:
build:
ci:
chore:
```

Examples:

```text
feat: add learner course enrollment flow
fix: prevent duplicate payment processing
docs: add backend engineering standards
refactor: isolate order pricing policy
test: add webhook replay regression coverage
```

Commit messages SHOULD describe the change outcome, not the editing action.

Prefer:

```text
fix: enforce ownership before updating profile
```

over:

```text
update user service
```

---

## 11. Pull Requests / Change Reviews

Where review is used, a change SHOULD clearly communicate:

- what changed;
- why;
- requirement/spec reference;
- architecture impact;
- contract/data impact;
- tests/evidence;
- risks/limitations;
- migration or rollout considerations.

Large changes SHOULD be split when independent review is possible.

---

## 12. Review Priorities

Review SHOULD prioritize:

1. correctness against requirement;
2. security/data integrity;
3. architecture boundaries;
4. failure behavior;
5. compatibility;
6. test evidence;
7. maintainability;
8. style.

Do not spend most review effort on formatting while behavioral risks remain unresolved.

---

## 13. Definition of Ready

A task is ready for implementation when enough context exists to proceed safely.

For non-trivial tasks, this generally means:
- desired outcome is understood;
- relevant spec exists or requested change is clear;
- major unresolved product decisions are identified;
- affected boundaries are known;
- blocking dependencies are known.

A task does not need perfect documentation before work begins.

---

## 14. Definition of Done

A change is done when applicable conditions are met:

- behavior satisfies requirement;
- contracts are synchronized;
- migrations are included;
- architecture is respected;
- relevant tests pass;
- security/reliability implications are addressed;
- affected documentation is current;
- limitations are explicit;
- evidence is reported.

`AGENTS.md` provides the repository-wide completion rule.

---

## 15. Verification

Contributors MUST NOT claim verification that was not performed.

Completion notes SHOULD distinguish:

```text
Executed:
- <command> → passed

Not executed:
- <check> → reason
```

Manual verification SHOULD describe what was actually observed.

---

## 16. Defect Workflow

For a defect:

1. reproduce or establish credible failing behavior;
2. identify expected behavior;
3. find root cause at the appropriate depth;
4. implement the smallest safe fix;
5. add regression coverage when practical;
6. verify adjacent high-risk behavior;
7. update docs only if authoritative behavior changed or a limitation is discovered.

Do not rewrite requirements simply to match defective implementation.

---

## 17. Refactoring Workflow

Refactoring MUST preserve intended external behavior unless behavior change is explicitly in scope.

Before large refactors:
- define the boundary;
- preserve or improve tests;
- avoid mixing unrelated product changes;
- use incremental migration when risk is high.

Architecture-level refactors MAY require an ADR.

---

## 18. Dependency Changes

New dependencies SHOULD be introduced only when they provide clear value over existing capabilities.

A dependency change SHOULD consider:
- maintenance;
- security;
- license;
- ecosystem maturity;
- bundle/runtime cost;
- lock-in;
- existing alternatives.

Detailed policy belongs in `12_DEPENDENCY_SUPPLY_CHAIN.md`.

---

## 19. Emergency Changes

Emergency production fixes MAY use a reduced process when user/business risk requires speed.

However:

- security guardrails remain;
- secrets MUST remain protected;
- destructive data actions MUST remain deliberate;
- change evidence MUST be preserved;
- missing tests/docs SHOULD be repaired immediately after stabilization;
- emergency behavior SHOULD NOT become the normal workflow.

---

## 20. AI-Assisted Work

AI-generated changes are reviewed under the same engineering standard as human-generated changes.

AI assistance does not reduce the requirement for:
- scope control;
- source-of-truth consistency;
- test evidence;
- contract/data safety;
- architecture adherence.

Detailed agent behavior belongs in `14_AI_ASSISTED_DEVELOPMENT.md`.

---

## 21. Exceptions

Workflow exceptions SHOULD be documented when they materially increase delivery or operational risk.

Do not create process for process's sake. The goal is reliable delivery with minimum necessary coordination.
