# Annotasi Template

> 🇬🇧 English · [🇮🇩 Bahasa Indonesia](./README.md)

An **AI-ready, opinionated, and production-oriented** software development template for fullstack, backend, and frontend product development.

Annotasi Template helps humans and AI coding agents such as **Codex** and **Claude Code** work from the same sources of truth—from product discovery, product intent, feature behavior, architecture, contracts, and engineering standards to release evidence.

> The goal is not to create as much documentation as possible. The goal is to maintain **shared understanding with as little duplication as possible**.

---

## What problem does this template solve?

AI-assisted development can accelerate coding, but it can easily create problems when:

- requirements live only in chat;
- AI starts shaping the repository before understanding the product;
- architecture changes without explicit decisions;
- API contracts fall behind the implementation;
- AI reads too much irrelevant context;
- business rules are scattered across the frontend, backend, and tests;
- a project has many documents but no clear indication of which ones are authoritative.

Annotasi Template uses the following flow:

```text
PROJECT DISCOVERY
      ↓
PRODUCT CONTEXT GATE
      ↓
PRODUCT BRIEF
      ↓
PRD
      ↓
FEATURE SPECS
      ↓
ARCHITECTURE + ADR
      ↓
MACHINE-READABLE CONTRACTS
      ↓
ENGINEERING STANDARDS
      ↓
IMPLEMENTATION
      ↓
TEST EVIDENCE
      ↓
RELEASE
```

The initialization principle is simple:

> **Understand the product first. Shape the repository once sufficient context is available.**

---

## Core principles

### One Concern, One Source of Truth

Each concern should have one authoritative source.

| Question | Source of Truth |
|---|---|
| How is a new project discovered and initialized? | `docs/PROJECT_INITIALIZATION.md` |
| Why does the product exist and for whom? | `docs/00_product/PRODUCT_BRIEF.md` |
| Which capabilities must be available? | `docs/00_product/PRD.md` |
| How should a feature behave? | `docs/01_features/<feature>.md` |
| How is the system structured? | `docs/02_architecture/SYSTEM_ARCHITECTURE.md` |
| Why was an architecture decision made? | `docs/02_architecture/adr/` |
| How well must the system perform? | `docs/02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md` |
| What is the persistent data model? | migrations/schema + `DATA_MODEL.md` |
| What are the REST/event contracts? | `contracts/` when used |
| How should engineering be performed? | `docs/standards/` |
| How is testing planned? | `docs/04_engineering/TEST_STRATEGY.md` |
| How is the system released/operated? | `docs/05_operations/` + `docs/06_delivery/` |

### Discovery before initialization

For a new project, AI must not immediately create an architecture, select a stack, or remove documentation based only on the repository name.

Initialization consists of:

```text
PHASE A — Project Discovery
(read-only)
        ↓
Minimum Product Context Gate
        ↓
PHASE B — Project Initialization
(repository mutation)
```

If product context is insufficient, AI should ask only for the information that is still missing.

### AI reads selectively

Do not ask AI to read the entire repository for every task.

For an initialized project, the default flow is:

```text
AGENTS.md
   ↓
relevant PRD section
   ↓
relevant feature spec
   ↓
relevant architecture / ADR
   ↓
relevant contract
   ↓
relevant engineering standard
   ↓
source code + tests
```

### Contracts before implementation drift

Changes to APIs, events, schemas, or persistent formats must update their contract/migration before or together with the implementation.

### Architecture decisions must be explicit

Material architecture changes must not exist only in code or chat. Use an ADR.

---

## Quick Start

### 1. Create a repository from the template

Click:

```text
Use this template
→ Create a new repository
```

in the Annotasi Template repository.

Alternatively, clone/copy the repository manually.

The new repository will include the documentation framework, AI instructions, engineering standards, initialization workflow, and validator.

**Do not immediately fill out the entire template or manually create a source structure.**

---

### 2. Open the new repository with Codex or Claude Code

The AI will read:

```text
AGENTS.md
        ↓
docs/PROJECT_INITIALIZATION.md
```

`AGENTS.md` is the repository-wide instruction source.

`PROJECT_INITIALIZATION.md` governs discovery-first initialization.

---

### 3. Start Project Discovery

Use the following prompt:

```text
Initialize this repository using AGENTS.md and
docs/PROJECT_INITIALIZATION.md.

Start with Project Discovery.

Execute Project Discovery immediately in this turn.
Do not merely acknowledge these instructions or describe what you would do.

Inspect the repository and the context I provide first.
Do not modify the repository until the Minimum Product Context Gate
defined in PROJECT_INITIALIZATION.md is satisfied.

If the Minimum Product Context Gate is incomplete, ask only for the
missing product context immediately.
Focus on the problem, users, desired outcome, initial scope,
non-goals, and important constraints before discussing technology.

Once my answers make the Minimum Product Context Gate PASS, continue
directly into Phase B — Project Initialization without requiring another
"proceed" prompt, unless I explicitly requested discovery-only or read-only
work.

In Phase B:
- recommend the project profile and modifiers;
- initialize only relevant project documentation;
- create feature specs only for sufficiently understood capabilities;
- establish architecture from product requirements and constraints;
- create contracts/source structure only when justified;
- generate the project README last;
- run project-mode validation;
- report unresolved decisions and evidence.

Do not invent missing product facts or architecture decisions.
```

You **do not need to define the profile, database, framework, or deployment target at the beginning**.

If the only available context is:

```text
Project: Penatika
```

the AI should **not modify the repository**.

The AI must enter Discovery Mode immediately and ask about any missing product
context, rather than merely acknowledging the instructions.

---

### 4. Provide the context you already know

This is optional, but the clearer the initial context is, the fewer discovery questions will be necessary.

Example:

```text
Project:
<PROJECT_NAME>

What I already know:
- the problem to solve;
- the primary users;
- the desired outcome;
- an outline of the first version;
- constraints that are already known.
```

There is no need to force technical answers that have not yet been decided.

---

### 5. Minimum Product Context Gate

Before the repository may be initialized, the AI must understand at least:

```text
✓ Project name
✓ Core problem
✓ Primary user
✓ Desired user outcome
✓ Initial scope / MVP hypothesis
✓ Important known constraints
```

Constraints may be:

```text
None known yet
```

if none are currently known.

The following may remain undecided:

```text
technology stack
database
deployment target
monolith / microservices
event broker
base profile
modifiers
```

---

### 6. AI recommends the project shape

After the context gate returns `PASS`, the AI determines or recommends:

```text
Base Profile
Modifiers
Active Documentation
Conditional Documentation
Known Technology Decisions
Open Technology Decisions
```

Example:

```text
Recommended Base Profile:
fullstack

Recommended Modifiers:
saas

Reason:
- the product requires a user-facing UI;
- authoritative backend behavior;
- persistent user data;
- authentication and tenant isolation.
```

The profile is an **outcome of product discovery**, not something the user must know before getting started.

---

### 7. The new repository is initialized

Initialization order:

```text
Discovery Summary
        ↓
Product Brief
        ↓
PRD
        ↓
Initial Feature Specs
        ↓
System Architecture
        ↓
Conditional Documents
        ↓
Contracts if needed
        ↓
Source Structure if justified
        ↓
Project README
        ↓
Validation
```

The project README is created **last**, so it describes a project that has actually been understood rather than merely presenting a list of `TBD` values.

---

### 8. Validate the initialization

Run:

```bash
python3 scripts/validate_template.py --project-mode
```

or, in certain environments:

```bash
python scripts/validate_template.py --project-mode
```

The validator checks structural health, such as local Markdown links and unresolved bootstrap metadata.

The validator is **not** a substitute for product, architecture, or engineering review.

---

### 9. Review the baseline before coding

Before implementation begins, review at least:

```text
PRODUCT_BRIEF.md
        ↓
Are the problem, users, and outcomes correct?

PRD.md
        ↓
Are the capabilities and scope correct?

FEATURE SPECS
        ↓
Is the initial behavior correct?

SYSTEM_ARCHITECTURE.md
        ↓
Do the technical boundaries follow the product needs?
```

Once the baseline is reasonable, commit the initialization as a project checkpoint.

Example:

```bash
git add .
git commit -m "chore: initialize project from Annotasi Template"
```

---

### 10. Start feature development

For a new feature:

1. use/copy `docs/01_features/FEATURE_TEMPLATE.md`;
2. name it after the domain/feature;
3. define stable requirement IDs such as `FR-PAYMENT-001`;
4. implement it using the context routing in `AGENTS.md`.

Example task:

```text
Implement FR-PAYMENT-001 from
docs/01_features/payment.md.

Follow AGENTS.md and load only the relevant architecture,
contracts, standards, source code, and tests.
```

---

## Template repository structure

The structure **actually provided by the template** is:

```text
.
├── README.md
├── README.en.md
├── AGENTS.md
├── CLAUDE.md
│
├── docs/
│   ├── PROJECT_INITIALIZATION.md
│   │
│   ├── 00_product/
│   │   ├── PRODUCT_BRIEF.md
│   │   ├── PRD.md
│   │   └── ROADMAP.md
│   │
│   ├── 01_features/
│   │   └── FEATURE_TEMPLATE.md
│   │
│   ├── 02_architecture/
│   │   ├── SYSTEM_ARCHITECTURE.md
│   │   ├── DATA_MODEL.md
│   │   ├── NON_FUNCTIONAL_REQUIREMENTS.md
│   │   └── adr/
│   │       └── ADR_TEMPLATE.md
│   │
│   ├── 03_design/
│   │   ├── UX_FLOWS.md
│   │   └── DESIGN_SYSTEM.md
│   │
│   ├── 04_engineering/
│   │   ├── TEST_STRATEGY.md
│   │   └── THREAT_MODEL.md
│   │
│   ├── 05_operations/
│   │   ├── DEVELOPER_SETUP.md
│   │   ├── CONFIGURATION.md
│   │   ├── DEPLOYMENT.md
│   │   └── RUNBOOK.md
│   │
│   ├── 06_delivery/
│   │   ├── RISKS.md
│   │   ├── RELEASE_CHECKLIST.md
│   │   └── KNOWN_LIMITATIONS.md
│   │
│   └── standards/
│       ├── 00_STANDARD_INDEX.md
│       ├── 01_ENGINEERING_WORKFLOW.md
│       ├── 02_CODE_QUALITY.md
│       ├── 03_ARCHITECTURE.md
│       ├── 04_BACKEND_STANDARD.md
│       ├── 05_FRONTEND_STANDARD.md
│       ├── 06_API_INTEGRATION_STANDARD.md
│       ├── 07_DATA_PERSISTENCE_STANDARD.md
│       ├── 08_SECURITY_STANDARD.md
│       ├── 09_TESTING_STANDARD.md
│       ├── 10_OBSERVABILITY_RELIABILITY.md
│       ├── 11_PERFORMANCE_STANDARD.md
│       ├── 12_DEPENDENCY_SUPPLY_CHAIN.md
│       ├── 13_CI_CD_RELEASE.md
│       └── 14_AI_ASSISTED_DEVELOPMENT.md
│
└── scripts/
    ├── README.md
    └── validate_template.py
```

Directories such as `src/`, `backend/`, `frontend/`, `contracts/openapi/`, `contracts/asyncapi/`, migrations, or deployment manifests are **created according to project needs after the product and architecture are sufficiently understood**, rather than being imposed by the template.

---

## Required vs conditional documents

Not every project must fill out every document.

### Core — almost always active

| Document | Status |
|---|---|
| `README.md` | Required after the project is initialized |
| `AGENTS.md` | Required for AI-assisted projects |
| `PRODUCT_BRIEF.md` | Required |
| `PRD.md` | Required for products with non-trivial behavior |
| `SYSTEM_ARCHITECTURE.md` | Required for non-trivial software |
| `FEATURE_TEMPLATE.md` | Retained as a template |
| `ADR_TEMPLATE.md` | Retained as a template |
| `docs/standards/` | Retained and read selectively |

### Conditional

| Document | Active when |
|---|---|
| `ROADMAP.md` | the product has more than one milestone/direction |
| `DATA_MODEL.md` | the project has persistent/domain data |
| `NON_FUNCTIONAL_REQUIREMENTS.md` | quality targets need to be explicit |
| `UX_FLOWS.md` | there are user journeys across screens/features |
| `DESIGN_SYSTEM.md` | there is a user-facing UI |
| `TEST_STRATEGY.md` | testing involves more than simple unit tests |
| `THREAT_MODEL.md` | there is authentication, user data, a network boundary, payments, uploads, administration, etc. |
| `DEVELOPER_SETUP.md` | the project needs developer onboarding |
| `CONFIGURATION.md` | runtime configuration is non-trivial |
| `DEPLOYMENT.md` | the project is deployed |
| `RUNBOOK.md` | the project is operated/supported |
| `RISKS.md` | material risks require ownership |
| `RELEASE_CHECKLIST.md` | there is a controlled production release |
| `KNOWN_LIMITATIONS.md` | contributors/users need to know about limitations |

Engineering standards remain in the repository even when not all of them are active for every task. `AGENTS.md` only routes AI to the relevant standards.

Conditional documentation **must not be removed merely because the profile is not yet known**.

---

## Project Profiles

Project profiles help determine which documentation and engineering concerns are relevant.

**Users are not required to select a profile before discovery.** By default, AI recommends a profile after the Minimum Product Context Gate is satisfied.

### Fullstack

For products that require a user-facing frontend and authoritative backend behavior.

Typically activates:

- product docs;
- feature specs;
- architecture/data/NFR;
- UX/design;
- test strategy/threat model;
- operations when approaching production.

### Backend Service

For APIs/services/background systems without a primary user-facing frontend.

Design docs can usually be deactivated. Backend, API/integration, persistence, security, testing, and reliability become priorities.

### Frontend App

For applications that are primarily client/frontend and use an existing backend/service.

Backend/persistence project docs can be reduced. Design, UX, API contract consumption, accessibility, testing, and security remain relevant.

### Prototype

For rapid exploration with a minimum baseline:

```text
PRODUCT_BRIEF
PRD
FEATURE SPECS
SYSTEM_ARCHITECTURE
AGENTS
```

Add other documents only when risk/complexity requires them.

Prototypes still follow discovery-first initialization.

### Modifiers

Once product context is known, the profile can include modifiers:

- `saas`
- `event-driven`
- `ai-enabled`
- `open-source`
- `regulated`

Detailed recommendations and the activation matrix are available in `docs/PROJECT_INITIALIZATION.md`.

---

## Codex and Claude

### Codex

`AGENTS.md` is the canonical repository-wide instruction source.

### Claude Code

`CLAUDE.md` is intentionally very thin and imports:

```text
@AGENTS.md
```

This ensures that Claude and Codex do not have two different rule sets.

Detailed AI behavior is documented in:

```text
docs/standards/14_AI_ASSISTED_DEVELOPMENT.md
```

---

## Language policy

Annotasi Template uses:

### Indonesian / hybrid

For human-facing product thinking:

- `README.md`
- `PROJECT_INITIALIZATION.md`
- `PRODUCT_BRIEF.md`
- `PRD.md`
- `ROADMAP.md`
- `FEATURE_TEMPLATE.md`
- `UX_FLOWS.md`
- `DESIGN_SYSTEM.md`

Technical vocabulary such as `Acceptance Criteria`, `Non-Goals`, `ADR`, `idempotency`, `rollback`, or `Given/When/Then` may remain in English when that is more natural.

### English

For engineering and machine-oriented artifacts:

- `AGENTS.md`
- `CLAUDE.md`
- architecture docs;
- ADRs;
- engineering/test/security/operations docs;
- `docs/standards/`;
- source code;
- database/schema naming;
- OpenAPI/AsyncAPI/contracts.

Only the README is mirrored bilingually (`README.md` + `README.en.md`). Other specifications use **one canonical language** to prevent drift.

---

## Requirement IDs

Feature behavior uses stable IDs:

```text
FR-<FEATURE>-<NUMBER>
```

Examples:

```text
FR-AUTH-001
FR-CHECKOUT-004
FR-PAYMENT-012
```

Rules:

- IDs do not change merely because of a refactor;
- retired IDs are not reused;
- tests, contracts, issues, and ADRs may reference IDs;
- do not create IDs for trivial implementation details.

---

## Versioning

Annotasi Template versions should use:

- Git Tags;
- GitHub Releases.

Repository or folder names do not need to include a version number.

---

## Validation

For the Annotasi Template repository:

```bash
python3 scripts/validate_template.py
```

For an initialized project:

```bash
python3 scripts/validate_template.py --project-mode
```

The validator performs basic structural checks and local Markdown link validation. It is not a substitute for reviewing document content.

A complete explanation is available in:

```text
scripts/README.md
```

---

## Template philosophy

Annotasi Template is not a framework that requires every project to maintain dozens of active documents.

Use the following principles:

1. **Understand the product before shaping the solution.**
2. **Keep the source of truth clear.**
3. **Delete or ignore what does not help delivery.**
4. **Load only the context needed for the current task.**

AI accelerates implementation; AI does not own product truth.
