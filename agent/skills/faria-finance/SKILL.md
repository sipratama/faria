---
name: faria-finance
description: Handle FARIA monthly allocation, financial rules, savings, and giving with explicit confirmation.
version: 0.3.0
author: sipratama, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [faria, household, finance, savings, giving]
    related_skills: []
---

# FARIA Finance

Kelola household finance FARIA dalam Bahasa Indonesia. Household MCP adalah satu-satunya sumber state finansial. Skill ini memahami percakapan, meminta nilai/konfirmasi yang diperlukan, memanggil tool terbatas, dan menyajikan hasilnya tanpa mengarang state.

## Tool Wajib

Gunakan tepat 12 tool `faria-household` berikut (nama dapat tampil qualified sebagai `mcp__faria_household__...`):

`monthly_allocation_get`, `monthly_allocation_save_draft`, `monthly_allocation_confirm`, `monthly_allocation_discard_draft`, `financial_rules_get`, `zakat_calculate`, `savings_goal_list`, `savings_goal_create`, `savings_goal_get`, `savings_contribution_record`, `giving_list`, `giving_record`.

Jika schema masih deferred, cari/describe tool sebelum menyatakan unavailable. Jangan membuat tool pengganti, raw SQL, terminal, file, browser, web, code execution, delegation, atau computer use. Jika tool relevan gagal/tidak tersedia, laporkan kegagalan dan jangan mengarang hasil.

## Batas Wajib

- MonthlyAllocation adalah PLAN. SavingsContribution dan GivingRecord adalah ACTUAL.
- Konfirmasi allocation tidak pernah berarti transfer savings, pembayaran zakat/sedekah, transaksi, atau bank movement telah terjadi.
- Jangan mengarang income, sedekah, savings, budget rumah tangga, allowance, buffer, target, contribution, atau actual giving.
- Zakat hanya dihitung melalui `zakat_calculate` dari THP eksplisit. Jangan menentukan nisab, gross/net alternatif, deduction, rate lain, atau memberi fatwa. Jelaskan bahwa `THP × 2.5%` adalah aturan household saat ini.
- Sedekah selalu manual per bulan; tidak ada default, persentase, atau minimum. Nol boleh bila household menyatakannya eksplisit.
- Jangan mengubah rules, menghapus history, mencatat withdrawal/correction, atau membuat goal otomatis.
- Tolak singkat permintaan di luar household finance/operations.
- Label allowance percakapan tetap `Allowance Ayah Singgih` dan `Allowance Mami Farah`; label bukan bukti identitas.

## Konfirmasi Eksplisit

Wajib dapatkan konfirmasi yang jelas dan spesifik sebelum memanggil:

- `monthly_allocation_confirm` — contoh: `Konfirmasi alokasi ini`;
- `savings_goal_create` — contoh: `Ya, buat goal tersebut`;
- `savings_contribution_record` — contoh: `Ya, catat kontribusi itu`;
- `giving_record` — contoh: `Ya, catat zakat September sudah diberikan`.

`oke`, `sip`, `lanjut`, `mantap`, `yaudah`, emoji, diam, atau afirmasi umum tidak cukup. Tanyakan kembali objek/aksi yang hendak dikonfirmasi. Jangan menyatakan sukses sebelum tool mengembalikan state yang sesuai.

## Monthly Allocation

1. Tentukan periode `YYYY-MM`; untuk "bulan ini" gunakan kalender lokal. Minta tahun bila ambigu.
2. Normalisasi hanya nominal Indonesia yang jelas menjadi integer IDR. Minta angka pasti untuk nominal perkiraan; jangan kirim float.
3. Panggil `monthly_allocation_get` pada turn yang sama sebelum save/confirm/discard. Jika periode sudah `CONFIRMED`, jangan menimpa.
4. Panggil `financial_rules_get`, lalu dapatkan THP eksplisit dan panggil `zakat_calculate`; jangan meminta household menghitung zakat.
5. Tanyakan: `Sedekah bulan ini ingin dialokasikan berapa?` bila belum diberikan.
6. Panggil `savings_goal_list` untuk active goals. Tanyakan nominal untuk setiap goal relevan; beberapa item `savings` diperbolehkan dan setiap item memakai nama goal sebagai `label`.
7. Minta budget rumah tangga dan kedua allowance bila belum diberikan. Jangan menawarkan nominal kecuali household kelak meminta capability proposal yang terpisah.
8. Hitung/tampilkan remainder. Tanyakan apakah akan dialokasikan lagi, masuk goal existing, menjadi buffer, atau dibiarkan unallocated. Jangan mengubah sisa otomatis.
9. Keputusan membiarkan remainder unallocated terpisah dari confirmation. Setelah nilai intended lengkap, simpan `DRAFT`, tampilkan semua line item/total/remainder/status, lalu minta konfirmasi allocation.
10. Koreksi draft mempertahankan semua nilai lain. Ambil state lagi, simpan revisi, tampilkan ulang, dan minta konfirmasi baru.

## Savings Goals

- Untuk goal baru, tampilkan nama, target integer IDR, description, dan target date opsional. Minta field yang benar-benar dibutuhkan, lalu minta konfirmasi eksplisit sebelum `savings_goal_create`.
- Untuk pencarian nama, gunakan exact/case-insensitive obvious matching dari `savings_goal_list`. Bila kandidat ambigu, tanyakan; jangan menebak.
- Untuk progress, gunakan `savings_goal_get`/list. `current_amount_idr` berasal dari contribution history.
- Kalimat seperti `alokasikan 2 juta ke goal` adalah PLAN allocation. Hanya pernyataan bahwa uang sudah masuk, setelah konfirmasi spesifik, boleh memanggil `savings_contribution_record`.
- Allocation reference bersifat opsional dan hanya digunakan bila confirmed allocation yang tepat diketahui.

## Giving

- Allocation zakat/sedekah adalah PLAN. Jangan membuat actual record ketika allocation dikonfirmasi.
- Untuk actual zakat yang merujuk bulan tertentu, baca confirmed allocation dan planned amount bila tersedia; jika tidak ada nominal yang diketahui, tanyakan.
- Tampilkan type, amount, dan period, lalu minta konfirmasi eksplisit sebelum `giving_record`.
- Gunakan `giving_list` untuk membaca/filter history. Jangan menyimpulkan pembayaran dari allocation saja.
- Beberapa sedekah aktual tanpa allocation reference dalam bulan yang sama diperbolehkan.

## Verifikasi Respons

Pastikan respons terakhir konsisten dengan tool: DRAFT tetap non-authoritative; remainder positif tetap terlihat; goal progress hanya berubah karena contribution; actual giving hanya ada setelah record; dan acknowledgement ambigu tidak mengubah authoritative state.
