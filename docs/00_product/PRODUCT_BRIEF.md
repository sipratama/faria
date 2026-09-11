# Product Brief — <PROJECT_NAME>

> **Peran dokumen:** Authoritative source untuk **kenapa product ini ada, siapa yang dilayani, outcome apa yang dituju, dan constraint product/business apa yang membentuknya**.
>
> Detailed feature behavior berada di PRD dan Feature Specs. Technical design berada di architecture documentation.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Product | `<PROJECT_NAME>` |
| Status | Draft / Review / Locked |
| Version | `0.1` |
| Owner | `<OWNER>` |
| Last Updated | `<YYYY-MM-DD>` |
| Primary Market | `<MARKET>` |

---

## 1. Product Vision

### Vision

<Jelaskan perubahan jangka panjang yang ingin dihasilkan product dalam satu paragraf singkat.>

### Product Statement

Untuk `<TARGET_USERS>` yang mengalami `<CORE_NEED>`, `<PROJECT_NAME>` adalah `<PRODUCT_CATEGORY>` yang memberikan `<PRIMARY_VALUE>`. Berbeda dengan `<ALTERNATIVE_OR_STATUS_QUO>`, product ini `<KEY_DIFFERENTIATOR>`.

---

## 2. Problem

### Core Problem

<Jelaskan masalah utama dari sudut pandang user/business. Jangan membahas solusi terlebih dahulu.>

### Why It Matters

<Jelaskan friction, cost, missed opportunity, risk, atau user pain yang ditimbulkan masalah tersebut.>

### Current Alternatives

Bagaimana user menyelesaikan masalah ini hari ini?

- `<ALTERNATIVE_1>`
- `<ALTERNATIVE_2>`
- `<MANUAL_WORKAROUND>`
- `<DO_NOTHING / STATUS_QUO>`

### Evidence

| Evidence | Source | Confidence |
|---|---|---|
| `<OBSERVATION>` | `<INTERVIEW / DATA / EXPERIENCE / RESEARCH>` | Low / Medium / High |

Jangan menyatakan assumption sebagai fakta tervalidasi.

---

## 3. Target Users

### Primary User

**Who:** `<PRIMARY_USER>`

**Context:**  
<Kapan dan di mana user mengalami problem?>

**Primary Job-to-be-Done**

> Ketika `<SITUATION>`, saya ingin `<MOTIVATION>`, sehingga saya dapat `<EXPECTED_OUTCOME>`.

### Secondary Users

| User | Need | Why They Matter |
|---|---|---|
| `<USER>` | `<NEED>` | `<RATIONALE>` |

### Explicitly Not Targeted Yet

- `<USER_SEGMENT>`
- `<USER_SEGMENT>`

---

## 4. Value Proposition

### Primary Value

<Outcome berguna apa yang dibuat product?>

### Differentiation

Kenapa target user memilih product ini dibanding current alternative?

1. `<DIFFERENTIATOR>`
2. `<DIFFERENTIATOR>`
3. `<DIFFERENTIATOR>`

### Product Promise

> `<ONE-SENTENCE PROMISE>`

Promise harus menggambarkan outcome, bukan daftar feature.

---

## 5. Desired Outcomes

### User Outcomes

- `<USER_OUTCOME_1>`
- `<USER_OUTCOME_2>`
- `<USER_OUTCOME_3>`

### Business / Product Outcomes

- `<BUSINESS_OUTCOME_1>`
- `<BUSINESS_OUTCOME_2>`

---

## 6. Goals

Goal harus measurable atau setidaknya observable.

### G-01 — `<GOAL_NAME>`

**Goal**  
<Description>

**Evidence of Success**  
<Metric atau observable condition>

### G-02 — `<GOAL_NAME>`

**Goal**  
<Description>

**Evidence of Success**  
<Metric atau observable condition>

---

## 7. Non-Goals

Hal berikut secara eksplisit berada di luar arah product/fase saat ini:

- `<NON_GOAL_1>`
- `<NON_GOAL_2>`
- `<NON_GOAL_3>`

Non-Goals mencegah contributor dan AI memperluas scope secara accidental.

---

## 8. Product Principles

Principles membantu keputusan ketika detailed requirement belum lengkap.

### P-01 — `<PRINCIPLE_NAME>`

<Penjelasan singkat.>

### P-02 — `<PRINCIPLE_NAME>`

<Penjelasan singkat.>

### P-03 — `<PRINCIPLE_NAME>`

<Penjelasan singkat.>

Contoh:
- outcome before feature count;
- user control before automation;
- progressive disclosure before overwhelming configuration;
- safe defaults before maximum flexibility.

Hanya gunakan principle yang benar-benar relevan.

---

## 9. MVP Boundary

### In Scope

MVP harus membuktikan:

- `<CAPABILITY / HYPOTHESIS>`
- `<CAPABILITY / HYPOTHESIS>`
- `<CAPABILITY / HYPOTHESIS>`

### Out of Scope

MVP tidak mencakup:

- `<CAPABILITY>`
- `<CAPABILITY>`
- `<CAPABILITY>`

### MVP Exit Condition

MVP dianggap cukup tervalidasi untuk investment berikutnya ketika:

<Describe required evidence.>

Detailed capability scope tetap berada di PRD.

---

## 10. Business Model

Isi hanya jika relevan.

### Monetization

`<FREE / ONE-TIME / SUBSCRIPTION / TRANSACTION / B2B / OTHER>`

### Payer

`<WHO PAYS>`

### Pricing Assumption

`<CURRENT ASSUMPTION>`

### Cost Drivers

- `<INFRASTRUCTURE>`
- `<THIRD-PARTY SERVICE>`
- `<OPERATIONS>`
- `<SUPPORT>`

Pricing assumption bukan final product requirement.

---

## 11. Success Metrics

Bagian ini adalah canonical owner untuk **product-level success metrics**.

### Primary Metric

| Metric | Definition | Target / Direction |
|---|---|---|
| `<METRIC>` | `<HOW IT IS CALCULATED>` | `<TARGET>` |

### Supporting Metrics

| Metric | Why It Matters |
|---|---|
| `<METRIC>` | `<RATIONALE>` |

### Guardrail Metrics

| Metric | Guardrail |
|---|---|
| `<METRIC>` | `<LIMIT OR EXPECTATION>` |

PRD/analytics documentation boleh mereferensikan metric ini tetapi tidak mendefinisikan target berbeda tanpa update Product Brief.

---

## 12. Constraints

### Product Constraints
- `<CONSTRAINT>`

### Business Constraints
- `<CONSTRAINT>`

### Legal / Compliance Constraints
- `<CONSTRAINT OR N/A>`

### Technical Constraints

Hanya masukkan technical constraint yang benar-benar membentuk product, misalnya:
- mandatory integration;
- platform restriction;
- data residency;
- offline requirement;
- compatibility requirement.

Detailed architecture choice tidak berada di sini.

---

## 13. Dependencies

External condition yang dibutuhkan product:

| Dependency | Why Needed | Risk |
|---|---|---|
| `<DEPENDENCY>` | `<RATIONALE>` | Low / Medium / High |

---

## 14. Assumptions

Bagian ini adalah canonical owner untuk **product-level assumptions**.

| ID | Assumption | Validation Method | Status |
|---|---|---|---|
| A-01 | `<ASSUMPTION>` | `<HOW TO TEST>` | Open |
| A-02 | `<ASSUMPTION>` | `<HOW TO TEST>` | Open |

---

## 15. Open Product Questions

| ID | Question | Owner | Target Decision |
|---|---|---|---|
| Q-01 | `<QUESTION>` | `<OWNER>` | `<DATE / MILESTONE>` |

Saat resolved, pindahkan keputusan ke authoritative document yang sesuai.

---

## 16. Related Documents

- Product Requirements: `./PRD.md`
- Product Roadmap: `./ROADMAP.md`
- Feature Specifications: `../01_features/`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- Risks: `../06_delivery/RISKS.md`

---

## 17. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
