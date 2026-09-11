# UX Flows — <PROJECT_NAME>

> **Peran dokumen:** Source of truth untuk **alur pengalaman pengguna lintas halaman/feature**, termasuk entry point, decision point, recovery path, dan expected user outcome.
>
> Detail behavior satu feature tetap berada di feature specification. Visual tokens dan reusable component rules berada di `DESIGN_SYSTEM.md`. Backend/security behavior berada di feature spec, architecture, dan engineering standards.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Product | `<PROJECT_NAME>` |
| Status | Draft / Review / Locked |
| Owner | `<OWNER>` |
| Last Updated | `<YYYY-MM-DD>` |

---

## 1. Prinsip UX Flow

UX flow harus:

- menggambarkan tujuan user, bukan urutan screen semata;
- mencakup happy path dan recovery path penting;
- tidak menduplikasi seluruh functional requirement;
- menyebut role/actor dan entry point;
- menghubungkan flow ke capability/feature yang relevan;
- menunjukkan kondisi yang mengubah arah flow;
- mempertimbangkan loading, empty, validation, error, forbidden, dan degraded state bila relevan.

---

## 2. Actor Overview

| Actor | Tujuan Utama | Flow Utama |
|---|---|---|
| `<ACTOR>` | `<GOAL>` | `UXF-...` |

---

## 3. Flow Index

Gunakan stable flow ID:

```text
UXF-<DOMAIN>-<NUMBER>
```

| ID | Flow | Actor | Status | Related Feature |
|---|---|---|---|---|
| `UXF-AUTH-001` | `<FLOW>` | `<ACTOR>` | Draft / Locked | `<FEATURE>` |

---

## 4. UXF-<DOMAIN>-001 — <FLOW_NAME>

### Tujuan User

> Sebagai `<ACTOR>`, saya ingin `<GOAL>`, sehingga `<OUTCOME>`.

### Entry Point

- `<ROUTE / ACTION / NOTIFICATION / DEEP LINK>`

### Preconditions

- `<PRECONDITION>`

### Primary Flow

```text
<ENTRY>
   ↓
<STEP 1>
   ↓
<STEP 2>
   ↓
<DECISION?>
  ↙       ↘
Yes       No
 ↓         ↓
<STEP>   <RECOVERY>
   \       /
      ↓
   <OUTCOME>
```

### Step Detail

| Step | User Action | System Response | UX Requirement |
|---|---|---|---|
| 1 | `<ACTION>` | `<RESPONSE>` | `<RULE>` |
| 2 | `<ACTION>` | `<RESPONSE>` | `<RULE>` |

### Success Condition

- `<SUCCESS CONDITION>`

### Related Requirements

- `CAP-...`
- `FR-...`

---

## 5. Alternate and Recovery Flows

### AF-01 — <ALTERNATE_FLOW>

**Trigger**  
`<CONDITION>`

**Expected Experience**

1. `<STEP>`
2. `<STEP>`
3. `<OUTCOME>`

### RF-01 — <RECOVERY_FLOW>

**Failure**  
`<FAILURE CONDITION>`

**User Must Be Able To**
- understand what happened;
- know whether their action succeeded;
- retry safely when appropriate;
- avoid accidental duplicate operations;
- continue through an alternative path when available.

**Recovery Steps**
1. `<STEP>`
2. `<STEP>`

---

## 6. Cross-Product States

Gunakan pola yang konsisten lintas feature.

### Loading

- jangan tampilkan blank screen jika progress dapat dikomunikasikan;
- hindari duplicate submission selama operation masih berjalan;
- gunakan skeleton/spinner/progress berdasarkan konteks.

### Empty

Empty state harus menjelaskan:
1. apa kondisi saat ini;
2. mengapa belum ada data jika diketahui;
3. action berikutnya jika tersedia.

### Validation Error

- tampilkan error sedekat mungkin dengan field/action;
- jangan menghapus valid input yang sudah diberikan user;
- fokuskan field bermasalah bila sesuai.

### Server / Dependency Error

- jangan tampilkan raw stack trace/internal code ke user;
- bedakan retryable dan non-retryable error bila pengalaman pengguna memerlukan;
- jangan menyatakan operasi gagal jika status sebenarnya unknown tanpa recovery behavior.

### Unauthorized / Forbidden

- unauthenticated user diarahkan ke authentication flow bila sesuai;
- authenticated-but-forbidden user mendapat explanation yang aman;
- UI restriction bukan security enforcement.

### Degraded / Offline

- jelaskan capability apa yang masih tersedia;
- hindari action yang akan gagal secara pasti;
- gunakan queued/retry experience hanya jika architecture mendukung.

---

## 7. Navigation Model

### Primary Navigation

| Destination | Actor | Purpose |
|---|---|---|
| `<DESTINATION>` | `<ACTOR>` | `<PURPOSE>` |

### Navigation Rules

- preserve user context where practical;
- deep links should resolve predictably;
- browser back behavior should not corrupt state;
- protected routes must handle expired sessions;
- navigation should not depend on hidden implementation state.

---

## 8. Forms and Submission

### Form Principles

- field requirement harus terlihat sebelum submit bila memungkinkan;
- client validation mempercepat feedback, server tetap authoritative;
- submission harus mempunyai clear progress state;
- destructive actions membutuhkan confirmation yang sebanding dengan risikonya;
- retry harus mempertimbangkan idempotency.

### Unsaved Changes

`<POLICY / N/A>`

---

## 9. Long-Running Operations

Jika operation memerlukan waktu cukup lama:

- berikan acknowledgment bahwa request diterima;
- jelaskan apakah user harus menunggu atau dapat meninggalkan halaman;
- tampilkan progress hanya jika progress meaningful;
- sediakan final status;
- recovery dari refresh/revisit harus jelas.

---

## 10. Notifications and Return Paths

| Trigger | Channel | Destination | Expected Action |
|---|---|---|---|
| `<TRIGGER>` | Email / Push / In-app | `<ROUTE>` | `<ACTION>` |

Deep link harus mempertimbangkan:
- authentication state;
- permission;
- expired/invalid resource;
- already-completed action.

---

## 11. Responsive Behavior

Untuk flow kritis:

| Flow | Mobile | Tablet | Desktop | Notes |
|---|---|---|---|---|
| `<FLOW>` | Supported | Supported | Supported | `<RULE>` |

Jangan membuat mobile flow yang kehilangan capability kritis tanpa keputusan product eksplisit.

---

## 12. Accessibility Flow Requirements

Flow kritis harus dapat diselesaikan dengan mempertimbangkan:

- keyboard navigation;
- visible focus;
- semantic labels;
- screen-reader announcements untuk dynamic state penting;
- error association;
- non-color-only status indication;
- reduced motion bila animasi bukan bagian esensial dari task.

---

## 13. Analytics Checkpoints

Catat hanya event product yang diperlukan untuk memahami funnel/outcome.

| Flow Step | Event | Purpose |
|---|---|---|
| `<STEP>` | `<EVENT>` | `<WHY>` |

Jangan menduplikasi telemetry implementation detail.

---

## 14. Open UX Decisions

| ID | Question | Impact | Owner |
|---|---|---|---|
| UXQ-01 | `<QUESTION>` | `<IMPACT>` | `<OWNER>` |

Behavior decision yang sudah resolved harus dipindahkan ke feature spec atau design system sesuai ownership.

---

## 15. Related Documents

- Product Brief: `../00_product/PRODUCT_BRIEF.md`
- PRD: `../00_product/PRD.md`
- Feature Specs: `../01_features/`
- Design System: `./DESIGN_SYSTEM.md`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`

---

## 16. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
