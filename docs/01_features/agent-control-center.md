# Feature Specification — Agent Control Center

> **Peran dokumen:** Authoritative source untuk behavior `CAP-DASH-001`.
>
> Product scope berada di PRD. Boundary teknis berada di System Architecture dan ADR-0001.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Feature ID | `DASH` |
| Feature Name | Agent Control Center |
| Status | Locked |
| Owner | Household |
| Priority | P1 |
| Target Release | RF-05 |
| Last Updated | `2026-09-12` |

### Related Sources

- PRD: `../00_product/PRD.md` — `CAP-DASH-001`
- Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md` — dashboard sections
- Data Model: `../02_architecture/DATA_MODEL.md` — `AgentActivity`, `AgentPersonaState`
- ADR: `../02_architecture/adr/ADR-0001-local-read-only-dashboard-api.md`

---

## 1. Feature Intent

Memberi household tampilan lokal yang jujur untuk memahami kondisi FARIA, logical persona yang aktif, aktivitas terbaru, konfirmasi yang benar-benar tertunda, dan ringkasan kecil state household tanpa membuka jalur mutasi finansial.

---

## 2. Scope

### In Scope

- Observable health FARIA, Dashboard API, dan database.
- State logical persona Finance dan Giving.
- Home Ops dan Planner yang terlihat jelas sebagai belum diaktifkan.
- Recent persisted agent activity, persisted MonthlyAllocation draft yang menunggu konfirmasi, dan small household snapshot.
- Honest empty, stale, and unavailable states.

### Out of Scope

- Financial or household-state mutation actions.
- Independent autonomous agents, remote access/authentication, deployment, routines, reminders, scheduling, or 2D/3D visualization.
- Live Hermes Gateway, 9Router, or AI usage monitoring without an observable source.

---

## 3. Functional Requirements

### FR-DASH-001 — Show FARIA Observable Health

**Requirement**
Dashboard menunjukkan hanya health yang dapat diobservasi. Hermes Gateway, 9Router, dan AI usage harus berlabel "not monitored"/"not connected" atau tidak ditampilkan bila belum observable.

**Acceptance Criteria**

- Dashboard API dan database yang berhasil diperiksa ditampilkan sehat.
- State yang belum diobservasi tidak ditampilkan sebagai sehat.

### FR-DASH-002 — Show Logical Persona State

**Requirement**
Dashboard menampilkan Finance dan Giving sebagai logical persona dalam satu FARIA runtime. Home Ops dan Planner selalu terlihat `NOT_ACTIVATED` selama capability tersebut belum diaktifkan.

**Acceptance Criteria**

- Finance/Giving dapat menunjukkan Idle, Working, atau Error dari current monitoring state.
- UI tidak menyiratkan bahwa empat independent autonomous agents berjalan.

### FR-DASH-003 — Show Recent Agent Activity

**Requirement**
Dashboard menampilkan recent completed activities hanya dari persisted `AgentActivity`, newest first dan dengan empty state yang eksplisit.

**Acceptance Criteria**

- Persisted success/failure activity dapat muncul pada feed.
- Tidak ada activity fiktif saat belum ada persisted activity.

### FR-DASH-004 — Show Observable Pending Confirmations

**Requirement**
Pending confirmations hanya berasal dari authoritative persisted state yang dapat diobservasi. Pada RF-05, sumber tersebut adalah `MonthlyAllocation` berstatus `DRAFT`.

**Acceptance Criteria**

- Persisted MonthlyAllocation draft ditampilkan menunggu konfirmasi manusia.
- Proposal yang hanya berada di LLM/chat state tidak boleh diciptakan atau ditampilkan sebagai pending.
- Empty state ditampilkan ketika tidak ada persisted draft.

### FR-DASH-005 — Show Small Household Snapshot

**Requirement**
Dashboard menampilkan snapshot read-only yang terbatas pada latest confirmed monthly allocation, savings-goal counts, dan giving summary yang tersedia dari authoritative state.

**Acceptance Criteria**

- Snapshot mencerminkan persisted confirmed allocation, savings, dan giving data.
- Missing data ditampilkan sebagai belum tersedia atau nilai kosong yang jujur, bukan nilai household yang dibuat-buat.

### FR-DASH-006 — Remain Strictly Read-Only

**Requirement**
Dashboard tidak menyediakan action untuk mengonfirmasi alokasi, membuat atau mengubah financial state, atau menjalankan household operation. RF-05 tetap local-only.

**Acceptance Criteria**

- Dashboard surface hanya mendukung read operations.
- Mutation methods ditolak dan UI tidak menampilkan financial mutation controls.
- Kegagalan pembacaan tidak mengubah authoritative database.

### FR-DASH-007 — Handle Empty / Unavailable States Truthfully

**Requirement**
Ketika data kosong, dashboard menampilkan empty state yang eksplisit. Ketika API/frontend refresh gagal, dashboard menampilkan unavailable atau stale-data warning tanpa memfabrikasi healthy state atau household data.

**Acceptance Criteria**

- Initial API failure menampilkan outage state dan retry control.
- Refresh failure hanya mempertahankan snapshot terakhir dengan warning yang jelas.
- Error response tidak membocorkan private path atau internal detail.

---

## 4. Business Rules

| ID | Rule |
|---|---|
| BR-DASH-01 | Hanya persisted, observable state yang boleh direpresentasikan sebagai fact. |
| BR-DASH-02 | Persona cards merepresentasikan logical skills/personas dalam satu runtime, bukan independent agents. |
| BR-DASH-03 | Dashboard tidak boleh menjadi jalur authoritative mutation. |
| BR-DASH-04 | Unobservable integrations tidak boleh diberi fabricated health or usage status. |

---

## 5. UX and Failure States

| State | Required Behavior |
|---|---|
| Healthy | Tampilkan observable health dan current snapshot. |
| Working / Error | Refleksikan current active-persona monitoring state. |
| Empty | Tampilkan bahwa activity, pending confirmation, atau domain data belum tersedia. |
| Refresh failed | Tampilkan warning bahwa snapshot terakhir sedang digunakan. |
| Initial load unavailable | Tampilkan explicit unavailable state; jangan tampilkan fabricated healthy data. |

---

## 6. Minimum Regression Coverage

- Observable health and unmonitored integrations.
- Active Finance/Giving versus inactive Home Ops/Planner.
- Empty and populated activity/pending-confirmation states.
- Persisted household snapshot projection.
- Read-only API surface and absence of financial action controls.
- Generic, non-mutating API failure and explicit frontend outage state.

---

## 7. Definition of Done

- Semua `FR-DASH-*` acceptance criteria memiliki automated coverage pada backend atau frontend yang sesuai.
- Dashboard tetap local-only, read-only, dan hanya merepresentasikan observable persisted state.
- PRD, architecture, ADR, data model, source, dan tests tidak saling bertentangan.

---

## 8. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | `2026-09-12` | Added RF-05 authoritative feature behavior and acceptance closure | sipratama |
