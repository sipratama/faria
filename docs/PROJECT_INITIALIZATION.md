# Project Initialization — Annotasi Template

> **Peran dokumen:** Guided workflow untuk mengubah repository Annotasi Template menjadi project nyata dengan prinsip **product discovery first, repository initialization second**.
>
> Dokumen ini dibaca saat project baru dibuat dari Annotasi Template atau ketika user meminta repository diinisialisasi. Setelah initialization selesai, AI tidak perlu membacanya untuk feature development biasa kecuali diminta.

---

## 1. Core Principle

Project initialization **MUST NOT begin from repository structure, technology stack, or architecture**.

Urutan yang benar adalah:

```text
UNDERSTAND THE PRODUCT
        ↓
ESTABLISH MINIMUM PRODUCT CONTEXT
        ↓
RECOMMEND PROJECT SHAPE
        ↓
INITIALIZE DOCUMENTATION
        ↓
ESTABLISH ARCHITECTURE
        ↓
CREATE ONLY REQUIRED STRUCTURE
        ↓
VALIDATE
```

AI harus memahami masalah dan intended product outcome sebelum membentuk repository.

> **Understand the problem first, then shape the solution.**

---

## 2. Initialization Has Two Phases

Initialization terdiri dari dua fase yang berbeda.

```text
PHASE A
PROJECT DISCOVERY
(read-only)
        ↓
Minimum Product Context Gate
        ↓
PHASE B
PROJECT INITIALIZATION
(repository mutation)
```

### Phase A — Project Discovery

Tujuan:

- memahami product;
- menemukan missing context;
- membedakan fakta, assumption, dan open question;
- menentukan apakah konteks sudah cukup untuk initialization.

Selama fase ini AI **MUST NOT modify repository files**.

### Phase B — Project Initialization

Fase ini hanya boleh dimulai setelah **Minimum Product Context Gate** terpenuhi.

Tujuan:

- memilih/rekomendasikan project profile;
- initialize Product Brief;
- initialize PRD;
- membuat feature specs yang sudah cukup dipahami;
- establish initial architecture;
- activate conditional documentation;
- membuat contracts/source structure hanya jika relevan;
- generate project README;
- validate hasil initialization.

---

## 3. Kapan Workflow Ini Aktif?

Gunakan workflow ini ketika:

- repository baru dibuat dari Annotasi Template;
- active project docs masih berisi bootstrap placeholders seperti `<PROJECT_NAME>`;
- user meminta `initialize`, `start project`, `adapt template`, `bootstrap project`, atau setara.

Jangan menjalankan seluruh initialization untuk:

- feature implementation biasa;
- defect fix;
- refactor;
- routine architecture change pada project yang sudah initialized.

---

# PHASE A — PROJECT DISCOVERY

## 4. Inspect Before Asking

Sebelum bertanya kepada user, AI harus membaca:

```text
AGENTS.md
README.md
docs/PROJECT_INITIALIZATION.md
```

Lalu inspect hanya evidence yang relevan dari repository:

- existing source code;
- build/package files;
- existing project documentation;
- Git remote/repository name;
- current repository structure;
- user-provided context dalam request/conversation.

### Important Rule

Repository name boleh digunakan sebagai **project name candidate**, tetapi:

> **Repository name MUST NOT be treated as evidence of product purpose.**

Contoh:

```text
Repository: penatika
```

AI boleh menyimpulkan:

```text
Candidate project name: Penatika
```

tetapi tidak boleh menyimpulkan product purpose tanpa evidence.

---

## 5. Minimum Product Context Gate

Sebelum repository boleh dimodifikasi, AI harus memahami minimal:

| Context | Required | Meaning |
|---|---:|---|
| Project name | Yes | Nama project/product candidate |
| Core problem | Yes | Masalah utama yang ingin diselesaikan |
| Primary user | Yes | Siapa pengguna utama |
| Desired user outcome | Yes | Hasil yang ingin didapat user |
| Initial scope / MVP hypothesis | Yes | Kemampuan awal atau boundary versi pertama |
| Important known constraints | Yes | Constraint penting, atau eksplisit `None known yet` |

### Tidak Wajib Sebelum Gate

Hal berikut **tidak wajib diketahui** untuk memulai initialization:

- programming language;
- framework;
- database;
- cloud provider;
- deployment target;
- monolith vs microservices;
- event broker;
- base profile;
- modifiers.

Hal tersebut boleh tetap undecided sampai product context cukup untuk menilainya.

---

## 6. Context Sufficiency Rule

AI harus mengevaluasi context yang sudah tersedia.

### Gate = PASS

Gate dianggap terpenuhi jika AI dapat menjawab dengan cukup jelas:

```text
What problem?
For whom?
What outcome?
What initial boundary?
What known constraints?
```

Jawaban tidak harus final atau sangat detail.

### Gate = FAIL

Gate gagal jika jawaban masih terlalu kosong atau ambigu sehingga project shape tidak dapat ditentukan secara masuk akal.

Contoh:

```text
Project: Penatika
```

atau:

```text
Aplikasi untuk membantu orang.
```

belum cukup.

---

## 7. No-Context → No-Mutation Rule

Jika Minimum Product Context Gate belum terpenuhi, AI **MUST NOT**:

- rewrite `README.md`;
- initialize atau rewrite Product Brief;
- initialize atau rewrite PRD;
- create feature specifications;
- initialize System Architecture;
- choose technology stack silently;
- mark a project profile as final;
- create contracts;
- create source directories;
- remove conditional documentation;
- delete template files;
- create migrations;
- create deployment/infrastructure structure.

AI harus tetap berada di **Discovery Mode**.

---

## 8. Adaptive Discovery Questions

Jika context belum cukup, AI harus bertanya hanya tentang informasi yang masih hilang.

### Default Question Areas

Gunakan maksimal sekitar **3–7 pertanyaan dalam satu putaran**, sesuai kebutuhan.

Pertanyaan dasar:

1. **Masalah apa yang ingin product ini selesaikan?**
2. **Siapa pengguna utamanya?**
3. **Setelah menggunakan product ini, hasil utama apa yang seharusnya mereka dapatkan?**
4. **Untuk versi pertama, kemampuan apa saja yang paling penting?**
5. **Apa yang secara eksplisit belum ingin dibangun di versi awal?**
6. **Apakah ada constraint yang sudah pasti?**
7. **Apakah ada keputusan teknologi yang memang sudah fixed?** Jika belum, tidak masalah.

### Question Rules

AI MUST:

- menggunakan context yang sudah diberikan;
- **tidak menanyakan ulang informasi yang sudah diketahui**;
- bertanya tentang problem/product sebelum teknologi;
- menghindari questionnaire panjang;
- menggunakan follow-up hanya jika jawaban masih terlalu abstrak;
- membedakan unknown product decision dari implementation detail.

### Example

Jika user sudah mengatakan:

```text
Saya ingin membuat aplikasi web untuk mahasiswa yang membantu
mengorganisir catatan kuliah.
```

AI tidak boleh bertanya lagi:

```text
Siapa target user?
Apakah ini web?
```

AI boleh bertanya:

```text
Apa outcome utama yang paling penting:
menemukan catatan dengan cepat, memahami materi,
membuat rangkuman, atau kolaborasi?
```

---

## 9. Progressive Discovery

Satu putaran pertanyaan mungkin belum cukup.

Jika jawaban user masih terlalu luas, AI MAY melakukan follow-up yang lebih sempit.

Contoh:

User:

```text
Untuk membantu mahasiswa belajar lebih baik.
```

AI dapat memperjelas:

```text
"Belajar lebih baik" masih luas.
Outcome mana yang paling dekat untuk versi pertama:
- mengorganisir catatan,
- memahami materi,
- latihan soal,
- mengatur jadwal,
- kolaborasi,
- membangun project,
atau sesuatu yang lain?
```

Tujuannya bukan memaksa user memilih dari opsi, tetapi membantu memperjelas intended outcome.

---

## 10. Discovery Must Not Become Technology Interview

Pada Discovery Mode, AI SHOULD NOT langsung bertanya:

```text
PostgreSQL atau MongoDB?
Kafka atau RabbitMQ?
Kubernetes?
Microservices?
AWS atau GCP?
```

kecuali user sudah membawa constraint teknis tersebut.

Technology choice harus mengikuti kebutuhan product, bukan mendahuluinya.

---

## 11. Discovery Summary

Setelah context cukup, tetapi **sebelum repository dimodifikasi**, AI harus menyusun summary:

```text
Project:
<NAME>

Problem:
<CORE PROBLEM>

Primary User:
<PRIMARY USER>

Desired Outcome:
<OUTCOME>

Initial Scope:
- ...
- ...

Non-Goals:
- ...
- ...

Known Constraints:
- ...

Known Product Assumptions:
- ...

Remaining Open Questions:
- ...
```

Summary harus:

- hanya menggunakan informasi yang didukung oleh user/repository evidence;
- membedakan confirmed fact dan assumption;
- tidak mengarang metric/evidence;
- tidak memaksakan architecture.

---

## 12. Product Context Gate Decision

Setelah Discovery Summary, AI menyatakan:

```text
Minimum Product Context Gate: PASS
```

atau:

```text
Minimum Product Context Gate: FAIL
```

Jika `FAIL`, lanjutkan discovery.

Jika `PASS`, baru Phase B boleh dimulai.

AI tidak perlu meminta confirmation tambahan jika context sudah jelas dan user memang meminta initialization.

Namun unresolved **material product decisions** harus dicatat sebagai Open Question, bukan ditebak.

---

# PHASE B — PROJECT INITIALIZATION

## 13. Recommend Project Shape

Setelah Product Context Gate `PASS`, AI menentukan atau merekomendasikan project shape.

Catat:

```text
Recommended Base Profile:
Modifiers:
Known Technology Decisions:
Still-Open Technology Decisions:
Deployment Maturity:
Reasoning:
```

### Important Rule

Base profile adalah **hasil dari product context**, bukan input wajib.

Jika user sudah menentukan profile, AI boleh menggunakannya selama tidak bertentangan dengan product evidence.

Jika belum, AI harus merekomendasikannya.

---

## 14. Base Profiles

Pilih satu base profile.

### `fullstack`

Untuk product yang membutuhkan:

- user-facing frontend;
- authoritative backend behavior;
- API/application layer;
- biasanya persistence/integration.

Typical docs:

- Product Brief;
- PRD;
- Feature Specs;
- System Architecture;
- Data Model bila persistent;
- NFR;
- UX Flows;
- Design System;
- Test Strategy;
- Threat Model bila ada meaningful trust boundary;
- Developer Setup;
- Configuration.

Deployment/Runbook/Release docs aktif sesuai maturity.

### `backend-service`

Untuk service/API/background system tanpa primary user-facing frontend.

Typical docs:

- Product Brief;
- PRD bila mempunyai meaningful business capability;
- Feature Specs;
- System Architecture;
- Data Model bila persistent;
- NFR;
- Test Strategy;
- Threat Model bila network/sensitive;
- Developer Setup;
- Configuration;
- operations/delivery sesuai maturity.

UX/Design biasanya inactive.

### `frontend-app`

Untuk application yang mayoritas frontend/client dan mengonsumsi existing backend/service.

Typical docs:

- Product Brief;
- PRD;
- Feature Specs;
- System Architecture;
- UX Flows;
- Design System;
- NFR untuk performance/accessibility;
- Test Strategy;
- Threat Model bila auth/session/sensitive data relevan;
- Developer Setup;
- Configuration.

Data Model hanya jika meaningful local persistence ada.

### `prototype`

Untuk eksplorasi cepat dengan minimum documentation.

Minimum:

```text
PRODUCT_BRIEF.md
PRD.md
FEATURE_TEMPLATE.md + feature specs
SYSTEM_ARCHITECTURE.md
AGENTS.md
```

Tambahkan docs lain hanya saat risk/complexity membutuhkannya.

Prototype tetap tidak boleh:

- commit secrets;
- invent requirements;
- silently break contracts;
- perform destructive data change without deliberation.

---

## 15. Optional Modifiers

Modifiers dapat dikombinasikan dengan base profile.

### `saas`

Pertimbangkan:
- tenancy;
- identity/authorization;
- billing jika ada;
- data isolation;
- configuration;
- deployment/operations;
- security/retention.

### `event-driven`

Pertimbangkan:
- AsyncAPI/schema bila event menjadi contract;
- ownership;
- idempotency;
- retry;
- ordering;
- DLQ;
- observability.

### `ai-enabled`

Pertimbangkan:
- model/provider;
- prompt/versioning bila material;
- evaluation;
- cost;
- privacy;
- untrusted model output;
- fallback/degradation.

### `open-source`

Pertimbangkan:
- `CONTRIBUTING.md`;
- license;
- public setup;
- compatibility;
- release/changelog policy.

### `regulated`

Perkuat:
- traceability;
- security;
- audit;
- retention;
- compliance evidence;
- release approval.

Jangan mengklaim compliance hanya karena template menyediakan control.

---

## 16. Activation Matrix

Legenda:

- **R** — Required/default
- **C** — Conditional
- **—** — Usually inactive

| Document | Fullstack | Backend | Frontend | Prototype |
|---|:---:|:---:|:---:|:---:|
| Product Brief | R | R | R | R |
| PRD | R | C/R | R | R |
| Roadmap | C | C | C | — |
| Feature Specs | R | R | R | R |
| System Architecture | R | R | R | R |
| Data Model | R/C | R/C | C | — |
| NFR | R/C | R/C | R/C | C |
| UX Flows | R | — | R | C |
| Design System | R | — | R | C |
| Test Strategy | R | R | R | C |
| Threat Model | R/C | R/C | C | C |
| Developer Setup | R | R | R | C |
| Configuration | R/C | R/C | R/C | C |
| Deployment | C | C | C | — |
| Runbook | C | C | C | — |
| Risks | C | C | C | — |
| Release Checklist | C | C | C | — |
| Known Limitations | C | C | C | C |

Engineering standards tetap berada di repository dan dibaca secara selektif.

---

## 17. Initialize Product Brief First

File pertama yang diisi:

```text
docs/00_product/PRODUCT_BRIEF.md
```

Isi hanya berdasarkan Discovery Summary dan confirmed context.

Prioritas:

- problem;
- target user;
- value;
- desired outcome;
- goals bila diketahui;
- non-goals;
- product principles bila sudah meaningful;
- MVP boundary;
- assumptions;
- open questions.

### Must Not

Jangan:

- mengarang research evidence;
- mengarang market data;
- membuat target metric tanpa basis;
- mengubah assumption menjadi fact.

---

## 18. Initialize PRD Second

PRD menerjemahkan Product Brief menjadi capability-level product definition.

Isi:

- actors;
- in/out scope;
- initial capabilities;
- cross-feature journeys;
- product-wide rules;
- release scope.

### Ownership Boundary

Product Brief owns:

```text
why
who
value
product-level outcome
product-level metrics
product-level assumptions
```

PRD owns:

```text
what capabilities
cross-feature behavior
product rules
release product scope
```

Jangan copy Product Brief ke PRD.

---

## 19. Create Feature Specs Only for Understood Capabilities

Jangan membuat giant FRD.

Untuk capability yang sudah cukup jelas, copy:

```text
docs/01_features/FEATURE_TEMPLATE.md
```

menjadi:

```text
docs/01_features/authentication.md
docs/01_features/course-enrollment.md
```

Gunakan stable IDs:

```text
FR-AUTH-001
FR-ENROLLMENT-001
```

### Important Rule

Jika capability masih terlalu ambigu, jangan membuat feature spec penuh hanya untuk mengisi folder.

Catat sebagai Open Product Question atau PRD future scope.

---

## 20. Establish Architecture After Product Shape

Baru setelah Product Brief + initial PRD cukup, initialize:

```text
docs/02_architecture/SYSTEM_ARCHITECTURE.md
```

Architecture harus berasal dari:

- product capability;
- data needs;
- user interaction;
- integration boundary;
- known constraints;
- NFR/risk jika tersedia.

### Technology Selection

AI MAY recommend technology jika user belum memilih, tetapi harus menjelaskan:

```text
Requirement/constraint
        ↓
Recommended technology
        ↓
Reason
        ↓
Tradeoff
```

Jangan memilih technology hanya karena familiar.

---

## 21. Architecture Minimum

Initial architecture minimal menjelaskan:

- system purpose;
- main runtime components;
- module/system boundaries;
- dependency direction;
- data ownership;
- authentication boundary bila relevan;
- integration boundary bila relevan;
- architecture invariants.

Jika keputusan material belum dipilih:

```text
TBD / Open Architecture Decision
```

lebih baik daripada architecture fiction.

---

## 22. ADR During Initialization

Buat ADR hanya jika material architecture decision benar-benar sudah dipilih.

Contoh:

```text
ADR-0001-use-postgresql.md
```

Jangan membuat ADR untuk setiap implementation preference.

Jika decision belum dipilih, simpan sebagai Open Architecture Question.

---

## 23. Activate Conditional Documents

Setelah profile dan product shape cukup jelas, evaluasi conditional docs.

Untuk setiap document:

### Activate

Jika concern sudah nyata dan document membantu delivery.

### Keep as Template / Conditional

Jika kemungkinan segera dibutuhkan tetapi belum cukup context untuk mengisinya.

### Remove from Derived Project

Hanya jika concern jelas tidak relevan dan file hanya menjadi noise.

---

## 24. Unknown Profile → No Pruning

AI **MUST NOT remove conditional documentation while base profile is unresolved**.

Jika profile masih:

```text
TBD
```

maka:

```text
UX_FLOWS.md
DESIGN_SYSTEM.md
DATA_MODEL.md
THREAT_MODEL.md
...
```

tidak boleh dihapus hanya berdasarkan asumsi.

Pruning hanya boleh dilakukan setelah profile/context gate cukup.

---

## 25. Create Contracts Only When Boundaries Exist

REST API contract:

```text
contracts/openapi/openapi.yaml
```

dibuat hanya jika REST API menjadi actual cross-component/public boundary.

Async contract:

```text
contracts/asyncapi/asyncapi.yaml
```

dibuat hanya jika events/messages memang menjadi contract.

Jangan membuat dummy contract folder agar repository terlihat lengkap.

---

## 26. Create Source Structure Only After Architecture Is Known

Template tidak menentukan:

```text
src/
backend/
frontend/
services/
apps/
packages/
```

Source structure harus mengikuti selected architecture dan technology.

Jangan membuat folder architecture secara speculative.

---

## 27. README Is Generated Last

Project README **MUST NOT be generated during Discovery Mode**.

README baru dibuat setelah:

- Product Brief initialized;
- PRD baseline tersedia;
- base profile diketahui;
- initial architecture cukup diketahui;
- active docs diketahui;
- source/build setup diketahui jika sudah dibuat.

README harus menjadi summary project nyata, bukan daftar `TBD`.

Jika stack belum dipilih, README boleh mengatakan stack belum diputuskan, tetapi product purpose tetap harus jelas.

---

## 28. Derived Project README

README project minimal menjelaskan:

- apa product/project-nya;
- problem/outcome;
- target user bila relevan;
- current project status;
- technology stack bila sudah dipilih;
- setup/run bila tersedia;
- test command bila tersedia;
- key documentation entry points;
- deployment status bila relevan.

Derived project tidak wajib bilingual.

---

## 29. Placeholder Rules

Placeholder diperbolehkan pada reusable template files seperti:

```text
docs/01_features/FEATURE_TEMPLATE.md
docs/02_architecture/adr/ADR_TEMPLATE.md
```

Pada active project docs, metadata placeholder:

```text
<PROJECT_NAME>
<OWNER>
<YYYY-MM-DD>
<AUTHOR>
```

harus diganti.

Jika value memang belum diketahui, gunakan:

```text
TBD
Unknown
Open Question
Not decided
```

tetapi jangan menggunakan `TBD` untuk menggantikan seluruh product definition ketika discovery seharusnya dilakukan.

---

## 30. Standards During Initialization

Jangan rewrite seluruh:

```text
docs/standards/
```

untuk setiap project.

Standards adalah reusable engineering baseline.

Project-specific deviation harus hidup di:

- System Architecture;
- ADR;
- NFR;
- Threat Model;
- Design documentation;
- Configuration/operations docs;

sesuai concern ownership.

---

## 31. Validation

Setelah initialization:

```bash
python3 scripts/validate_template.py --project-mode
```

atau:

```bash
python scripts/validate_template.py --project-mode
```

Lalu jalankan project-specific checks bila source/build sudah tersedia.

Contoh:

```text
pnpm test
./mvnw test
dotnet test
```

sesuai stack.

---

## 32. Initialization Report

AI harus melaporkan:

```text
Product Context
Minimum Product Context Gate
Selected / Recommended Profile
Modifiers
Files Activated
Files Kept Conditional
Files Removed
Files Created
Feature Specs Created
Known Technology Decisions
Open Product Decisions
Open Architecture Decisions
Contracts Created
Validation / Tests Executed
Risks / Limitations
Recommended Next Step
```

Report harus faktual.

Jangan menyatakan initialization selesai jika Product Brief masih sekadar template skeleton.

---

# RECOMMENDED USER EXPERIENCE

## 33. Default Initialization Behavior

Jika user mengatakan:

```text
Initialize this project.
```

AI harus:

```text
execute Project Discovery immediately in the current turn
  ↓
inspect repository evidence and provided context
  ↓
evaluate product context
  ↓
IF insufficient:
    ask the missing discovery questions immediately
ELSE:
    summarize context
    recommend project shape
    continue directly into Phase B — Project Initialization
```

AI **MUST NOT** hanya acknowledge instruction initialization atau sekadar
menjelaskan apa yang akan dilakukan.

Ketika jawaban user membuat Minimum Product Context Gate menjadi `PASS`, AI
harus melanjutkan langsung ke Phase B tanpa meminta prompt `proceed` atau
konfirmasi tambahan. Pengecualian hanya jika user secara eksplisit meminta
discovery-only atau read-only work.

User tidak seharusnya dipaksa mengetahui:

```text
profile
modifier
stack
deployment
```

sebelum product context dibahas.

---

## 34. Recommended Initialization Prompt

Gunakan prompt sederhana:

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

### Optional Context

User MAY append known context:

```text
Project:
<NAME>

What I already know:
<PRODUCT IDEA / PROBLEM / USER / CONSTRAINTS>
```

Profile, modifiers, technology, dan deployment target boleh diberikan jika memang sudah diketahui, tetapi bukan mandatory input.

---

# INITIALIZATION DEFINITION OF DONE

## 35. Discovery Definition of Done

Discovery selesai ketika:

- [ ] project name diketahui;
- [ ] core problem cukup jelas;
- [ ] primary user cukup jelas;
- [ ] desired outcome cukup jelas;
- [ ] initial scope/MVP hypothesis cukup jelas;
- [ ] important known constraints dicatat atau eksplisit `None known yet`;
- [ ] assumptions dibedakan dari confirmed facts;
- [ ] remaining material questions eksplisit;
- [ ] Minimum Product Context Gate = `PASS`.

---

## 36. Initialization Definition of Done

Initialization selesai ketika:

- [ ] Discovery Definition of Done terpenuhi;
- [ ] base profile dipilih atau direkomendasikan berdasarkan product context;
- [ ] Product Brief menggambarkan product nyata;
- [ ] PRD mempunyai capability/scope yang diketahui;
- [ ] initial feature specs dibuat hanya untuk sufficiently understood capabilities;
- [ ] System Architecture menggambarkan baseline nyata, bukan template fiction;
- [ ] conditional docs diputuskan setelah profile diketahui;
- [ ] irrelevant docs hanya dihapus setelah cukup evidence;
- [ ] contract folders hanya dibuat bila boundary benar-benar ada;
- [ ] source structure hanya dibuat berdasarkan actual architecture/stack;
- [ ] active docs tidak memakai unresolved bootstrap metadata placeholders;
- [ ] project README dibuat terakhir dan menggambarkan project nyata;
- [ ] validation dijalankan bila tooling tersedia;
- [ ] open product/architecture decisions dilaporkan;
- [ ] remaining limitations/risks eksplisit.

Initialization **tidak berarti semua requirements atau architecture harus final**.

Tujuannya adalah menghasilkan baseline project yang cukup nyata, coherent, dan grounded untuk memulai delivery tanpa mengarang keputusan.
