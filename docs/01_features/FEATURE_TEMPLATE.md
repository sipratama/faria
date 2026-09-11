# Feature Specification — <FEATURE_NAME>

> **Peran dokumen:** Authoritative source untuk **detailed behavior dari satu feature**.
>
> Product-level scope berada di PRD. Cross-cutting technical design berada di System Architecture/ADR. Exact public interface berada di machine-readable contracts.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Feature ID | `<FEATURE_ID>` |
| Feature Name | `<FEATURE_NAME>` |
| Status | Draft / Review / Locked / Deprecated |
| Owner | `<OWNER>` |
| Priority | P0 / P1 / P2 |
| Target Release | `<RELEASE / MILESTONE>` |
| Last Updated | `<YYYY-MM-DD>` |

### Related Sources

- PRD: `<LINK OR SECTION>`
- Architecture: `<LINK OR SECTION>`
- ADRs: `<LINKS>`
- API Contract: `<LINK>`
- Event Contract: `<LINK>`
- UX Flow / Design: `<LINK>`

---

## 1. Feature Intent

### Problem Addressed

<Problem user/product apa yang diselesaikan feature ini?>

### Desired Outcome

<Apa yang menjadi mungkin atau lebih baik setelah feature tersedia?>

### Actors

| Actor | Role in Feature |
|---|---|
| `<ACTOR>` | `<ROLE>` |

---

## 2. Scope

### In Scope

- `<BEHAVIOR>`
- `<BEHAVIOR>`

### Out of Scope

- `<BEHAVIOR>`
- `<BEHAVIOR>`

Out-of-scope item tidak boleh diimplementasikan opportunistically.

---

## 3. Feature Flow

Bagian ini hanya untuk flow di dalam feature.

Cross-feature journey sebaiknya direferensikan dari `../03_design/UX_FLOWS.md`.

### Primary Flow

```text
<START>
   ↓
<STEP>
   ↓
<DECISION>
  ↙   ↘
<A>   <B>
   ↓
<END>
```

1. `<STEP>`
2. `<STEP>`
3. `<STEP>`

### Alternate Flow — AF-01

1. `<STEP>`
2. `<STEP>`

---

## 4. Functional Requirements

Gunakan stable IDs.

### FR-<FEATURE>-001 — `<REQUIREMENT_TITLE>`

**Requirement**  
<Jelaskan observable behavior, bukan implementation detail.>

**Rationale**  
<Kenapa behavior ini penting?>

**Acceptance Criteria**

- Given `<PRECONDITION>`, when `<ACTION>`, then `<OUTCOME>`.
- Given `<PRECONDITION>`, when `<ACTION>`, then `<OUTCOME>`.

**Priority**  
P0 / P1 / P2

### FR-<FEATURE>-002 — `<REQUIREMENT_TITLE>`

**Requirement**  
<Description>

**Acceptance Criteria**

- Given `<PRECONDITION>`, when `<ACTION>`, then `<OUTCOME>`.

**Priority**  
P0 / P1 / P2

---

## 5. Business Rules

Business rule harus deterministic dan testable.

| ID | Rule |
|---|---|
| BR-01 | `<RULE>` |
| BR-02 | `<RULE>` |

Rule yang menjadi product-wide sebaiknya pindah ke PRD.

---

## 6. State Model

Gunakan jika feature mempunyai meaningful lifecycle state.

| State | Meaning | Allowed Next States |
|---|---|---|
| `<STATE>` | `<MEANING>` | `<STATE_2>, <STATE_3>` |

### State Invariants

- `<INVARIANT>`
- `<INVARIANT>`

---

## 7. Permissions and Authorization

| Action | Actor / Role | Condition |
|---|---|---|
| `<ACTION>` | `<ROLE>` | `<CONDITION>` |

Authoritative authorization harus enforced pada trusted/backend boundary sesuai architecture.

Frontend visibility bukan security enforcement.

---

## 8. Data Requirements

Product-relevant data saja; jangan menduplikasi physical database schema.

### Inputs

| Field / Concept | Required | Rules |
|---|---:|---|
| `<INPUT>` | Yes / No | `<VALIDATION>` |

### Outputs

| Field / Concept | Description |
|---|---|
| `<OUTPUT>` | `<DESCRIPTION>` |

### Sensitive Data

`<NONE / DESCRIPTION>`

Physical schema berada di Data Model + migrations/schema.

---

## 9. API and Integration Dependencies

Jangan copy full contract ke sini.

### APIs

| Operation | Contract | Purpose |
|---|---|---|
| `<METHOD / OPERATION>` | `<OPENAPI LINK>` | `<PURPOSE>` |

### Events

| Event | Direction | Contract | Purpose |
|---|---|---|---|
| `<EVENT>` | Produce / Consume | `<SCHEMA LINK>` | `<PURPOSE>` |

### External Services

| Service | Purpose | Failure Impact |
|---|---|---|
| `<SERVICE>` | `<PURPOSE>` | `<IMPACT>` |

---

## 10. UX and UI States

Isi bila feature user-facing.

Required states yang relevan:

- Default
- Loading
- Empty
- Success
- Validation error
- Server/dependency error
- Unauthorized / forbidden
- Offline / degraded

### UX Rules

- `<RULE>`
- `<RULE>`

### Accessibility

- `<KEYBOARD / SCREEN READER / FOCUS / CONTRAST REQUIREMENT>`

Reusable visual pattern tetap berada di Design System.

---

## 11. Failure and Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC-01 | `<SCENARIO>` | `<EXPECTED BEHAVIOR>` |
| EC-02 | `<SCENARIO>` | `<EXPECTED BEHAVIOR>` |

Pertimbangkan bila relevan:
- duplicate request;
- retry;
- partial failure;
- timeout;
- race condition;
- stale data;
- expired credential;
- invalid state transition;
- unavailable dependency;
- malformed/large input;
- repeated user action.

---

## 12. Security and Privacy

### Threat-Sensitive Behavior

- `<AUTHENTICATION / AUTHORIZATION / INPUT / FILE / PAYMENT / ETC.>`

### Security Requirements

- `<REQUIREMENT>`

### Privacy Requirements

- `<RETENTION / MASKING / CONSENT / DATA MINIMIZATION / N/A>`

Update Threat Model bila feature memperkenalkan trust boundary atau material threat baru.

---

## 13. Observability

Definisikan hanya signal yang berguna untuk behavior penting.

### Logs
- `<IMPORTANT STRUCTURED EVENT>`

### Metrics
- `<METRIC>`

### Traces
- `<IMPORTANT SPAN / EXTERNAL CALL>`

### Business Events
- `<PRODUCT OR DOMAIN EVENT>`

Sensitive value tidak boleh masuk telemetry tanpa kebutuhan yang benar.

---

## 14. Test Scenarios

| Test ID | Requirement | Level | Scenario |
|---|---|---|---|
| T-001 | `FR-<FEATURE>-001` | Unit / Integration / E2E / Contract | `<SCENARIO>` |

### Minimum Regression Coverage

- `<CRITICAL PATH>`
- `<FAILURE PATH>`
- `<PERMISSION PATH>`

Test implementation detail berada di Testing Standard.

---

## 15. Rollout and Migration

Isi bila behavior berdampak pada production rollout.

### Rollout Strategy

`<DIRECT / FEATURE FLAG / PHASED / CANARY / OTHER>`

### Data Migration

`<NONE / DESCRIPTION>`

### Backward Compatibility

`<NOT APPLICABLE / REQUIREMENTS>`

### Rollback / Recovery

`<STRATEGY>`

---

## 16. Dependencies

### Upstream
- `<FEATURE / SERVICE / CONTRACT>`

### Downstream
- `<FEATURE / SERVICE / CONSUMER>`

---

## 17. Open Questions

| ID | Question | Owner | Blocking? |
|---|---|---|---|
| Q-01 | `<QUESTION>` | `<OWNER>` | Yes / No |

Jangan sembunyikan unresolved product decision di implementation comment.

---

## 18. Definition of Done

- [ ] P0 requirements implemented.
- [ ] Acceptance Criteria pass.
- [ ] API/event contracts synchronized.
- [ ] Authorization enforced.
- [ ] Required UI states implemented.
- [ ] Relevant automated tests pass.
- [ ] Important failure paths covered.
- [ ] Security/privacy implications addressed.
- [ ] Observability sufficient for important paths.
- [ ] Migration/rollout ready when applicable.
- [ ] Affected authoritative docs are current.
- [ ] Known limitations explicit.

---

## 19. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
