# Annotasi Template

> 🇮🇩 Bahasa Indonesia · [🇬🇧 English](./README.en.md)

Template pengembangan software yang **AI-ready, opinionated, dan production-oriented** untuk product development fullstack, backend, maupun frontend.

Annotasi Template membantu manusia dan AI coding agent seperti **Codex** dan **Claude Code** bekerja dari source of truth yang sama—mulai dari product discovery, product intent, feature behavior, architecture, contract, engineering standards, sampai release evidence.

> Tujuannya bukan membuat dokumentasi sebanyak mungkin. Tujuannya adalah menjaga **shared understanding dengan duplikasi seminimal mungkin**.

---

## Apa yang diselesaikan template ini?

AI-assisted development bisa mempercepat coding, tetapi mudah menimbulkan masalah ketika:

- requirement hanya hidup di chat;
- AI mulai membentuk repository sebelum memahami product;
- architecture berubah tanpa keputusan eksplisit;
- API contract tertinggal dari implementation;
- AI membaca terlalu banyak context yang tidak relevan;
- business rule tersebar di frontend, backend, dan test;
- project punya banyak dokumen tetapi tidak jelas mana yang authoritative.

Annotasi Template menggunakan alur:

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

Prinsip initialization-nya sederhana:

> **Pahami product terlebih dahulu. Bentuk repository setelah konteksnya cukup.**

---

## Prinsip utama

### One Concern, One Source of Truth

Satu concern harus mempunyai satu authoritative source.

| Pertanyaan | Source of Truth |
|---|---|
| Bagaimana project baru ditemukan dan diinisialisasi? | `docs/PROJECT_INITIALIZATION.md` |
| Kenapa product dibuat dan untuk siapa? | `docs/00_product/PRODUCT_BRIEF.md` |
| Capability apa yang harus tersedia? | `docs/00_product/PRD.md` |
| Bagaimana satu feature harus berperilaku? | `docs/01_features/<feature>.md` |
| Bagaimana sistem disusun? | `docs/02_architecture/SYSTEM_ARCHITECTURE.md` |
| Kenapa keputusan architecture dibuat? | `docs/02_architecture/adr/` |
| Seberapa baik sistem harus bekerja? | `docs/02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md` |
| Apa persistent data model-nya? | migrations/schema + `DATA_MODEL.md` |
| Apa REST/event contract-nya? | `contracts/` bila digunakan |
| Bagaimana engineering dilakukan? | `docs/standards/` |
| Bagaimana testing direncanakan? | `docs/04_engineering/TEST_STRATEGY.md` |
| Bagaimana system dirilis/dioperasikan? | `docs/05_operations/` + `docs/06_delivery/` |

### Discovery sebelum initialization

Untuk project baru, AI tidak boleh langsung membuat architecture, memilih stack, atau menghapus dokumentasi hanya berdasarkan nama repository.

Initialization terdiri dari:

```text
PHASE A — Project Discovery
(read-only)
        ↓
Minimum Product Context Gate
        ↓
PHASE B — Project Initialization
(repository mutation)
```

Jika konteks product belum cukup, AI harus bertanya hanya tentang informasi yang masih hilang.

### AI membaca secara selektif

Jangan meminta AI membaca seluruh repository untuk setiap task.

Untuk project yang sudah diinisialisasi, default flow:

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

### Contract sebelum implementation drift

Perubahan terhadap API, event, schema, atau persistent format harus memperbarui contract/migration sebelum atau bersamaan dengan implementation.

### Architecture decision harus eksplisit

Material architecture change tidak boleh hanya muncul di code atau chat. Gunakan ADR.

---

## Quick Start

### 1. Buat repository dari template

Klik:

```text
Use this template
→ Create a new repository
```

pada repository Annotasi Template.

Alternatif: clone/copy repository secara manual.

Repository baru akan membawa documentation framework, AI instructions, engineering standards, initialization workflow, dan validator.

**Jangan langsung mengisi seluruh template atau membuat source structure secara manual.**

---

### 2. Buka repository baru dengan Codex atau Claude Code

AI akan membaca:

```text
AGENTS.md
        ↓
docs/PROJECT_INITIALIZATION.md
```

`AGENTS.md` adalah repository-wide instruction source.

`PROJECT_INITIALIZATION.md` mengatur discovery-first initialization.

---

### 3. Mulai Project Discovery

Gunakan prompt berikut:

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

Anda **tidak perlu menentukan profile, database, framework, atau deployment target dari awal**.

Jika context yang tersedia baru:

```text
Project: Penatika
```

AI seharusnya **tidak mengubah repository**.

AI harus langsung masuk Discovery Mode dan segera bertanya tentang product
yang masih belum jelas, bukan hanya mengakui instruction.

---

### 4. Berikan context yang sudah Anda ketahui

Opsional, tetapi semakin jelas context awal, semakin sedikit pertanyaan discovery yang diperlukan.

Contoh:

```text
Project:
<NAMA_PROJECT>

What I already know:
- masalah yang ingin diselesaikan;
- pengguna utama;
- outcome yang diharapkan;
- gambaran versi pertama;
- constraint yang sudah pasti.
```

Tidak perlu memaksakan jawaban teknis yang memang belum diputuskan.

---

### 5. Minimum Product Context Gate

Sebelum repository boleh diinisialisasi, AI minimal harus memahami:

```text
✓ Project name
✓ Core problem
✓ Primary user
✓ Desired user outcome
✓ Initial scope / MVP hypothesis
✓ Important known constraints
```

Constraint boleh:

```text
None known yet
```

jika memang belum ada.

Hal berikut boleh tetap undecided:

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

### 6. AI merekomendasikan project shape

Setelah context gate `PASS`, AI menentukan atau merekomendasikan:

```text
Base Profile
Modifiers
Active Documentation
Conditional Documentation
Known Technology Decisions
Open Technology Decisions
```

Contoh:

```text
Recommended Base Profile:
fullstack

Recommended Modifiers:
saas

Reason:
- product membutuhkan user-facing UI;
- authoritative backend behavior;
- persistent user data;
- authentication dan tenant isolation.
```

Profile adalah **hasil dari product discovery**, bukan sesuatu yang harus diketahui user sebelum mulai.

---

### 7. Repository baru diinisialisasi

Urutan initialization:

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

README project dibuat **terakhir**, sehingga README menggambarkan project yang benar-benar sudah dipahami dan bukan sekadar daftar `TBD`.

---

### 8. Validasi initialization

Jalankan:

```bash
python3 scripts/validate_template.py --project-mode
```

atau pada environment tertentu:

```bash
python scripts/validate_template.py --project-mode
```

Validator memeriksa structural health seperti local Markdown links dan unresolved bootstrap metadata.

Validator **bukan** pengganti product, architecture, atau engineering review.

---

### 9. Review baseline sebelum coding

Sebelum implementation dimulai, review minimal:

```text
PRODUCT_BRIEF.md
        ↓
Apakah problem, user, dan outcome benar?

PRD.md
        ↓
Apakah capability dan scope benar?

FEATURE SPECS
        ↓
Apakah behavior awal sudah sesuai?

SYSTEM_ARCHITECTURE.md
        ↓
Apakah technical boundaries mengikuti kebutuhan product?
```

Setelah baseline tersebut masuk akal, commit initialization sebagai checkpoint project.

Contoh:

```bash
git add .
git commit -m "chore: initialize project from Annotasi Template"
```

---

### 10. Mulai feature development

Untuk feature baru:

1. gunakan/copy `docs/01_features/FEATURE_TEMPLATE.md`;
2. beri nama berdasarkan domain/feature;
3. definisikan stable requirement IDs seperti `FR-PAYMENT-001`;
4. implementasikan dengan context routing dari `AGENTS.md`.

Contoh task:

```text
Implement FR-PAYMENT-001 from
docs/01_features/payment.md.

Follow AGENTS.md and load only the relevant architecture,
contracts, standards, source code, and tests.
```

---

## Struktur repository template

Struktur yang **benar-benar disediakan oleh template**:

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

Folder seperti `src/`, `backend/`, `frontend/`, `contracts/openapi/`, `contracts/asyncapi/`, migrations, atau deployment manifests **dibuat sesuai kebutuhan project setelah product dan architecture cukup dipahami**, bukan dipaksakan oleh template.

---

## Dokumen wajib vs kondisional

Tidak semua project harus mengisi semua dokumen.

### Core — hampir selalu aktif

| Dokumen | Status |
|---|---|
| `README.md` | Wajib setelah project diinisialisasi |
| `AGENTS.md` | Wajib untuk AI-assisted project |
| `PRODUCT_BRIEF.md` | Wajib |
| `PRD.md` | Wajib untuk product dengan behavior non-trivial |
| `SYSTEM_ARCHITECTURE.md` | Wajib untuk software non-trivial |
| `FEATURE_TEMPLATE.md` | Dipertahankan sebagai template |
| `ADR_TEMPLATE.md` | Dipertahankan sebagai template |
| `docs/standards/` | Dipertahankan; dibaca selektif |

### Conditional

| Dokumen | Aktif ketika |
|---|---|
| `ROADMAP.md` | product memiliki lebih dari satu milestone/direction |
| `DATA_MODEL.md` | project memiliki persistent/domain data |
| `NON_FUNCTIONAL_REQUIREMENTS.md` | quality targets perlu eksplisit |
| `UX_FLOWS.md` | ada user journey lintas screen/feature |
| `DESIGN_SYSTEM.md` | ada user-facing UI |
| `TEST_STRATEGY.md` | testing melibatkan lebih dari unit test sederhana |
| `THREAT_MODEL.md` | ada auth, user data, network boundary, payment, upload, admin, dll. |
| `DEVELOPER_SETUP.md` | project perlu onboarding developer |
| `CONFIGURATION.md` | runtime configuration non-trivial |
| `DEPLOYMENT.md` | project dideploy |
| `RUNBOOK.md` | project dioperasikan/di-support |
| `RISKS.md` | ada material risk yang perlu ownership |
| `RELEASE_CHECKLIST.md` | ada controlled production release |
| `KNOWN_LIMITATIONS.md` | ada limitation yang perlu diketahui contributor/user |

Engineering standards tetap disimpan, walaupun tidak semuanya aktif untuk setiap task. `AGENTS.md` hanya merutekan AI ke standard yang relevan.

Conditional documentation **tidak boleh dihapus hanya karena profile belum diketahui**.

---

## Project Profiles

Project profile membantu menentukan dokumentasi dan engineering concern yang relevan.

**User tidak wajib memilih profile sebelum discovery.** Secara default, AI merekomendasikan profile setelah Minimum Product Context Gate terpenuhi.

### Fullstack

Untuk product yang membutuhkan user-facing frontend dan authoritative backend behavior.

Umumnya mengaktifkan:

- product docs;
- feature specs;
- architecture/data/NFR;
- UX/design;
- test strategy/threat model;
- operations saat menuju production.

### Backend Service

Untuk API/service/background system tanpa primary user-facing frontend.

Design docs biasanya dapat dinonaktifkan. Backend, API/integration, persistence, security, testing, dan reliability menjadi prioritas.

### Frontend App

Untuk application yang mayoritas client/frontend dan menggunakan existing backend/service.

Backend/persistence project docs dapat dikurangi. Design, UX, API contract consumption, accessibility, testing, dan security tetap relevan.

### Prototype

Untuk eksplorasi cepat dengan baseline minimum:

```text
PRODUCT_BRIEF
PRD
FEATURE SPECS
SYSTEM_ARCHITECTURE
AGENTS
```

Tambahkan dokumen lain hanya ketika risk/complexity membutuhkannya.

Prototype tetap mengikuti discovery-first initialization.

### Modifiers

Setelah product context diketahui, profile dapat ditambah modifier:

- `saas`
- `event-driven`
- `ai-enabled`
- `open-source`
- `regulated`

Detail rekomendasi dan activation matrix berada di `docs/PROJECT_INITIALIZATION.md`.

---

## Codex dan Claude

### Codex

`AGENTS.md` adalah canonical repository-wide instruction source.

### Claude Code

`CLAUDE.md` sengaja sangat tipis dan mengimpor:

```text
@AGENTS.md
```

Jadi Claude dan Codex tidak memiliki dua rule set berbeda.

Detailed AI behavior berada di:

```text
docs/standards/14_AI_ASSISTED_DEVELOPMENT.md
```

---

## Kebijakan bahasa

Annotasi Template menggunakan:

### Bahasa Indonesia / hybrid

Untuk human-facing product thinking:

- `README.md`
- `PROJECT_INITIALIZATION.md`
- `PRODUCT_BRIEF.md`
- `PRD.md`
- `ROADMAP.md`
- `FEATURE_TEMPLATE.md`
- `UX_FLOWS.md`
- `DESIGN_SYSTEM.md`

Technical vocabulary seperti `Acceptance Criteria`, `Non-Goals`, `ADR`, `idempotency`, `rollback`, atau `Given/When/Then` boleh tetap English bila lebih natural.

### English

Untuk engineering dan machine-oriented artifacts:

- `AGENTS.md`
- `CLAUDE.md`
- architecture docs;
- ADR;
- engineering/test/security/operations docs;
- `docs/standards/`;
- source code;
- database/schema naming;
- OpenAPI/AsyncAPI/contracts.

Hanya README yang dimirror bilingual (`README.md` + `README.en.md`). Specification lain mempunyai **satu canonical language** agar tidak terjadi drift.

---

## Requirement IDs

Feature behavior menggunakan stable IDs:

```text
FR-<FEATURE>-<NUMBER>
```

Contoh:

```text
FR-AUTH-001
FR-CHECKOUT-004
FR-PAYMENT-012
```

Rules:

- ID tidak berubah hanya karena refactor;
- ID yang retired tidak digunakan ulang;
- test, contract, issue, dan ADR boleh mereferensikan ID;
- jangan membuat ID untuk implementation detail trivial.

---

## Versioning

Versi Annotasi Template direkomendasikan menggunakan:

- Git Tags;
- GitHub Releases.

Nama repository atau folder tidak perlu membawa nomor versi.

---

## Validasi

Untuk repository Annotasi Template:

```bash
python3 scripts/validate_template.py
```

Pada project yang sudah diinisialisasi:

```bash
python3 scripts/validate_template.py --project-mode
```

Validator melakukan structural checks dasar dan local Markdown link validation. Ini bukan pengganti review isi dokumen.

Penjelasan lengkap tersedia di:

```text
scripts/README.md
```

---

## Filosofi template

Annotasi Template bukan framework yang mewajibkan semua project mempunyai puluhan dokumen aktif.

Gunakan prinsip berikut:

1. **Understand the product before shaping the solution.**
2. **Keep the source of truth clear.**
3. **Delete or ignore what does not help delivery.**
4. **Load only the context needed for the current task.**

AI mempercepat implementation; AI tidak memiliki product truth.
