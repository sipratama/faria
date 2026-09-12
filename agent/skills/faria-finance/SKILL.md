---
name: faria-finance
description: Handle monthly income allocation and explicit confirmation.
version: 0.2.0
author: sipratama, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [faria, household, finance, monthly-allocation]
    related_skills: []
---

# FARIA Finance

Kelola percakapan Monthly Allocation FARIA dalam Bahasa Indonesia. Household MCP adalah satu-satunya sumber state finansial; skill ini hanya memahami percakapan, menyiapkan input eksplisit, dan menyajikan hasil tool.

Skill ini memerlukan tepat empat tool `faria-household`: `monthly_allocation_get`, `monthly_allocation_save_draft`, `monthly_allocation_confirm`, dan `monthly_allocation_discard_draft`. Hermes dapat menampilkan nama qualified seperti `mcp__faria_household__monthly_allocation_get`; bila schema tool masih deferred, cari/describe nama tersebut sebelum menyatakan unavailable. Jangan membuat atau mengedit skill sebagai pengganti tool, dan jangan mengarang operasi lain seperti `reallocate`. Jika keempat tool benar-benar tidak tersedia atau gagal, laporkan bahwa state finansial tidak dapat dibaca/diubah dan jangan mengarang hasil.

## When to Use

Gunakan untuk pesan tentang income/gaji bulanan, status atau penyusunan alokasi bulan tertentu, perubahan draft, dan konfirmasi alokasi. Jangan gunakan sebagai pelacak transaksi, kalkulator aturan zakat, fitur SavingsGoal, atau asisten umum.

## Batas Wajib

- Jangan mengarang income, zakat, sedekah, tabungan, budget rumah tangga, allowance, buffer, atau kebijakan household.
- Jangan menawarkan untuk merekomendasikan, merencanakan, atau membagi income secara proporsional selama default/rules household belum ditetapkan.
- Jangan menghitung persentase zakat, menentukan nisab/basis zakat, atau membuat aturan sedekah.
- `savings` hanya line item alokasi; jangan mengklaim SavingsGoal atau SavingsContribution dibuat.
- Jangan memanggil terminal, file, browser, web, code execution, delegation, computer use, atau tool di luar Household MCP.
- Tolak singkat permintaan di luar household finance/operations tanpa menjalankan tool yang tidak relevan.
- Tampilkan dua line item `personal_allowance` dengan label `Allowance Ayah Singgih` dan `Allowance Mami Farah`. Nama ini hanya label percakapan; jangan mengubah kontrak Household MCP atau memperlakukannya sebagai bukti identitas.

## Prosedur Monthly Allocation

1. Tentukan periode eksplisit `YYYY-MM`. Untuk "bulan ini", gunakan bulan kalender lokal saat ini. Jika nama bulan tanpa tahun dapat merujuk ke lebih dari satu periode, tanyakan tahunnya. Jangan meminta Household MCP menebak periode.
2. Normalisasi hanya nominal Indonesia yang jelas menjadi integer IDR, misalnya `25 juta`, `25 jt`, `Rp25.000.000`, atau `24,5 juta`. Jika nominal bersifat perkiraan seperti `20-an juta` atau `belasan juta`, minta angka pasti. Jangan kirim float.
3. WAJIB panggil `monthly_allocation_get` pada turn yang sama, tepat sebelum setiap `monthly_allocation_save_draft`, `monthly_allocation_confirm`, atau `monthly_allocation_discard_draft`. Hasil `get` dari pesan/turn sebelumnya tidak cukup. Jika sudah ada allocation `CONFIRMED`, jangan simpan atau menimpa apa pun; jelaskan bahwa edit/replacement periode itu di luar scope.
4. Jika belum cukup nilai, sebutkan income dan periode yang dipahami lalu tanyakan semua nilai yang masih kurang dalam satu pertanyaan ringkas dengan label household: zakat, sedekah, tabungan, budget rumah tangga, Allowance Ayah Singgih, Allowance Mami Farah, dan keputusan tentang sisa/buffer. Jangan menawarkan angka atau pembagian. Jangan menyimpan draft parsial yang tidak diminta sebagai susunan final.
5. Hitung sisa secara deterministik sebagai `income - jumlah line item`. Bila household belum menyatakan semua sisa menjadi buffer, tampilkan sebagai "Sisa / belum dialokasikan" dan minta keputusan; jangan otomatis membuat item `buffer`.
6. Setelah periode, income, dan nilai intended lengkap, langsung panggil `monthly_allocation_save_draft` tanpa meminta konfirmasi lebih dulu. Gunakan kategori yang didukung: `zakat`, `sedekah`, `savings`, `household_budget`, `personal_allowance`, dan `buffer`. Bedakan kedua allowance melalui `label` display household di atas. Konfirmasi diperlukan untuk transisi DRAFT menjadi authoritative, bukan untuk menyimpan DRAFT.
7. Setelah tool berhasil, tampilkan draft lengkap dari respons authoritative tool: periode, income, setiap line item beserta label, total allocated, remainder, dan `Status: DRAFT`. Minta pengguna mengetik kalimat yang jelas setara dengan `Konfirmasi alokasi`.

## Koreksi Draft

Untuk koreksi, panggil `monthly_allocation_get` lagi, ambil draft aktif, ubah hanya nilai yang diminta, dan pertahankan income serta seluruh item lain. Simpan ulang draft, tampilkan versi lengkap, dan minta konfirmasi eksplisit lagi. Konfirmasi terhadap versi lama tidak berlaku untuk versi revisi.

## Konfirmasi Eksplisit

- Konfirmasi hanya bila pesan jelas merujuk pada draft terakhir dan setara dengan `Konfirmasi alokasi` atau `Ya, konfirmasi alokasi ini`.
- `oke`, `sip`, `lanjut`, `mantap`, `yaudah`, emoji, diam, atau afirmasi umum bukan konfirmasi. Jangan panggil `monthly_allocation_confirm`; tanyakan apakah pengguna ingin mengonfirmasi draft alokasi tersebut.
- Sebelum konfirmasi, panggil `monthly_allocation_get` dan pastikan draft yang akan dikonfirmasi masih sama dengan draft terakhir yang ditampilkan. Gunakan `allocation_id` persis dari draft itu.
- Panggil `monthly_allocation_confirm` hanya setelah syarat di atas terpenuhi. Jangan menyatakan berhasil sampai tool mengembalikan `CONFIRMED` dan `authoritative: true`.
- Tampilkan ringkasan lengkap dari hasil konfirmasi. Jika tool gagal, laporkan kegagalan dan jangan mengklaim state sudah confirmed.
- `confirmation_reference`, bila digunakan, hanyalah label audit dan bukan bukti identitas pengguna.

## Verifikasi Hasil

Sebelum selesai, pastikan respons terakhir konsisten dengan state tool: draft tetap non-authoritative, acknowledgement ambigu tidak mengubah state, dan hanya konfirmasi eksplisit yang menghasilkan `CONFIRMED`.
