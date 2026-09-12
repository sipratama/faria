from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "agent" / "skills" / "faria-home-ops" / "SKILL.md"
SOUL = ROOT / "agent" / "prompts" / "SOUL.md"


def test_home_ops_skill_encodes_conservative_confirmation_boundary() -> None:
    skill = SKILL.read_text(encoding="utf-8")

    assert "Konfirmasi buat routine ini" in skill
    assert "Konfirmasi pembatalan routine" in skill
    assert "`oke`, `sip`, `mantap`, `lanjut`" in skill
    assert "tidak cukup untuk membuat atau membatalkan routine" in skill


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
