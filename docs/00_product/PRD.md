# Product Requirements Document (PRD) — <PROJECT_NAME>

> **Peran dokumen:** Source of truth untuk **apa yang harus disediakan product pada level capability, cross-feature behavior, user journey, dan release scope**.
>
> Product purpose, target user, success metrics, dan product-level assumptions berada di `PRODUCT_BRIEF.md`. Detailed behavior satu feature berada di `docs/01_features/<feature>.md`. Technical design berada di architecture/ADR/contracts.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Product | `<PROJECT_NAME>` |
| Status | Draft / Review / Locked |
| Version | `0.1` |
| Owner | `<OWNER>` |
| Last Updated | `<YYYY-MM-DD>` |
| Target Release / Phase | `<MILESTONE>` |

---

## 1. Product Summary

<Jelaskan product dalam 2–4 kalimat dari sisi capability dan user outcome. Jangan mengulang seluruh Product Brief.>

### Product Brief Reference

Canonical product intent:

`./PRODUCT_BRIEF.md`

Jika product purpose, target users, strategic outcome, success metric, atau product-level assumption berubah, update Product Brief.

---

## 2. Actors

Hanya actor yang diperlukan untuk memahami product behavior.

| Actor | Primary Goal | Access / Responsibility |
|---|---|---|
| `<ACTOR>` | `<GOAL>` | `<SCOPE>` |

Detailed persona/context tetap berada di Product Brief.

---

## 3. Product Scope

### In Scope

- `<CAPABILITY>`
- `<CAPABILITY>`

### Out of Scope

- `<OUT_OF_SCOPE>`
- `<OUT_OF_SCOPE>`

Product Brief menjelaskan MVP hypothesis/boundary. PRD menerjemahkannya menjadi capability scope yang lebih konkret.

---

## 4. Product Capabilities

Gunakan stable capability ID:

```text
CAP-<DOMAIN>-<NUMBER>
```

### CAP-<DOMAIN>-001 — <CAPABILITY_NAME>

**Description**  
<Jelaskan capability dari sudut pandang product.>

**User Outcome**  
<Outcome yang diterima user.>

**Primary Actors**
- `<ACTOR>`

**Priority**  
P0 / P1 / P2

**Related Feature Specs**
- `../01_features/<feature>.md`

### CAP-<DOMAIN>-002 — <CAPABILITY_NAME>

**Description**  
<Description>

**User Outcome**  
<Outcome>

**Priority**  
P0 / P1 / P2

**Related Feature Specs**
- `../01_features/<feature>.md`

---

## 5. Primary User Journeys

PRD hanya menyimpan cross-feature journey.

Detailed within-feature flow berada di Feature Spec. UX interaction detail dapat berada di `../03_design/UX_FLOWS.md`.

### J-01 — <JOURNEY_NAME>

**Actor:** `<ACTOR>`  
**Goal:** `<GOAL>`

```text
<ENTRY>
   ↓
<STEP>
   ↓
<STEP>
   ↓
<OUTCOME>
```

**Success Condition**
- `<CONDITION>`

**Related Capabilities**
- `CAP-...`
- `CAP-...`

---

## 6. Product-Wide Rules

Hanya aturan lintas-feature atau product-wide.

| ID | Rule |
|---|---|
| PR-001 | `<PRODUCT-WIDE RULE>` |
| PR-002 | `<PRODUCT-WIDE RULE>` |

Rule yang hanya berlaku pada satu feature harus berada di Feature Spec.

---

## 7. Roles and Permissions Overview

Ini adalah product-level overview, bukan authoritative security implementation.

| Capability / Action | `<ROLE_A>` | `<ROLE_B>` | `<ROLE_C>` |
|---|---:|---:|---:|
| `<ACTION>` | Yes | No | Own only |

Detailed authorization rule tetap berada di Feature Spec dan trusted backend/security boundary.

---

## 8. UX Requirements

### Cross-Product Experience Expectations

- `<EXPECTATION>`
- `<EXPECTATION>`

### Required States

Aplikasi harus menangani state yang relevan secara konsisten:

- loading;
- empty;
- success;
- validation error;
- server/dependency error;
- unauthorized/forbidden;
- offline/degraded jika applicable.

### Responsive / Accessibility

- `<REQUIREMENT>`
- `<REQUIREMENT>`

Detailed UI pattern/tokens berada di Design System.

---

## 9. Notifications and User Communication

Isi bila product mempunyai email, push, in-app notification, atau transactional communication.

| Trigger | Audience | Channel | Purpose |
|---|---|---|---|
| `<TRIGGER>` | `<ACTOR>` | Email / Push / In-app | `<PURPOSE>` |

Final copy boleh hidup di dedicated content source.

---

## 10. Search, Filter, Sort, and Discovery

Isi hanya bila relevan.

### Search
- `<EXPECTED PRODUCT BEHAVIOR>`

### Filter
- `<EXPECTED PRODUCT BEHAVIOR>`

### Sort
- `<EXPECTED PRODUCT BEHAVIOR>`

### Discovery / Recommendation
- `<EXPECTED PRODUCT BEHAVIOR OR N/A>`

Query/index/search architecture tidak berada di PRD.

---

## 11. Analytics and Product Instrumentation

**Success metric targets tidak didefinisikan ulang di sini.**

Canonical metrics berada di:

`./PRODUCT_BRIEF.md#11-success-metrics`

PRD hanya memetakan event/instrumentation yang diperlukan untuk mengukur product behavior/outcome.

| Event | Trigger | Key Properties | Supports Metric / Question |
|---|---|---|---|
| `<EVENT_NAME>` | `<WHEN>` | `<PROPERTIES>` | `<METRIC / QUESTION>` |

Jangan memasukkan sensitive data ke analytics tanpa kebutuhan dan review yang jelas.

---

## 12. Data and Privacy Expectations

Product-level expectation:

- `<WHAT USER DATA IS REQUIRED>`
- `<WHAT USER CAN VIEW / EDIT / DELETE>`
- `<RETENTION OR CONSENT EXPECTATION>`
- `<DATA EXPORT / ACCOUNT DELETION EXPECTATION>`

Physical data model berada di Data Model dan migrations/schema.

---

## 13. Integrations

Product-level dependency pada external systems.

| Integration | Product Purpose | Critical? | Related Feature |
|---|---|---:|---|
| `<SERVICE>` | `<PURPOSE>` | Yes / No | `<FEATURE>` |

Technical protocol, retry, timeout, auth, dan compatibility berada di contracts/architecture/standards.

---

## 14. Release Scope

### Required for Release

- `CAP-...`
- `CAP-...`

### Can Be Deferred

- `CAP-...`

### Product Release Blockers

Release belum product-complete jika:

- `<BLOCKER CONDITION>`
- `<BLOCKER CONDITION>`

Technical release gate berada di Release Checklist dan CI/CD standard.

---

## 15. Delivery Dependencies

Bagian ini hanya untuk dependency yang menghambat delivery capability saat ini.

Product/business assumptions tetap authoritative di Product Brief.

| Dependency | Needed For | Risk | Status |
|---|---|---|---|
| `<DEPENDENCY>` | `<CAPABILITY>` | Low / Medium / High | Open / Ready |

---

## 16. Open Product Decisions

| ID | Decision / Question | Owner | Blocking? | Target |
|---|---|---|---:|---|
| PD-01 | `<QUESTION>` | `<OWNER>` | Yes / No | `<MILESTONE>` |

Jika decision:
- mengubah architecture → buat/update ADR;
- mengubah detailed feature behavior → update Feature Spec;
- mengubah product purpose/metric/assumption → update Product Brief.

---

## 17. Feature Specification Index

| Feature | Spec | Status | Related Capability |
|---|---|---|---|
| `<FEATURE>` | `../01_features/<feature>.md` | Draft / Locked | `CAP-...` |

PRD tidak boleh menduplikasi seluruh Functional Requirements dari Feature Specs.

---

## 18. Product Acceptance

Scope fase ini dianggap terpenuhi ketika:

- [ ] seluruh P0 capabilities tersedia;
- [ ] primary user journeys dapat diselesaikan;
- [ ] relevant feature Acceptance Criteria terpenuhi;
- [ ] instrumentation yang diperlukan untuk canonical product metrics tersedia;
- [ ] tidak ada unresolved product blocker;
- [ ] out-of-scope behavior tidak masuk tanpa keputusan eksplisit.

Engineering Definition of Done berada di `AGENTS.md` dan engineering standards.

---

## 19. Related Documents

- Product Brief: `./PRODUCT_BRIEF.md`
- Roadmap: `./ROADMAP.md`
- Feature Specs: `../01_features/`
- UX Flows: `../03_design/UX_FLOWS.md`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- NFR: `../02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`
- Data Model: `../02_architecture/DATA_MODEL.md`

---

## 20. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
