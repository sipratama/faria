from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "agent" / "skills" / "faria-home-ops" / "SKILL.md"
SOUL = ROOT / "agent" / "prompts" / "SOUL.md"
FEATURE = ROOT / "docs" / "01_features" / "household-routines.md"
ARCHITECTURE = ROOT / "docs" / "02_architecture" / "SYSTEM_ARCHITECTURE.md"


def test_clear_one_off_creation_may_proceed_without_second_confirmation() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    feature = FEATURE.read_text(encoding="utf-8")

    assert "Ingatkan saya 3 menit lagi untuk cek galon." in skill
    assert "tanpa meminta turn konfirmasi tambahan" in skill
    assert "without requiring a second confirmation turn" in feature


def test_clear_recurring_creation_may_proceed_without_second_confirmation() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    feature = FEATURE.read_text(encoding="utf-8")

    assert "Ingatkan service AC setiap 3 bulan tanggal 1 jam 09:00." in skill
    assert "may proceed directly as a recurring routine" in feature


def test_vague_schedule_requires_clarification_without_mutation() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    feature = FEATURE.read_text(encoding="utf-8")

    assert "Ingatkan nanti sore" in skill
    assert "Service AC beberapa bulan lagi" in skill
    assert "minta klarifikasi dan berhenti tanpa mutation" in skill
    assert "Vague or incomplete schedules require clarification" in feature


def test_generic_acknowledgement_alone_cannot_create_a_routine() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    soul = SOUL.read_text(encoding="utf-8")

    assert "`oke`, `sip`, `mantap`, `lanjut`" in skill
    assert "bukan perintah creation mandiri" in skill
    assert "bukan perintah creation mandiri" in soul


def test_generic_acknowledgement_does_not_duplicate_successful_creation() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    feature = FEATURE.read_text(encoding="utf-8")

    assert "tidak boleh memanggil ulang `routine_create`" in skill
    assert "tidak boleh menduplikasi routine atau cron job" in skill
    assert "does not repeat `routine_create`, cron creation" in feature


def test_cancellation_still_requires_explicit_confirmation() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    feature = FEATURE.read_text(encoding="utf-8")
    architecture = ARCHITECTURE.read_text(encoding="utf-8")

    assert "Konfirmasi pembatalan routine Service AC" in skill
    assert "obtains explicit cancellation confirmation" in feature
    assert "cancellation still requires explicit object-specific confirmation" in architecture


def test_generic_acknowledgement_cannot_cancel() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    soul = SOUL.read_text(encoding="utf-8")

    assert "`oke`, `sip`, `ya`" in skill
    assert "tidak cukup untuk membatalkan routine" in skill
    assert "afirmasi umum tidak boleh membatalkan" in soul


def test_clear_completion_remains_allowed_without_confirmation() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    feature = FEATURE.read_text(encoding="utf-8")

    assert "Service AC sudah selesai" in skill
    assert "tanpa turn konfirmasi tambahan" in skill
    assert "without an extra confirmation turn" in feature


def test_home_ops_skill_encodes_scheduler_saga_and_orphan_safety() -> None:
    skill = SKILL.read_text(encoding="utf-8")

    assert "PENDING_SCHEDULE" in skill
    assert "routine_scheduler_link" in skill
    assert 'deliver="origin"' in skill
    assert 'enabled_toolsets=["skills", "mcp-faria-household-cron-readonly"]' in skill
    assert "[SILENT]" in skill
    assert "routine_get" in skill


def test_home_ops_scope_refuses_general_automation_and_preserves_finance_policy() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    soul = SOUL.read_text(encoding="utf-8")

    assert "deployment" in skill
    assert "harga saham" in skill
    assert "general-purpose automation" in skill
    assert "general-purpose automation" in soul
    assert "Existing finance confirmation policy tidak berubah." in skill
    assert "Kebijakan konfirmasi finance tidak berubah." in soul
