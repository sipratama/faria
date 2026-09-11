# Product Brief — FARIA

> **Peran dokumen:** Authoritative source untuk **kenapa product ini ada, siapa yang dilayani, outcome apa yang dituju, dan constraint product/business apa yang membentuknya**.
>
> Detailed feature behavior berada di PRD dan Feature Specs. Technical design berada di architecture documentation.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Product | FARIA |
| Status | Draft |
| Version | `0.1` |
| Owner | Household (sipratama) |
| Last Updated | `2026-09-11` |
| Primary Market | Private — single household, not market-facing |

---

## 1. Product Vision

### Vision

FARIA becomes the household's operational assistant — reducing the mental load of managing money allocation, giving, savings goals, and recurring household responsibilities, so the household owner and spouse can run their household with less manual bookkeeping and fewer missed obligations.

### Product Statement

Untuk pasangan suami-istri yang mengelola keuangan dan rutinitas rumah tangga sendiri, FARIA adalah AI household operating system yang mengelola alokasi dan goals, bukan pencatatan transaksi. Berbeda dengan spreadsheet atau aplikasi budgeting manual yang mengharuskan pencatatan setiap pengeluaran, FARIA membiarkan household menyampaikan apa yang terjadi ("gaji sudah masuk", "zakat sudah dibayar") lewat percakapan Telegram privat, lalu FARIA yang menjaga alokasi, progress savings, dan obligation berulang.

---

## 2. Problem

### Core Problem

Household management melibatkan banyak tanggung jawab finansial dan operasional kecil namun berulang (alokasi income, zakat, sedekah, savings goals, household budget, personal allowance, reminder, maintenance) yang mudah terlewat, tetapi household tidak ingin mencatat setiap transaksi harian untuk mengelolanya.

### Why It Matters

Tanpa sistem yang ringan, alokasi bulanan diputuskan secara informal setiap bulan, obligation seperti zakat/sedekah atau reminder maintenance bisa terlewat, dan savings goals tidak punya progress yang terlihat — menimbulkan stres yang bisa dihindari tanpa menambah insight finansial yang berarti (karena pencatatan transaksi memang tidak diinginkan).

### Current Alternatives

- Mengingat/menyepakati alokasi secara verbal setiap bulan.
- Spreadsheet ad-hoc yang diupdate tidak konsisten.
- Tidak melakukan apa-apa sampai ada bill/obligation yang terlewat.

### Evidence

| Evidence | Source | Confidence |
|---|---|---|
| Household saat ini melakukan alokasi bulanan secara informal dan tidak mencatat pengeluaran kecil | Context yang diberikan saat initialization | High |

---

## 3. Target Users

### Primary User

**Who:** Household owner.

**Context:**
Pada awal bulan saat income masuk, dan kapan pun terjadi event finansial/household (zakat dibayar, savings contribution, maintenance selesai).

**Primary Job-to-be-Done**

> Ketika income bulanan masuk, saya ingin mengalokasikannya ke zakat, sedekah, savings, household budget, dan personal allowance tanpa mencatat setiap transaksi secara manual, sehingga obligation rumah tangga terpenuhi dan goals kami berjalan dengan predictable.

### Secondary Users

| User | Need | Why They Matter |
|---|---|---|
| Spouse | Job-to-be-done yang sama dengan household owner | Berinteraksi dengan household context yang sama lewat Telegram private group yang sama |

### Explicitly Not Targeted Yet

- Household lain (bukan produk multi-household).
- Pengguna umum/publik.
- Financial advisor / akuntan pihak ketiga.

---

## 4. Value Proposition

### Primary Value

Mengurangi mental load mengelola tanggung jawab finansial/operasional rumah tangga yang berulang.

### Differentiation

1. Mengalokasikan berdasarkan bucket/goal, bukan memaksa pencatatan transaksi.
2. Antarmuka percakapan (Telegram) alih-alih aplikasi budgeting berbasis form.
3. Manusia mengonfirmasi setiap perubahan finansial material — FARIA hanya mengusulkan, tidak pernah memutuskan diam-diam.

### Product Promise

> "Ceritakan apa yang terjadi ke FARIA; ia menjaga uang dan rutinitas rumah tangga tetap terorganisir tanpa memintamu mencatat setiap pengeluaran."

Promise ini menggambarkan outcome, bukan daftar feature.

---

## 5. Desired Outcomes

### User Outcomes

- Household tahu status alokasi bulanan tanpa perlu menghitung manual.
- Zakat dan sedekah tidak pernah terlewat diam-diam.
- Savings goals punya progress yang terlihat dan dapat dipercaya.
- Obligation rumah tangga berulang (maintenance, bills) mendapat reminder tepat waktu.

### Business / Product Outcomes

- FARIA menjadi tempat pertama yang digunakan household untuk tanggung jawab ini setiap bulan (dipakai rutin, bukan hanya dicoba lalu ditinggalkan).

---

## 6. Goals

### G-01 — Reliable Monthly Allocation

**Goal**
Setiap bulan, household dapat mencatat income dan mendapatkan draft alokasi yang benar untuk zakat, sedekah, savings, household budget, dan personal allowance, yang menjadi authoritative hanya setelah konfirmasi eksplisit.

**Evidence of Success**
Household menyelesaikan langkah konfirmasi setiap bulan tanpa perlu melewati FARIA (bypass).

### G-02 — Trustworthy Savings Progress

**Goal**
Savings goals merefleksikan current amount dan progress yang akurat setelah setiap contribution dicatat.

**Evidence of Success**
Household mengandalkan progress savings dari FARIA, bukan spreadsheet terpisah.

---

## 7. Non-Goals

Hal berikut secara eksplisit berada di luar arah product/fase saat ini:

- Pencatatan pengeluaran transaction-by-transaction.
- Produk SaaS publik / multi-household.
- Integrasi bank otomatis, transfer uang otomatis, atau pembayaran bill otomatis.
- Independent multi-agent architecture (persona adalah skill logis di bawah satu Hermes runtime pada V1).
- Visualisasi dashboard 2D/3D.
- Mobile application.

Non-Goals mencegah contributor dan AI memperluas scope secara accidental.

---

## 8. Product Principles

### P-01 — Manage allocations and goals, not transactions

Household financial state dinyatakan sebagai bucket/goal, bukan pencatatan pengeluaran per item.

### P-02 — Propose, then confirm

FARIA tidak boleh menyimpan perubahan financial state material sebagai authoritative tanpa konfirmasi manusia eksplisit.

### P-03 — Household scope only

FARIA menolak dengan sopan permintaan di luar household finance/operations, ditegakkan lebih dari sekadar system prompt (domain instructions, tool allowlist, intent validation).

### P-04 — SQLite is the source of truth, never LLM memory

Angka finansial household selalu authoritative dari SQLite, bukan dari memory LLM/Hermes.

---

## 9. MVP Boundary

### In Scope

MVP harus membuktikan:

- Monthly allocation vertical slice: Telegram → draft → confirmation → Household MCP persistence → dashboard reflection.
- Savings goals dan contributions.
- Zakat penghasilan dan sedekah sebagai recurring allocation terpisah (rule dikonfigurasi household, tidak di-hardcode).
- Household operating budget dan personal allowance sebagai alokasi bulanan tanpa visibility transaksi.
- Household routines/reminders sederhana.
- Dashboard sebagai Agent Control Center yang menampilkan status persona.

### Out of Scope

MVP tidak mencakup:

- Pencatatan pengeluaran transaction-level.
- Integrasi bank/payment otomatis.
- Multi-household support.
- Visualisasi dashboard 2D/3D.

### MVP Exit Condition

MVP dianggap cukup tervalidasi ketika household telah menyelesaikan minimal satu siklus alokasi bulanan penuh (income → draft → confirm → persisted → dashboard reflects it) end-to-end lewat Telegram.

Detailed capability scope tetap berada di PRD.

---

## 10. Business Model

### Monetization

N/A — private household system, tidak dimonetisasi.

### Payer

N/A.

### Pricing Assumption

N/A.

### Cost Drivers

- Biaya inference LLM lewat OpenRouter/9Router.
- Hosting (VPS atau XCodePod.Cloud).
- Storage backup terenkripsi.

---

## 11. Success Metrics

### Primary Metric

| Metric | Definition | Target / Direction |
|---|---|---|
| Monthly allocation completion rate | Household menyelesaikan siklus propose→confirm setiap bulan kalender FARIA digunakan | Digunakan di setiap bulan aktif (kualitatif — skala satu household, bukan target numerik keras) |

### Supporting Metrics

| Metric | Why It Matters |
|---|---|
| Jumlah savings goals yang aktif dilacak | Menunjukkan adopsi fitur savings |
| Household routines/reminders yang diacknowledge tepat waktu | Menunjukkan nilai reminder |

### Guardrail Metrics

| Metric | Guardrail |
|---|---|
| Alokasi yang belum dikonfirmasi | Tidak pernah diperlakukan sebagai authoritative |
| Pesan Telegram dari luar allowlist | Tidak pernah diproses |

---

## 12. Constraints

### Product Constraints
- Hanya digunakan oleh household (2 pengguna).
- Bahasa Indonesia adalah bahasa percakapan utama.

### Business Constraints
- Tidak ada — proyek personal yang didanai sendiri.

### Legal / Compliance Constraints
- N/A — sistem privat, tidak ada klaim regulasi/compliance.

### Technical Constraints

- Telegram private group sebagai antarmuka utama.
- SQLite sebagai authoritative store.
- Hermes + 9Router + OpenRouter sebagai arah teknis V1 yang sudah fixed (lihat System Architecture).

---

## 13. Dependencies

| Dependency | Why Needed | Risk |
|---|---|---|
| Telegram Bot API | Antarmuka percakapan utama | Low |
| OpenRouter via 9Router | Inference LLM untuk Hermes | Medium — perubahan model/provider |
| Always-on host (provider belum final) | Operasi berkelanjutan | Medium — keputusan hosting masih terbuka |

---

## 14. Assumptions

| ID | Assumption | Validation Method | Status |
|---|---|---|---|
| A-01 | Kedua anggota household akan konsisten menggunakan Telegram private group yang sama sebagai antarmuka utama | Observasi pemakaian bulanan aktual | Open |
| A-02 | Household nyaman dengan tracking level-alokasi dan tidak akan menuntut pencatatan transaksi di kemudian hari | Revisit setelah 1-2 bulan pemakaian | Open |

---

## 15. Open Product Questions

| ID | Question | Owner | Target Decision |
|---|---|---|---|
| Q-01 | Apa formula/aturan alokasi Zakat Penghasilan yang tepat? | Household | Sebelum alokasi zakat pertama dikonfirmasi |
| Q-02 | Apa aturan/nominal Sedekah bulanan yang berulang? | Household | Sebelum alokasi sedekah pertama dikonfirmasi |
| Q-03 | Hosting provider final: XCodePod.Cloud atau paid VPS? | Household | Sebelum deployment |
| Q-04 | Destinasi encrypted backup eksternal? | Household | Sebelum production use |
| Q-05 | Identitas/allowlist Telegram (dua akun mana)? | Household | Sebelum integrasi Telegram |

Saat resolved, pindahkan keputusan ke authoritative document yang sesuai.

---

## 16. Related Documents

- Product Requirements: `./PRD.md`
- Feature Specifications: `../01_features/`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`

---

## 17. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `2026-09-11` | Initial draft | sipratama |
