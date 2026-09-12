---
name: faria-home-ops
description: Handle FARIA household routines and Telegram reminders with explicit creation and cancellation confirmation.
version: 0.1.0
author: sipratama, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [faria, household, routines, reminders, home-ops]
    related_skills: []
---

# FARIA Home Ops

Kelola routine dan reminder operasional rumah tangga FARIA dalam Bahasa Indonesia. SQLite di balik Household MCP adalah sumber kebenaran `HouseholdRoutine`. Hermes Cron hanya scheduler dan delivery adapter; hilangnya cron job tidak menghapus routine authoritative.

## Batas Scope

Skill ini hanya menangani:

- reminder rumah tangga one-off;
- routine rumah tangga berulang;
- daftar/detail/status routine;
- penyelesaian occurrence;
- pembatalan reminder mendatang.

Tolak permintaan finance, coding, deployment, system administration, web research, harga saham, scraping, dan general-purpose automation. Jangan menggunakan terminal, file, browser, web, code execution, delegation, atau computer use. Jangan membuat payment, transfer, email, push notification, calendar integration, location trigger, dependency graph, atau project plan.

## Tool Surface

Gunakan tool `faria-household` berikut (dapat tampil qualified sebagai `mcp__faria_household__...`):

`routine_list`, `routine_get`, `routine_create`, `routine_scheduler_link`, `routine_complete`, `routine_cancel`.

Gunakan Hermes `cronjob` hanya untuk membuat, menjalankan, atau membersihkan jadwal routine rumah tangga yang sudah dinormalisasi. Jangan gunakan cron untuk coding, deploy, restart server, scraping, market monitoring, atau automasi umum.

Cron execution harus dibatasi per job ke:

`skills`, `mcp-faria-household-cron-readonly`.

Alias read-only tersebut hanya boleh mengekspos `routine_get`. Jika alias/tool tidak tersedia, jangan membuat jadwal dengan surface yang lebih luas; laporkan konfigurasi runtime belum siap.

## Timezone dan Normalisasi Jadwal

- Household timezone V1 adalah tepat `Asia/Jakarta`.
- Household MCP hanya menerima `ONE_OFF` atau `RECURRING` dan jadwal canonical.
- `ONE_OFF` memakai timestamp ISO offset-aware dengan offset Jakarta, misalnya `2026-09-13T19:00:00+07:00`.
- `RECURRING` memakai tepat lima field cron, misalnya `0 19 * * *`, `0 9 20 * * *`, atau `0 10 1 */3 *`.
- Natural-language time resolution dilakukan di percakapan sebelum tool MCP dipanggil.
- Jangan mengarang tanggal atau jam. Tanyakan bila waktu belum presisi, termasuk `nanti sore`, `awal bulan`, `beberapa minggu lagi`, atau tanggal berulang tanpa jam.
- Tampilkan waktu dalam WIB dan sebutkan `Asia/Jakarta` pada proposal.

## Konfirmasi Eksplisit

Creation dan cancellation menghasilkan proactive future behavior sehingga wajib mendapat konfirmasi yang jelas dan spesifik.

Creation yang valid misalnya:

- `Konfirmasi buat routine ini`;
- `Ya, buat reminder beli galon tersebut`.

Cancellation yang valid misalnya:

- `Konfirmasi pembatalan routine Service AC`;
- `Ya, batalkan reminder filter air tersebut`.

`oke`, `sip`, `mantap`, `lanjut`, `yaudah`, emoji, diam, atau afirmasi umum tidak cukup untuk membuat atau membatalkan routine. Tanyakan kembali objek dan aksi yang perlu dikonfirmasi. Existing finance confirmation policy tidak berubah.

Pernyataan completion yang jelas seperti `Service AC sudah selesai` boleh langsung diproses tanpa turn konfirmasi tambahan bila tepat satu routine cocok. Bila beberapa routine mungkin cocok, tanyakan pilihan.

## Matching Routine

Gunakan matching deterministik dari `routine_list`:

1. exact match;
2. case-insensitive match;
3. obvious unique normalized match.

Jika lebih dari satu kandidat masuk akal, tanyakan routine yang dimaksud. Jangan memakai embedding atau vector search.

## Saga Creation

1. Normalisasi title, description opsional, schedule kind, canonical schedule, waktu WIB, dan timezone.
2. Tampilkan proposal lengkap dan minta konfirmasi creation eksplisit.
3. Setelah konfirmasi, panggil `routine_create`. State harus `PENDING_SCHEDULE`; jangan menyatakan active.
4. Buat Hermes cron job dengan canonical schedule, `deliver="origin"`, skill `faria-home-ops`, dan `enabled_toolsets=["skills", "mcp-faria-household-cron-readonly"]`.
5. Prompt cron harus self-contained sesuai bagian berikut.
6. Jika cron creation gagal, biarkan routine `PENDING_SCHEDULE`, laporkan scheduling failure, dan jangan mengklaim reminder active.
7. Jika cron creation berhasil, panggil `routine_scheduler_link` dengan routine UUID dan returned cron job ID.
8. Hanya setelah link mengembalikan `ACTIVE`, laporkan routine berhasil aktif.
9. Jika scheduler link gagal, best-effort `cronjob(action="remove", job_id=...)`; jangan mengklaim sukses. Routine tetap `PENDING_SCHEDULE` dan dapat direkonsiliasi lewat percakapan berikutnya.

Jangan menyimpan Telegram numeric ID, API key, filesystem path, atau cron prompt body di HouseholdRoutine.

## Prompt Cron Self-Contained

Gunakan prompt dengan isi semantik berikut untuk setiap job, memasukkan hanya routine UUID:

```text
You are executing a FARIA Household Routine reminder.

Routine ID: <routine_uuid>

Load the faria-home-ops skill.
Use only the read-only Household MCP routine_get tool for this routine.

If authoritative routine status is not ACTIVE, respond only:
[SILENT]

If ACTIVE, send a concise Indonesian household reminder for the routine title and description.

Do not execute external actions.
Do not modify financial state.
Do not use tools outside the approved Home Ops read-only surface.
```

Cron berjalan di fresh session. Jangan bergantung pada chat history atau memory percakapan. Delivery harus kembali ke `origin` yang membuat job. Jangan menyertakan user/chat ID, credentials, financial data, atau private path.

## Completion

1. Resolve tepat satu routine menggunakan list/get.
2. Panggil `routine_complete` hanya untuk routine `ACTIVE`.
3. Untuk `ONE_OFF`, hasil authoritative menjadi `COMPLETED`; setelah MCP sukses, best-effort remove cron job bila masih ada. Job yang sudah fired/missing bukan error.
4. Untuk `RECURRING`, hasil authoritative tetap `ACTIVE`, `last_completed_at` berubah, dan cron job tidak dihapus karena hanya occurrence saat ini yang selesai.

## Cancellation

1. Resolve routine dan tampilkan konsekuensi bahwa reminder berikutnya berhenti.
2. Minta konfirmasi cancellation eksplisit.
3. Setelah konfirmasi, panggil `routine_cancel` terlebih dahulu. `CANCELLED` authoritative berlaku segera.
4. Setelah MCP sukses, best-effort remove `scheduler_job_id` bila ada.
5. Jika cron removal gagal, jangan rollback ke `ACTIVE`. Orphan job wajib membaca status dan menghasilkan `[SILENT]`.

## Listing dan Reconciliation

- `routine_list` default menampilkan `PENDING_SCHEDULE` dan `ACTIVE`; gunakan include-inactive hanya saat history diperlukan.
- Jelaskan `PENDING_SCHEDULE` sebagai routine yang tersimpan tetapi scheduler belum aktif/perlu scheduling attention.
- Jangan menyimpulkan routine tidak ada hanya karena cron job hilang.
- Tidak ada reconciliation daemon pada RF-06; retry dilakukan melalui controlled conversational flow.

## Deferred

`SNOOZE` deferred setelah RF-06. Edit/reschedule dan automatic background reconciliation juga belum tersedia. Jangan membuat cron-job juggling sementara untuk meniru snooze.
