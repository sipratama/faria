# Engineering Standards Index

> **Document role:** Entry point and routing map for project engineering standards.
>
> These standards define reusable engineering rules. They do not replace product requirements, feature specifications, architecture decisions, or machine-readable contracts.

---

## 1. Purpose

The standards directory exists to give humans and AI coding agents a predictable set of implementation expectations without placing every rule in `AGENTS.md`.

Use standards selectively.

Do **not** load all standards for every task.

---

## 2. Normative Language

The keywords below indicate rule strength:

- **MUST** — required unless an approved exception or ADR explicitly overrides it.
- **MUST NOT** — prohibited unless an approved exception or ADR explicitly overrides it.
- **SHOULD** — expected default; deviation requires a reasonable project-specific justification.
- **SHOULD NOT** — generally avoid; deviation should be intentional.
- **MAY** — optional.
- **PREFER** — recommended when alternatives are otherwise comparable.

Project-specific documentation may strengthen a rule.

A project-specific accepted ADR may override an architectural default when the decision is explicit and consistent with higher-level product/security constraints.

---

## 3. Source-of-Truth Boundary

Standards answer:

> **How should engineering work usually be performed?**

They do not answer:

| Question | Source |
|---|---|
| Why does the product exist? | `docs/00_product/PRODUCT_BRIEF.md` |
| What product capability is required? | `docs/00_product/PRD.md` |
| How should one feature behave? | `docs/01_features/<feature>.md` |
| How is this system actually structured? | `docs/02_architecture/SYSTEM_ARCHITECTURE.md` |
| Why was a material technical choice made? | `docs/02_architecture/adr/` |
| What is the exact API/event contract? | `contracts/` |
| What quality target must be met? | `NON_FUNCTIONAL_REQUIREMENTS.md` |
| How should code be implemented safely? | `docs/standards/` |

When a standard conflicts with an accepted project-specific ADR, the ADR owns the explicit project decision.

When a standard conflicts with a product/security requirement, the requirement takes precedence.

---

## 4. Standards Catalog

| ID | Standard | Primary Concern |
|---|---|---|
| 00 | `00_STANDARD_INDEX.md` | Routing, semantics, ownership |
| 01 | `01_ENGINEERING_WORKFLOW.md` | Work lifecycle, review, change discipline |
| 02 | `02_CODE_QUALITY.md` | Maintainable language-agnostic code |
| 03 | `03_ARCHITECTURE.md` | Boundaries, dependencies, architecture change rules |
| 04 | `04_BACKEND_STANDARD.md` | Backend application/service implementation |
| 05 | `05_FRONTEND_STANDARD.md` | Frontend application implementation |
| 06 | `06_API_INTEGRATION_STANDARD.md` | APIs, events, external integrations |
| 07 | `07_DATA_PERSISTENCE_STANDARD.md` | Database, schema, migrations, transactions |
| 08 | `08_SECURITY_STANDARD.md` | Secure implementation practices |
| 09 | `09_TESTING_STANDARD.md` | Test implementation and maintenance |
| 10 | `10_OBSERVABILITY_RELIABILITY.md` | Telemetry, failure handling, resilience |
| 11 | `11_PERFORMANCE_STANDARD.md` | Performance engineering |
| 12 | `12_DEPENDENCY_SUPPLY_CHAIN.md` | Dependencies, licenses, provenance |
| 13 | `13_CI_CD_RELEASE.md` | CI/CD and release engineering |
| 14 | `14_AI_ASSISTED_DEVELOPMENT.md` | Rules for AI-assisted coding |

---

## 5. Task Routing

Load the smallest relevant set.

### Backend Feature

Typical:

```text
01_ENGINEERING_WORKFLOW
02_CODE_QUALITY
03_ARCHITECTURE
04_BACKEND_STANDARD
+ feature-specific standards as needed
```

Add:
- `06_API_INTEGRATION_STANDARD` for API/event/integration work;
- `07_DATA_PERSISTENCE_STANDARD` for persistence changes;
- `08_SECURITY_STANDARD` for security-sensitive behavior;
- `09_TESTING_STANDARD` when implementing/reviewing tests;
- `10_OBSERVABILITY_RELIABILITY` for async/failure/telemetry work.

### Frontend Feature

Typical:

```text
01_ENGINEERING_WORKFLOW
02_CODE_QUALITY
05_FRONTEND_STANDARD
```

Add:
- `06_API_INTEGRATION_STANDARD` for API consumption;
- `08_SECURITY_STANDARD` for auth/session/security-sensitive UI;
- `09_TESTING_STANDARD` for test work;
- design docs for UX/component behavior.

### Architecture Change

Typical:

```text
01_ENGINEERING_WORKFLOW
03_ARCHITECTURE
+ relevant domain standards
```

Also read:
- System Architecture;
- relevant ADRs;
- NFRs;
- affected contracts.

### Defect Fix

Load:
- relevant feature spec;
- relevant implementation standard;
- `09_TESTING_STANDARD`.

Do not broaden a defect fix into unrelated architecture cleanup without explicit scope.

---

## 6. Project-Specific Adoption

A project does not need every standard to be equally active.

Recommended profiles:

### Fullstack Product

Use all applicable standards.

### Backend Service

Frontend standard MAY be omitted.

### Frontend-Only Application

Backend/data standards MAY be reduced, but API contract and security expectations remain relevant.

### Prototype

Operational rigor MAY be reduced, but:
- secrets MUST still be protected;
- requirements MUST NOT be invented silently;
- contract changes MUST remain explicit;
- destructive data changes MUST remain deliberate.

### Regulated / High-Risk

Projects SHOULD strengthen:
- traceability;
- security;
- audit;
- release evidence;
- change approvals;
- operational controls.

---

## 7. Exceptions

A standard exception MUST be:

1. intentional;
2. scoped;
3. justified;
4. visible to relevant contributors;
5. reviewed when the context changes.

Material architecture exceptions SHOULD be captured in an ADR.

Temporary exceptions SHOULD define a removal/review condition.

Do not create silent exceptions in implementation code.

---

## 8. Standard Maintenance

Update a standard when:

- the rule is reusable across projects/tasks;
- repeated implementation mistakes show a missing guideline;
- new engineering practice becomes the preferred baseline;
- tooling/ecosystem changes invalidate the existing rule.

Do not put project-specific product decisions into shared standards.

---

## 9. AI Agent Use

AI agents MUST:

- follow `AGENTS.md` first;
- load standards selectively;
- treat **MUST/MUST NOT** as hard constraints;
- avoid inventing a standard when one is absent;
- use established project patterns when a standard leaves room for implementation choice;
- surface material conflicts rather than silently choosing.

Detailed AI-specific behavior belongs in `14_AI_ASSISTED_DEVELOPMENT.md`.

---

## 10. Related Documents

- `AGENTS.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/02_architecture/adr/`
- `docs/04_engineering/TEST_STRATEGY.md`
- `docs/04_engineering/THREAT_MODEL.md`
