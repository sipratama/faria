# Scripts

Folder ini berisi utility ringan untuk membantu menjaga konsistensi dan kesehatan repository **Annotasi Template** maupun project yang dibuat dari template ini.

Saat ini tersedia:

```text
scripts/
├── README.md
└── validate_template.py
```

---

## `validate_template.py`

`validate_template.py` adalah **structural validator** untuk Annotasi Template.

Script ini membantu mendeteksi masalah mekanis seperti:

- file penting template yang tidak sengaja terhapus;
- local Markdown link yang rusak setelah file dipindahkan/di-rename;
- metadata placeholder template yang masih tertinggal setelah repository diinisialisasi menjadi project nyata.

Script ini **tidak** menilai kualitas isi dokumen.

Artinya validator tidak dapat menentukan apakah:

- PRD sudah benar;
- architecture sudah tepat;
- threat model sudah lengkap;
- NFR sudah realistis;
- feature requirement sudah cukup baik.

Untuk hal tersebut tetap diperlukan review manusia dan/atau AI terhadap authoritative project documentation.

---

# Mode Penggunaan

Validator memiliki dua mode.

## 1. Template Mode

Gunakan mode ini ketika bekerja langsung pada repository:

```text
annotasi-template
```

Jalankan dari root repository:

```bash
python3 scripts/validate_template.py
```

Pada beberapa environment:

```bash
python scripts/validate_template.py
```

### Yang diperiksa

Template mode memeriksa:

- expected template files;
- local Markdown links.

Contoh sukses:

```text
Validation passed (template mode).
```

Contoh failure:

```text
Validation failed:
- missing required template file: docs/standards/08_SECURITY_STANDARD.md
```

atau:

```text
Validation failed:
- README.md: broken local link: ./docs/00_product/PRDS.md
```

### Kapan digunakan

Disarankan menjalankan template mode:

- setelah menambah dokumen;
- setelah memindahkan file;
- setelah rename file/folder;
- setelah mengubah cross-link;
- sebelum commit perubahan struktur;
- sebelum membuat release/tag Annotasi Template.

Contoh workflow:

```bash
git status

python3 scripts/validate_template.py

git add .
git commit -m "docs: update template documentation"
```

---

## 2. Project Mode

Gunakan mode ini pada repository **hasil turunan dari Annotasi Template** setelah project initialization dilakukan.

Contoh:

```text
annotasi-template
       ↓
Use this template
       ↓
my-project
```

Jalankan:

```bash
python3 scripts/validate_template.py --project-mode
```

### Yang diperiksa

Project mode memeriksa:

- local Markdown links;
- unresolved core project metadata placeholders.

Contoh placeholder yang seharusnya tidak lagi tertinggal pada active project documentation:

```text
<PROJECT_NAME>
<OWNER>
<AUTHOR>
<YYYY-MM-DD>
```

Contoh failure:

```text
Validation failed:
- docs/00_product/PRODUCT_BRIEF.md: unresolved project metadata placeholder <PROJECT_NAME>
- docs/00_product/PRODUCT_BRIEF.md: unresolved project metadata placeholder <OWNER>
```

Contoh sukses:

```text
Validation passed (project mode).
```

---

# Kenapa Project Mode Tidak Memaksa Semua Template File Tetap Ada?

Project yang dibuat dari Annotasi Template tidak harus menggunakan seluruh dokumentasi.

Contoh:

```text
backend-service
```

mungkin tidak memerlukan:

```text
UX_FLOWS.md
DESIGN_SYSTEM.md
```

Sedangkan prototype mungkin belum memerlukan:

```text
RUNBOOK.md
RELEASE_CHECKLIST.md
```

Karena itu:

```bash
python3 scripts/validate_template.py --project-mode
```

tidak mewajibkan seluruh file template tetap tersedia.

Prinsipnya:

> **Template lengkap, derived project proporsional.**

Document activation rules tersedia di:

```text
docs/PROJECT_INITIALIZATION.md
```

---

# Local Markdown Link Validation

Validator memeriksa link repository-local seperti:

```md
[PRD](./docs/00_product/PRD.md)
```

atau:

```md
[System Architecture](../02_architecture/SYSTEM_ARCHITECTURE.md)
```

Jika file target tidak ditemukan, validation gagal.

External links seperti:

```md
[OpenAI](https://openai.com)
```

tidak diperiksa.

Alasannya:

- validator tetap cepat;
- dapat berjalan offline;
- tidak bergantung pada network;
- tidak menghasilkan false failure akibat website external sedang unavailable.

---

# Placeholder Validation

Placeholder diperbolehkan pada reusable template files, contohnya:

```text
docs/01_features/FEATURE_TEMPLATE.md
docs/02_architecture/adr/ADR_TEMPLATE.md
```

Namun pada active project docs, metadata bootstrap seharusnya sudah diisi setelah initialization.

Contoh:

```md
# Product Brief — <PROJECT_NAME>
```

harus berubah menjadi misalnya:

```md
# Product Brief — Pedago
```

Jika nilai sebenarnya belum diputuskan, gunakan nilai eksplisit seperti:

```text
TBD
Unknown
Open Question
Not decided
```

daripada mengarang fakta.

---

# Recommended Initialization Flow

Untuk project baru:

```text
Create repository from Annotasi Template
        ↓
Read AGENTS.md
        ↓
Read docs/PROJECT_INITIALIZATION.md
        ↓
Initialize project documentation
        ↓
Create only relevant project-specific structures/contracts
        ↓
Run project validator
        ↓
Run project build/tests
```

Command:

```bash
python3 scripts/validate_template.py --project-mode
```

Setelah itu lanjutkan dengan project-specific checks, misalnya:

```bash
pnpm test
```

atau:

```bash
./mvnw test
```

atau:

```bash
dotnet test
```

sesuai stack project.

---

# CI Usage

Validator dapat dijalankan di CI.

Untuk repository Annotasi Template:

```bash
python3 scripts/validate_template.py
```

Contoh high-level flow:

```text
Pull Request
     ↓
validate_template.py
     ↓
PASS
     ↓
merge
```

Validator ini cocok dijadikan lightweight repository health check untuk perubahan dokumentasi dan struktur.

Project yang dibuat dari Annotasi Template juga dapat menjalankan:

```bash
python3 scripts/validate_template.py --project-mode
```

jika struktur dokumentasinya tetap mengikuti Annotasi Template.

---

# Scope Validator

## Validator dapat mengecek

```text
✓ required template files
✓ local Markdown links
✓ core initialization placeholders in project mode
```

## Validator tidak mengecek

```text
✗ kualitas requirement
✗ correctness architecture
✗ security completeness
✗ kualitas source code
✗ API compatibility secara semantic
✗ database migration safety
✗ external URL availability
✗ apakah tests project pass
```

Dengan kata lain:

```text
validate_template.py
        =
structural health check

Human / AI engineering review
        =
semantic correctness
```

Keduanya saling melengkapi, bukan saling menggantikan.

---

# Troubleshooting

## `python3: command not found`

Coba:

```bash
python --version
python scripts/validate_template.py
```

Pastikan Python tersedia di environment.

---

## Broken Local Link

Contoh:

```text
README.md: broken local link: ./docs/00_product/PRDS.md
```

Periksa:

1. apakah filename benar;
2. apakah relative path benar;
3. apakah target file sudah dipindahkan;
4. apakah link masih diperlukan.

---

## Missing Required Template File

Contoh:

```text
missing required template file: docs/standards/08_SECURITY_STANDARD.md
```

Jika Anda sedang mengembangkan **Annotasi Template**, file tersebut seharusnya tetap ada.

Jika Anda sedang mengembangkan **derived project**, gunakan:

```bash
python3 scripts/validate_template.py --project-mode
```

karena project mode tidak memaksa seluruh template file tetap tersedia.

---

## Unresolved Placeholder

Contoh:

```text
docs/00_product/PRODUCT_BRIEF.md:
unresolved project metadata placeholder <PROJECT_NAME>
```

Isi metadata project sebenarnya atau gunakan nilai eksplisit seperti `TBD` jika memang belum diputuskan.

---

# Maintenance

Jika struktur canonical Annotasi Template berubah, update:

```text
scripts/validate_template.py
```

terutama daftar:

```text
REQUIRED_TEMPLATE_FILES
PROJECT_SPECIFIC_DOCS
```

Jangan menambahkan file ke required list hanya karena file tersebut tersedia.

File seharusnya menjadi required hanya jika kehilangan file tersebut membuat **repository template** tidak lagi lengkap atau konsisten.
