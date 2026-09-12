# Product Requirements Document (PRD) — FARIA

> **Peran dokumen:** Source of truth untuk **apa yang harus disediakan product pada level capability, cross-feature behavior, user journey, dan release scope**.
>
> Product purpose, target user, success metrics, dan product-level assumptions berada di `PRODUCT_BRIEF.md`. Detailed behavior satu feature berada di `docs/01_features/<feature>.md`. Technical design berada di architecture/ADR/contracts.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Product | FARIA |
| Status | Draft |
| Version | `0.3` |
| Owner | sipratama |
| Last Updated | `2026-09-12` |
| Target Release / Phase | V1 — personal MVP |

---

## 1. Product Summary

FARIA adalah AI household operating system privat yang membantu household owner dan spouse mengelola alokasi bulanan uang, zakat dan sedekah, savings goals, household operating budget, personal allowance, dan household routines melalui antarmuka percakapan Telegram, dengan web dashboard untuk memonitor aktivitas agent/persona.

### Product Brief Reference

Canonical product intent:

`./PRODUCT_BRIEF.md`

---

## 2. Actors

| Actor | Primary Goal | Access / Responsibility |
|---|---|---|
| Household Owner | Mengelola finance/routine rumah tangga lewat Telegram dan dashboard | Full access ke shared household context |
| Spouse | Sama dengan Household Owner | Full access ke shared household context |
| Hermes (agent runtime) | Menginterpretasi request, mengusulkan aksi, menegakkan confirmation | Beraksi hanya lewat Household MCP tools |

---

## 3. Product Scope

### In Scope

- Monthly allocation (draft + confirm).
- Savings goals dan contributions.
- Zakat penghasilan dan sedekah sebagai recurring allocation.
- Household operating budget allocation.
- Personal allowances.
- Household routines/reminders sederhana.
- Telegram conversational interaction dengan allowlist.
- Dashboard monitoring aktivitas agent/persona.
- Human confirmation untuk material financial changes.
- AI scope boundary enforcement.

### Out of Scope

- Transaction-level expense tracking.
- Multi-household / SaaS.
- Integrasi bank/payment otomatis.
- Independent multi-agent architecture.
- Visualisasi dashboard 2D/3D.
- Mobile app.

---

## 4. Product Capabilities

### CAP-ALLOC-001 — Monthly Allocation

**Description**
Household dapat mencatat income bulanan dan menerima draft alokasi zakat, sedekah, savings, household budget, dan personal allowance, yang menjadi authoritative hanya setelah dikonfirmasi.

**User Outcome**
Alokasi bulanan yang predictable dan low-effort tanpa pencatatan transaksi.

**Primary Actors**
- Household Owner, Spouse.

**Priority**
P0

**Related Feature Specs**
- `../01_features/monthly-allocation.md`

### CAP-SAVE-001 — Savings & Goals

**Description**
Household dapat membuat savings goals, mencatat contribution, dan melihat progress terhadap target amount/date.

**User Outcome**
Progress savings yang terlihat dan dapat dipercaya.

**Priority**
P0

**Related Feature Specs**
- `../01_features/savings-goals.md`

### CAP-GIVE-001 — Zakat & Sedekah

**Description**
Household dapat menghitung zakat penghasilan dari aturan household `THP × 2.5%`, menentukan sedekah secara manual setiap bulan, dan mencatat fulfillment aktual secara terpisah dari allocation plan.

**User Outcome**
Zakat dan sedekah tidak pernah terlewat diam-diam.

**Priority**
P0

**Related Feature Specs**
- `../01_features/giving.md`

### CAP-BUDGET-001 — Household Operating Budget

**Description**
Household dapat mengalokasikan satu nominal bulanan untuk operasional rumah tangga tanpa visibility level transaksi.

**User Outcome**
Biaya operasional rumah tangga terdanai tanpa overhead pencatatan.

**Priority**
P0

**Related Feature Specs**
- TBD.

### CAP-ALLOW-001 — Personal Allowances

**Description**
Household dapat mengalokasikan personal allowance bulanan tetap per spouse; FARIA hanya melacak nominal dan status alokasi, bukan penggunaannya.

**User Outcome**
Discretionary spending yang predictable tanpa kehilangan privasi.

**Priority**
P0

**Related Feature Specs**
- TBD.

### CAP-ROUTINE-001 — Household Routines & Reminders

**Description**
Household dapat membuat routine/reminder rumah tangga berulang atau one-off (misalnya service AC, bill reminder) dan menandainya selesai.

**User Outcome**
Obligation berulang tidak terlewat.

**Priority**
P1

**Related Feature Specs**
- TBD.

### CAP-CHAT-001 — Telegram Conversational Interaction

**Description**
Household berinteraksi dengan FARIA lewat private Telegram group yang dibatasi allowlist eksplisit.

**User Outcome**
Interaksi household yang low-friction dan natural language.

**Priority**
P0

**Related Feature Specs**
- `../01_features/monthly-allocation.md` (slice pertama yang mengujinya).

### CAP-DASH-001 — Dashboard Monitoring (Agent Control Center)

**Description**
Web dashboard menampilkan status setiap persona household (Idle/Working/Scheduled/Error), current/last task, last activity, next scheduled task, health, model alias, dan pending confirmation.

**User Outcome**
Household dapat melihat apa yang sedang dilakukan FARIA dan kenapa.

**Priority**
P1

**Related Feature Specs**
- `../01_features/agent-control-center.md`

**RF-05 implementation note**
The first local, read-only control center implements current Finance/Giving state,
completed activity history, pending MonthlyAllocation drafts, and a small household
snapshot. Home Ops and Planner remain visibly inactive. Scheduled/next-task state,
Hermes/9Router live health, and AI usage/cost remain deferred until reliable sources exist.

### CAP-APPROVE-001 — Human Confirmation Boundary

**Description**
FARIA mengusulkan perubahan financial/state material; manusia harus mengonfirmasi secara eksplisit sebelum disimpan sebagai authoritative.

**User Outcome**
Household mempertahankan kontrol penuh atas keputusan yang memengaruhi uang.

**Priority**
P0

**Related Feature Specs**
- `../01_features/monthly-allocation.md`

### CAP-SCOPE-001 — AI Scope Boundary

**Description**
FARIA menolak permintaan di luar scope household finance/operations, ditegakkan lewat domain instructions, constrained tool allowlist (Household MCP), dan intent validation — bukan hanya system prompt.

**User Outcome**
FARIA tetap menjadi household assistant, bukan chatbot umum.

**Priority**
P0

**Related Feature Specs**
- TBD.

---

## 5. Primary User Journeys

### J-01 — Monthly Allocation (first vertical slice)

**Actor:** Household Owner
**Goal:** mengubah income bulanan menjadi alokasi yang terkonfirmasi

```text
Telegram: pesan income diterima
   ↓
Hermes mengenali intent monthly-allocation
   ↓
Household MCP: get current allocation rules/state
   ↓
Hermes mengusulkan DRAFT allocation
   ↓
Household mengonfirmasi
   ↓
Household MCP memvalidasi + persist ke SQLite
   ↓
FARIA mengonfirmasi summary; dashboard merefleksikan update
```

**Success Condition**
- Alokasi hanya persisted setelah konfirmasi eksplisit, dan dashboard merefleksikan state yang terkonfirmasi.

**Related Capabilities**
- `CAP-ALLOC-001`, `CAP-CHAT-001`, `CAP-APPROVE-001`, `CAP-DASH-001`

### J-02 — Record a Savings Contribution

**Actor:** Spouse
**Goal:** menambahkan uang ke savings goal yang sudah ada lewat chat

```text
Telegram: "Tambahkan 3 juta ke dana darurat"
   ↓
Hermes mengenali intent savings-contribution
   ↓
FARIA meminta konfirmasi eksplisit
   ↓
Household MCP: savings_contribution_record
   ↓
FARIA mengonfirmasi progress baru
```

**Success Condition**
- Progress savings goal merefleksikan contribution baru.

**Related Capabilities**
- `CAP-SAVE-001`, `CAP-CHAT-001`

---

## 6. Product-Wide Rules

| ID | Rule |
|---|---|
| PR-001 | Alokasi finansial yang diusulkan TIDAK BOLEH disimpan sebagai authoritative sebelum household mengonfirmasi secara eksplisit. |
| PR-002 | FARIA TIDAK BOLEH secara otonom mentransfer uang, membayar bill, memindahkan savings, mengubah aturan zakat/sedekah, mengubah target finansial, atau menghapus riwayat finansial. |
| PR-003 | FARIA HARUS menolak permintaan di luar scope household finance/operations. |
| PR-004 | Hanya identitas Telegram pada allowlist eksplisit yang boleh berinteraksi dengan FARIA. |
| PR-005 | LLM TIDAK BOLEH memiliki akses raw SQL atau shell tanpa batas; semua perubahan authoritative state melalui Household MCP tools. |

---

## 7. Roles and Permissions Overview

| Capability / Action | Household Owner | Spouse |
|---|---:|---:|
| Mencatat income / membuat draft allocation | Yes | Yes |
| Mengonfirmasi allocation | Yes | Yes |
| Membuat savings goal / mencatat contribution | Yes | Yes |
| Melihat dashboard | Yes | Yes |

Kedua role berbagi household context yang sama; V1 tidak memodelkan permission yang berbeda selain allowlist Telegram itu sendiri.

---

## 8. UX Requirements

### Cross-Product Experience Expectations

- Respons percakapan default dalam Bahasa Indonesia.
- Dashboard menampilkan state saat ini tanpa mengharuskan user memahami arsitektur di baliknya.

### Required States

- loading/working;
- empty (belum ada alokasi bulan ini);
- success (terkonfirmasi);
- validation error (nominal tidak valid);
- pending confirmation;
- unauthorized (Telegram user di luar allowlist).

### Responsive / Accessibility

- Dashboard harus dapat digunakan di browser desktop dan mobile; tidak memerlukan native app untuk V1.

---

## 9. Notifications and User Communication

Telegram sendiri adalah channel notifikasi untuk V1 — balasan dan reminder FARIA adalah transactional communication-nya; belum ada sistem email/push terpisah di V1.

---

## 10. Search, Filter, Sort, and Discovery

N/A untuk V1 — dashboard menampilkan state saat ini secara langsung; belum diperlukan search/filter/discovery.

---

## 11. Analytics and Product Instrumentation

Canonical metrics: `./PRODUCT_BRIEF.md#11-success-metrics`

| Event | Trigger | Key Properties | Supports Metric / Question |
|---|---|---|---|
| `allocation_confirmed` | Household mengonfirmasi draft allocation | period, total amount | Monthly allocation completion rate |
| `savings_contribution_recorded` | Contribution dicatat | goal, amount | Savings goals yang aktif dilacak |

---

## 12. Data and Privacy Expectations

- Data finansial household (income, allocation, savings, zakat/sedekah) diperlukan untuk menjalankan FARIA.
- Detail penggunaan personal allowance secara eksplisit TIDAK dikumpulkan — hanya nominal yang dialokasikan.
- Household memiliki dan dapat mengekspor/memeriksa data SQLite miliknya sendiri kapan pun (single-tenant, self-hosted).
- Retention: indefinite selama household menggunakan FARIA; belum ada automatic deletion policy untuk V1.

---

## 13. Integrations

| Integration | Product Purpose | Critical? | Related Feature |
|---|---|---:|---|
| Telegram Bot API | Antarmuka percakapan utama | Yes | CAP-CHAT-001 |
| 9Router → OpenRouter → LLM | Reasoning/response generation agent | Yes | Semua capability percakapan |
| Household MCP | Domain tool boundary yang terkontrol untuk authoritative state | Yes | CAP-ALLOC-001, CAP-SAVE-001, CAP-GIVE-001, CAP-BUDGET-001, CAP-ALLOW-001, CAP-ROUTINE-001 |

---

## 14. Release Scope

### Required for Release

- `CAP-ALLOC-001`, `CAP-CHAT-001`, `CAP-APPROVE-001`, `CAP-SCOPE-001`

### Can Be Deferred

- `CAP-BUDGET-001`, `CAP-ALLOW-001`, `CAP-ROUTINE-001`, `CAP-DASH-001` (dashboard dapat dimulai read-only/minimal)

### Product Release Blockers

Release belum product-complete jika:

- alokasi finansial dapat disimpan sebagai authoritative tanpa konfirmasi eksplisit;
- FARIA beraksi di luar household domain tanpa menolak.

---

## 15. Delivery Dependencies

| Dependency | Needed For | Risk | Status |
|---|---|---|---|
| Implementasi Household MCP server | CAP-ALLOC-001, CAP-SAVE-001, dan CAP-GIVE-001 | High | Implemented locally through RF-04 |
| Konfigurasi allowlist Telegram | CAP-CHAT-001 | Medium | Open |
| Akses 9Router/OpenRouter | Semua capability percakapan | Medium | Open |

---

## 16. Open Product Decisions

| ID | Decision / Question | Owner | Blocking? | Target |
|---|---|---|---:|---|
| PD-01 | RESOLVED — aturan household adalah THP × 2.5% (250 basis points), bukan nasihat agama universal | Household | No | RF-04 |
| PD-02 | RESOLVED — sedekah ditentukan manual setiap bulan; FARIA tidak membuat default/percentage | Household | No | RF-04 |
| PD-03 | Hosting provider final | Household | No | Sebelum deployment |

---

## 17. Feature Specification Index

| Feature | Spec | Status | Related Capability |
|---|---|---|---|
| Monthly Allocation | `../01_features/monthly-allocation.md` | Draft | `CAP-ALLOC-001` |
| Savings Goals | `../01_features/savings-goals.md` | Draft | `CAP-SAVE-001` |
| Giving | `../01_features/giving.md` | Draft | `CAP-GIVE-001` |

---

## 18. Product Acceptance

Scope fase ini dianggap terpenuhi ketika:

- [ ] `CAP-ALLOC-001`, `CAP-CHAT-001`, `CAP-APPROVE-001`, `CAP-SCOPE-001` tersedia;
- [ ] journey J-01 Monthly Allocation dapat diselesaikan end to end;
- [ ] Acceptance Criteria pada `monthly-allocation.md` terpenuhi;
- [ ] instrumentation `allocation_confirmed` tersedia;
- [ ] tidak ada unresolved product blocker;
- [ ] behavior out-of-scope (transaction tracking, autonomous money movement) tidak masuk tanpa keputusan eksplisit.

Engineering Definition of Done berada di `AGENTS.md` dan engineering standards.

---

## 19. Related Documents

- Product Brief: `./PRODUCT_BRIEF.md`
- Feature Specs: `../01_features/`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- Data Model: `../02_architecture/DATA_MODEL.md`

---

## 20. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.3 | `2026-09-12` | Recorded the RF-05 read-only Agent Control Center capability boundary | sipratama |
| 0.1 | `2026-09-11` | Initial draft | sipratama |
