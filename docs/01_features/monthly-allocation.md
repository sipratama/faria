# Feature Specification — Monthly Allocation

> **Peran dokumen:** Authoritative source untuk **detailed behavior dari satu feature**.
>
> Product-level scope berada di PRD. Cross-cutting technical design berada di System Architecture. Exact Household MCP tool contract untuk RF-02 tercatat di Section 9.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Feature ID | `FR-ALLOC` |
| Feature Name | Monthly Allocation |
| Status | Draft |
| Owner | sipratama |
| Priority | P0 |
| Target Release | V1 |
| Last Updated | `2026-09-12` |

### Related Sources

- PRD: `../00_product/PRD.md` (`CAP-ALLOC-001`)
- Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- ADRs: none yet
- API Contract: Household MCP tools (Section 9)
- Event Contract: N/A
- UX Flow / Design: N/A for V1

---

## 1. Feature Intent

### Problem Addressed

Household perlu mengubah income bulanan menjadi alokasi zakat/sedekah/savings/household-budget/allowance tanpa pencatatan manual atau pemeliharaan spreadsheet.

### Desired Outcome

Household dapat menyatakan income sekali lewat Telegram dan mendapatkan alokasi yang benar dan dapat dikonfirmasi, yang menjadi authoritative record setelah konfirmasi eksplisit.

### Actors

| Actor | Role in Feature |
|---|---|
| Household Owner | Menginisiasi/mengonfirmasi allocation |
| Spouse | Menginisiasi/mengonfirmasi allocation |
| Hermes | Mengusulkan draft lewat skill Finance Agent |
| Household MCP | Memvalidasi + persist allocation |

---

## 2. Scope

### In Scope

- Mencatat income bulanan.
- Menghasilkan draft allocation dari authoritative household financial rules dan nilai manual household.
- Menampilkan draft ke user.
- Langkah konfirmasi eksplisit.
- Persisting allocation yang terkonfirmasi.
- Merefleksikan state terkonfirmasi di dashboard.

### Out of Scope

- Transfer uang / pembayaran otomatis.
- Membuat SavingsContribution atau GivingRecord ketika allocation dikonfirmasi.
- Pencatatan level-transaksi di dalam bucket allocation manapun.
- Mengedit allocation yang sudah terkonfirmasi (di luar scope V1 — perlakukan sebagai periode baru).

Out-of-scope item tidak boleh diimplementasikan opportunistically.

---

## 3. Feature Flow

### Primary Flow

```text
Telegram: pesan income
   ↓
Hermes: kenali intent monthly-allocation
   ↓
Household MCP: monthly_allocation_get (state untuk periode eksplisit)
   ↓
Hermes: simpan DRAFT allocation (monthly_allocation_save_draft)
   ↓
Hermes: tampilkan draft ke user
   ↓
User: konfirmasi?
  ↙ Ya          ↘ Tidak / minta koreksi
Household MCP:      Hermes meminta koreksi
monthly_allocation_confirm dan memperbarui draft
   ↓
FARIA: ringkasan konfirmasi
   ↓
Dashboard merefleksikan state terbaru
```

1. User mengirim pesan Telegram yang menyatakan income bulanan.
2. Hermes mengenali intent monthly-allocation.
3. Hermes menentukan periode, mengambil financial rules dan allocation state, lalu menghitung zakat melalui `zakat_calculate` dari THP eksplisit.
4. Hermes meminta sedekah manual, mengambil active savings goals, dan meminta nominal budget/allowance/savings yang belum diberikan.
5. Hermes menampilkan remainder dan meminta keputusan terpisah untuk mengalokasikan atau membiarkannya unallocated.
6. Hermes membuat dan menyimpan DRAFT allocation (persisted untuk dilanjutkan/review, tetapi belum authoritative).
7. Hermes menampilkan proposed allocation ke user untuk direview.
8. User mengonfirmasi secara eksplisit (atau meminta perubahan).
9. Hermes memanggil `monthly_allocation_confirm` setelah orchestration layer menetapkan bahwa user sudah mengonfirmasi secara eksplisit.
10. Household MCP secara atomik mengubah draft yang tersimpan menjadi Confirmed di SQLite tanpa membuat ACTUAL records.
11. FARIA merespons dengan ringkasan yang terkonfirmasi.
12. Dashboard reflection tetap deferred.

### Alternate Flow — AF-01 (User meminta koreksi sebelum konfirmasi)

1. User merespons dengan koreksi (misalnya nominal savings yang berbeda).
2. Hermes mengambil draft aktif, mempertahankan nilai lain, menyimpan hanya koreksi yang diminta, lalu menampilkan draft lengkap kembali untuk konfirmasi eksplisit baru.

### Alternate Flow — AF-02 (User tidak mengonfirmasi)

1. Draft allocation tetap unconfirmed; draft boleh tersimpan untuk direvisit tetapi tidak menjadi authoritative.
2. Draft dapat direvisit di pesan berikutnya dalam periode yang sama.

---

## 4. Functional Requirements

### FR-ALLOC-001 — Record Monthly Income

**Requirement**
FARIA harus dapat menerima nominal income bulanan dari pesan Telegram dan mengasosiasikannya dengan periode allocation saat ini.

**Rationale**
Income adalah input yang diperlukan untuk menghasilkan draft allocation.

**Acceptance Criteria**

- Given user allowlisted mengirim pesan yang menyatakan nominal income bulanan, when Hermes mem-parse intent, then FARIA mengonfirmasi nominal dan periode yang dikenali.
- Given nominal tidak dapat di-parse dengan confident, when Hermes memproses pesan, then FARIA meminta klarifikasi alih-alih menebak.

**Priority**
P0

### FR-ALLOC-002 — Generate Draft Allocation

**Requirement**
FARIA harus menghasilkan draft allocation untuk zakat, sedekah, savings, household operating budget, dan personal allowance dari nilai atau rules yang telah diberikan secara eksplisit oleh household.

**Rationale**
Household tidak seharusnya menghitung ulang setiap bucket secara manual setiap bulan.

**Acceptance Criteria**

- Given THP bulanan, when Hermes menghasilkan draft, then zakat dihitung oleh Household MCP sebagai THP × 2.5% dengan integer IDR dan ROUND_HALF_UP.
- Given sedekah belum diberikan, when Hermes melengkapi draft, then FARIA meminta nominal manual dan tidak mengarang angka; nol diperbolehkan bila eksplisit.
- Given active savings goals ada, when Hermes melengkapi draft, then household dapat memberi beberapa line item `savings` dengan label goal masing-masing.
- Given dua line item personal allowance ditampilkan, when Hermes menyajikan draft, then label percakapannya adalah `Allowance Ayah Singgih` dan `Allowance Mami Farah` tanpa mengubah kategori internal `personal_allowance`.
- Given belum ada allocation rule yang dikonfigurasi untuk suatu bucket, when draft dihasilkan, then bucket tersebut ditampilkan ke user sebagai perlu input eksplisit, bukan nilai tebakan.
- Given household belum memutuskan bahwa remainder menjadi buffer, when Hermes menghitung remainder, then nilai tersebut ditampilkan sebagai belum dialokasikan dan tidak diam-diam disimpan sebagai buffer.

**Priority**
P0

### FR-ALLOC-003 — Present Draft for Confirmation

**Requirement**
FARIA harus menampilkan seluruh proposed allocation ke user sebelum allocation menjadi authoritative.

**Rationale**
Household harus dapat mereview allocation sebelum menjadi authoritative.

**Acceptance Criteria**

- Given draft allocation ada, when FARIA menampilkannya, then seluruh line item dan buffer/remainder yang dihasilkan ditampilkan.

**Priority**
P0

### FR-ALLOC-004 — Require Explicit Confirmation Before Persistence

**Requirement**
FARIA tidak boleh persist draft allocation sebagai authoritative sebelum user mengonfirmasi secara eksplisit.

**Rationale**
Ini adalah human-authority boundary inti FARIA (lihat PRD PR-001).

**Acceptance Criteria**

- Given draft allocation sudah ditampilkan, when user belum mengonfirmasi, then tidak ada authoritative allocation record untuk periode tersebut.
- Given user mengonfirmasi secara eksplisit, when Hermes memanggil Household MCP, then allocation persisted dan ditandai confirmed.
- Given user hanya mengirim acknowledgement ambigu seperti `sip`, `oke`, atau emoji, when Hermes memproses pesan, then draft tetap `DRAFT` dan tool confirm tidak dipanggil.

**Priority**
P0

### FR-ALLOC-005 — Reflect Confirmed Allocation on Dashboard

**Requirement**
Setelah allocation dikonfirmasi dan persisted, dashboard harus merefleksikan household state terbaru dan last activity persona yang relevan.

**Rationale**
Dashboard adalah Agent Control Center FARIA; harus tetap konsisten dengan authoritative state.

**Acceptance Criteria**

- Given allocation baru dikonfirmasi, when dashboard dilihat, then dashboard menampilkan allocation yang terkonfirmasi sebagai last activity persona Finance Agent.

**Priority**
P1

---

## 5. Business Rules

| ID | Rule |
|---|---|
| BR-01 | Draft allocation tidak berpengaruh terhadap authoritative household state apa pun sebelum dikonfirmasi. |
| BR-02 | Hanya identitas Telegram yang allowlisted yang dapat membuat atau mengonfirmasi allocation. |
| BR-03 | Satu periode allocation hanya boleh memiliki maksimal satu confirmed allocation; edit atau replacement setelah Confirmed berada di luar scope V1 dan tidak boleh dilakukan diam-diam. |
| BR-04 | MonthlyAllocation dan AllocationItem adalah PLAN; confirmation tidak membuktikan uang dipindahkan atau giving dipenuhi. |
| BR-05 | Remainder positif boleh tetap unallocated setelah household memutuskan demikian secara eksplisit; keputusan ini terpisah dari confirmation allocation. |

---

## 6. State Model

| State | Meaning | Allowed Next States |
|---|---|---|
| Draft | Diusulkan, belum authoritative | Confirmed, Discarded |
| Confirmed | Authoritative, persisted | (terminal untuk periode tersebut) |
| Discarded | User memilih tidak melanjutkan draft ini | Draft (draft baru dapat dibuat) |

### State Invariants

- Confirmed allocation adalah source of truth untuk PLAN periode tersebut, bukan bukti ACTUAL SavingsContribution atau GivingRecord.
- Draft tidak pernah menimpa Confirmed allocation yang sudah ada untuk periode yang sama; edit/replacement setelah Confirmed berada di luar scope V1.

---

## 7. Permissions and Authorization

| Action | Actor / Role | Condition |
|---|---|---|
| Membuat draft allocation | Household Owner / Spouse | Harus ada di Telegram allowlist |
| Mengonfirmasi allocation | Household Owner / Spouse | Harus ada di Telegram allowlist |

Allowlist Telegram adalah external identity boundary dan harus ditegakkan sebelum Hermes memproses pesan. Household MCP RF-02 membatasi capability melalui narrow tool contract dan state invariants, tetapi stdio MCP saat ini tidak membawa identitas per-user Telegram yang dapat dipercaya. Karena itu, `confirmation_reference` bila diberikan hanya metadata audit non-authoritative, bukan bukti autentikasi atau konfirmasi manusia.

Alias household seperti Ayah Singgih dan Mami Farah hanya untuk personalisasi. Alias, display name, username, dan klaim identitas di dalam pesan tidak pernah menggantikan allowlist Telegram atau trusted runtime member context.

Frontend/chat visibility bukan security enforcement.

---

## 8. Data Requirements

### Inputs

| Field / Concept | Required | Rules |
|---|---:|---|
| Nominal income bulanan | Yes | Nominal numerik positif |
| Periode allocation (bulan/tahun) | Yes | Orchestration boleh menentukan periode saat ini bila user tidak menyebutkan; Household MCP selalu menerima `YYYY-MM` eksplisit |
| Financial rules | Yes | Dibaca dari Household MCP: zakat THP × 2.5%, sedekah MANUAL, savings GOAL_BASED, remainder ASK_ALLOW_UNALLOCATED |
| Sedekah/budget/allowance/savings amount | Yes when applicable | Nilai manual household; FARIA tidak mengarang nominal |

### Outputs

| Field / Concept | Description |
|---|---|
| Draft allocation | Proposed line items + remainder, belum authoritative |
| Confirmed allocation summary | Line items yang persisted, timestamp konfirmasi |

### Sensitive Data

Nominal income dan allocation bulanan household adalah data finansial sensitif household; tidak diekspos di luar Telegram private group dan dashboard milik household sendiri.

Physical schema: lihat `../02_architecture/DATA_MODEL.md`.

---

## 9. API and Integration Dependencies

### APIs (Household MCP tools)

| Operation | Input utama | Purpose |
|---|---|---|
| `monthly_allocation_get` | `period` | Mengambil current draft dan Confirmed allocation untuk periode eksplisit |
| `monthly_allocation_save_draft` | `period`, `income_idr`, `items[]` | Membuat atau memperbarui satu active draft non-authoritative |
| `monthly_allocation_confirm` | `allocation_id`, optional `confirmation_reference` | Transisi idempotent Draft ke Confirmed setelah konfirmasi ditetapkan di orchestration layer |
| `monthly_allocation_discard_draft` | `allocation_id` | Transisi Draft ke Discarded; Confirmed tidak dapat dibuang |

Semua nominal menggunakan integer IDR. Allocation tool tidak menginfer periode, membuat actual contribution/giving, menerima raw SQL, atau menghapus Confirmed allocation. Rule/zakat reads menggunakan `financial_rules_get` dan `zakat_calculate`; savings goals menggunakan `savings_goal_list` sebagai input penyusunan plan.

### External Services

| Service | Purpose | Failure Impact |
|---|---|---|
| Telegram Bot API | Pengiriman pesan | FARIA tidak dapat merespons user |
| OpenRouter (via 9Router) | Intent recognition / response generation | Hermes tidak dapat memproses pesan |

---

## 10. UX and UI States

Required states yang relevan:

- Default (menunggu pesan income);
- Loading/working (Hermes memproses);
- Success (draft ditampilkan / terkonfirmasi);
- Validation error (nominal tidak dapat di-parse);
- Pending confirmation;
- Unauthorized (pengirim di luar allowlist).

### UX Rules

- Draft tidak boleh pernah auto-confirmed secara diam-diam.
- Konfirmasi harus jelas merujuk ke draft terakhir dan setara dengan `Konfirmasi alokasi`; acknowledgement umum seperti `sip`, `oke`, atau emoji tidak cukup.
- Personal allowance ditampilkan sebagai `Allowance Ayah Singgih` dan `Allowance Mami Farah`.

### Accessibility

- Interaksi berbasis teks Telegram secara inheren screen-reader compatible; tidak ada pekerjaan accessibility tambahan yang diperlukan untuk chat flow V1.

---

## 11. Failure and Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC-01 | User mengirim pesan income dua kali untuk periode yang sama | FARIA memperlakukan pesan kedua sebagai update draft yang sama, bukan allocation duplikat |
| EC-02 | User meminta perubahan padahal sudah ada Confirmed allocation untuk periode tersebut | FARIA menjelaskan bahwa periode sudah authoritative dan edit/replacement berada di luar scope V1 |
| EC-03 | Household MCP tidak tersedia saat konfirmasi | FARIA melaporkan kegagalan dan tidak mengklaim allocation telah persisted |
| EC-04 | Pesan dari identitas Telegram yang tidak allowlisted | FARIA tidak memproses request tersebut |

---

## 12. Security and Privacy

### Threat-Sensitive Behavior

- Disclosure data finansial, konfirmasi allocation yang tidak sah.

### Security Requirements

- Allowlist Telegram ditegakkan sebelum memproses pesan.
- Household MCP tool calls dibatasi hanya pada operasi allocation (tidak ada raw SQL/shell yang diekspos ke LLM).

### Privacy Requirements

- Data income/allocation household tidak dibagikan di luar Telegram private group dan dashboard; tidak ada analytics pihak ketiga terhadap konten finansial.

---

## 13. Observability

### Logs
- Allocation draft dibuat, allocation dikonfirmasi, konfirmasi ditolak/gagal.

### Metrics
- Jumlah `allocation_confirmed` per periode.

### Business Events
- `allocation_confirmed` (lihat PRD Analytics).

---

## 14. Test Scenarios

| Test ID | Requirement | Level | Scenario |
|---|---|---|---|
| T-001 | `FR-ALLOC-002` | Unit | Draft allocation dihasilkan dengan benar dari rules yang dikonfigurasi |
| T-002 | `FR-ALLOC-004` | Integration | Draft yang tersimpan tetap non-authoritative sampai tool confirm dipanggil |
| T-003 | `FR-ALLOC-004` | Operational acceptance | Pengirim non-allowlisted tidak dapat mengonfirmasi allocation (pending actual non-allowlisted identity test) |
| T-004 | `FR-ALLOC-001`, `FR-ALLOC-002` | Conversational acceptance | Income tanpa nilai alokasi memicu satu grouped clarification dan tidak membuat draft |
| T-005 | `FR-ALLOC-004` | Conversational acceptance | Acknowledgement ambigu mempertahankan DRAFT; hanya konfirmasi eksplisit menghasilkan CONFIRMED |

### Minimum Regression Coverage

- Confirmation boundary (`FR-ALLOC-004`) harus selalu tercover, karena ini adalah garansi human-authority inti FARIA.

---

## 15. Rollout and Migration

### Rollout Strategy

Direct (implementasi pertama dari slice ini; belum ada existing user untuk dimigrasikan).

### Data Migration

Tidak ada — ini adalah schema pertama untuk feature ini.

### Backward Compatibility

Belum applicable.

### Rollback / Recovery

Koreksi schema yang sudah diterapkan dilakukan lewat forward version-controlled migration. Sebelum production use, backup/restore SQLite harus tersedia sesuai keputusan operations yang masih terbuka.

---

## 16. Dependencies

### Upstream
- Implementasi Household MCP server.
- Integrasi bot Telegram.
- Repo-owned Hermes Finance skill dan konfigurasi external skill directory.

### Downstream
- Savings & Goals (`CAP-SAVE-001`), Zakat & Sedekah (`CAP-GIVE-001`) dibangun di atas allocation record yang sama setelah persisted.

---

## 17. Open Questions

| ID | Question | Owner | Blocking? |
|---|---|---|---|
| Q-01 | Resolved in RF-04: household memilih THP × 2.5% | Household | No |
| Q-02 | Resolved in RF-04: sedekah manual setiap bulan | Household | No |
| Q-03 | Contract tool Household MCP yang tepat (parameter/response shape) | Resolved in RF-02; see Section 9 | No |

---

## 18. Definition of Done

- [ ] FR-ALLOC-001 sampai FR-ALLOC-004 diimplementasikan (P0).
- [ ] Acceptance Criteria pass.
- [ ] Household MCP tool contract terdokumentasi sebelum/bersamaan dengan implementasi.
- [ ] Authorization (Telegram allowlist) ditegakkan.
- [ ] Required UI/chat states diimplementasikan.
- [ ] Relevant automated tests pass.
- [ ] Confirmation boundary (FR-ALLOC-004) tercover oleh tests.
- [ ] Security/privacy implications ditangani.
- [ ] Dashboard merefleksikan confirmed state (FR-ALLOC-005) atau secara eksplisit dideferred.
- [ ] Affected authoritative docs current.
- [ ] Known limitations eksplisit (misalnya belum ada edit-after-confirm di V1).

---

## 19. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.5 | `2026-09-12` | Added RF-04 household rules, goal-based savings allocation, explicit unallocated remainder, and PLAN-versus-ACTUAL boundaries | sipratama |
| 0.4 | `2026-09-12` | Added household display labels for the two personal allowance line items | sipratama |
| 0.3 | `2026-09-12` | Added RF-03 conversation, correction, remainder, explicit-confirmation, and confirmed-period behavior | sipratama |
| 0.2 | `2026-09-12` | Recorded the RF-02 MCP tool surface and clarified draft persistence, period, identity, and confirmation boundaries | sipratama |
| 0.1 | `2026-09-11` | Initial draft | sipratama |
