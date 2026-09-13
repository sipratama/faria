from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from faria_household_mcp.database import HouseholdDatabase


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))

from scripts.operations._common import (  # noqa: E402
    DEFAULT_DATABASE_PATH,
    OperationsError,
    resolve_backup_directory,
    resolve_database_path,
    resolve_identity,
    resolve_recipient,
    verify_sqlite_database,
)
from scripts.operations.backup_faria import (  # noqa: E402
    apply_retention,
    create_backup,
)
from scripts.operations.verify_restore import verify_encrypted_backup  # noqa: E402


FAKE_AGE_HEADER = b"FAKE-AGE-TEST-ARTIFACT\n"


class FakeAge:
    def __init__(
        self,
        *,
        expected_identity: str = "test-identity",
        fail_encryption: bool = False,
        fail_decryption: bool = False,
    ) -> None:
        self.expected_identity = expected_identity
        self.fail_encryption = fail_encryption
        self.fail_decryption = fail_decryption
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, arguments) -> subprocess.CompletedProcess[str]:
        command = tuple(str(argument) for argument in arguments)
        self.calls.append(command)
        output = Path(command[command.index("--output") + 1])
        source = Path(command[-1])

        if "--encrypt" in command:
            if self.fail_encryption:
                output.write_bytes(b"incomplete")
                return subprocess.CompletedProcess(command, 1, "", "encryption failed")
            output.write_bytes(FAKE_AGE_HEADER + source.read_bytes())
            return subprocess.CompletedProcess(command, 0, "", "")

        identity = command[command.index("--identity") + 1]
        if self.fail_decryption or identity != self.expected_identity:
            return subprocess.CompletedProcess(command, 1, "", "decryption failed")
        encrypted = source.read_bytes()
        if not encrypted.startswith(FAKE_AGE_HEADER):
            return subprocess.CompletedProcess(command, 1, "", "corrupt artifact")
        output.write_bytes(encrypted.removeprefix(FAKE_AGE_HEADER))
        return subprocess.CompletedProcess(command, 0, "", "")


def create_synthetic_database(path: Path) -> None:
    database = HouseholdDatabase(path)
    database.initialize()
    now = "2099-01-01T00:00:00Z"
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO household_routines (
                id, title, schedule_kind, schedule_expression, timezone,
                status, created_at, updated_at
            ) VALUES (?, 'Synthetic backup drill', 'ONE_OFF',
                      '2099-01-02T09:00:00+07:00', 'Asia/Jakarta',
                      'PENDING_SCHEDULE', ?, ?)
            """,
            (str(uuid4()), now, now),
        )


def create_migration_001_database(path: Path, migration_directory: Path) -> None:
    migration_directory.mkdir()
    shutil.copy2(
        ROOT / "household-mcp/migrations/001_monthly_allocation.sql",
        migration_directory / "001_monthly_allocation.sql",
    )
    HouseholdDatabase(path, migrations=migration_directory).initialize()


def fake_locator(command: str) -> str:
    return f"/test-bin/{command}"


def test_backup_creates_verified_encrypted_artifact_and_manifest(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    staging_root = tmp_path / "staging"
    backup_directory.mkdir()
    staging_root.mkdir()
    create_synthetic_database(source)
    fake_age = FakeAge()

    result = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        now=datetime(2099, 1, 1, tzinfo=UTC),
        runner=fake_age,
        locator=fake_locator,
        staging_root=staging_root,
    )

    assert result.artifact.name == "faria-20990101T000000Z.sqlite.age"
    assert result.artifact.read_bytes().startswith(FAKE_AGE_HEADER)
    assert result.manifest.is_file()
    assert result.latest_migration == "004"
    assert list(staging_root.iterdir()) == []
    assert fake_age.calls[0][1:4] == ("--encrypt", "--recipient", "age1publicrecipient")
    manifest = json.loads(result.manifest.read_text(encoding="utf-8"))
    assert manifest["source_integrity_check"] == "ok"
    assert manifest["foreign_key_check"] == "ok"
    assert manifest["latest_schema_migration"] == "004"
    if sys.platform != "win32":
        assert result.artifact.stat().st_mode & 0o777 == 0o600
        assert result.manifest.stat().st_mode & 0o777 == 0o600

    with pytest.raises(sqlite3.DatabaseError):
        with sqlite3.connect(result.artifact) as connection:
            connection.execute("PRAGMA integrity_check").fetchall()


def test_backup_timestamps_are_unique_and_never_overwritten(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    backup_directory.mkdir()
    create_synthetic_database(source)
    fake_age = FakeAge()
    first_time = datetime(2099, 1, 1, tzinfo=UTC)

    first = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        now=first_time,
        runner=fake_age,
        locator=fake_locator,
    )
    second = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        now=first_time + timedelta(seconds=1),
        runner=fake_age,
        locator=fake_locator,
    )

    assert first.artifact != second.artifact
    with pytest.raises(OperationsError, match="refusing to overwrite"):
        create_backup(
            source,
            backup_directory,
            "age1publicrecipient",
            now=first_time,
            runner=fake_age,
            locator=fake_locator,
        )


def test_retention_deletes_only_old_faria_artifacts_and_sidecars(tmp_path) -> None:
    backup_directory = tmp_path / "external"
    backup_directory.mkdir()
    for day in range(16):
        artifact = backup_directory / f"faria-209901{day + 1:02d}T000000Z.sqlite.age"
        artifact.write_bytes(b"encrypted")
        artifact.with_name(f"{artifact.name}.json").write_text("{}", encoding="utf-8")
    unrelated = backup_directory / "keep-me.age"
    unrelated.write_bytes(b"unrelated")

    deleted = apply_retention(backup_directory, 14)

    assert [path.name for path in deleted] == [
        "faria-20990102T000000Z.sqlite.age",
        "faria-20990101T000000Z.sqlite.age",
    ]
    assert unrelated.is_file()
    assert len(list(backup_directory.glob("faria-*.sqlite.age"))) == 14
    assert not (backup_directory / "faria-20990101T000000Z.sqlite.age.json").exists()


def test_backup_rejects_missing_source_corrupt_database_and_unavailable_destination(
    tmp_path,
) -> None:
    backup_directory = tmp_path / "external"
    backup_directory.mkdir()
    corrupt = tmp_path / "corrupt.sqlite"
    corrupt.write_bytes(b"not sqlite")

    with pytest.raises(OperationsError, match="does not exist"):
        create_backup(
            tmp_path / "missing.sqlite",
            backup_directory,
            "age1publicrecipient",
            runner=FakeAge(),
            locator=fake_locator,
        )
    with pytest.raises(OperationsError, match="snapshot creation failed"):
        create_backup(
            corrupt,
            backup_directory,
            "age1publicrecipient",
            runner=FakeAge(),
            locator=fake_locator,
        )

    source = tmp_path / "source.sqlite"
    create_synthetic_database(source)
    with pytest.raises(OperationsError, match="must already exist"):
        create_backup(
            source,
            tmp_path / "missing-destination",
            "age1publicrecipient",
            runner=FakeAge(),
            locator=fake_locator,
        )


def test_backup_fails_closed_when_age_is_missing_or_encryption_fails(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    staging_root = tmp_path / "staging"
    backup_directory.mkdir()
    staging_root.mkdir()
    create_synthetic_database(source)

    with pytest.raises(OperationsError, match="age is not available"):
        create_backup(
            source,
            backup_directory,
            "age1publicrecipient",
            locator=lambda _: None,
        )
    with pytest.raises(OperationsError, match="no backup was published"):
        create_backup(
            source,
            backup_directory,
            "age1publicrecipient",
            runner=FakeAge(fail_encryption=True),
            locator=fake_locator,
            staging_root=staging_root,
        )

    assert list(backup_directory.iterdir()) == []
    assert list(staging_root.iterdir()) == []


def test_backup_reports_staging_storage_failure_without_artifacts(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    invalid_staging_root = tmp_path / "not-a-directory"
    backup_directory.mkdir()
    invalid_staging_root.write_text("file", encoding="utf-8")
    create_synthetic_database(source)

    with pytest.raises(OperationsError, match="filesystem operation failed"):
        create_backup(
            source,
            backup_directory,
            "age1publicrecipient",
            runner=FakeAge(),
            locator=fake_locator,
            staging_root=invalid_staging_root,
        )

    assert list(backup_directory.iterdir()) == []


def test_restore_verification_succeeds_and_cleans_plaintext(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    staging_root = tmp_path / "staging"
    backup_directory.mkdir()
    staging_root.mkdir()
    create_synthetic_database(source)
    fake_age = FakeAge()
    backup = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        runner=fake_age,
        locator=fake_locator,
    )

    result = verify_encrypted_backup(
        backup.artifact,
        "test-identity",
        runner=fake_age,
        locator=fake_locator,
        staging_root=staging_root,
    )

    assert result.latest_migration == "004"
    assert result.migration_versions == ("001", "002", "003", "004")
    assert list(staging_root.iterdir()) == []


def test_restore_rejects_wrong_identity_and_cleans_plaintext(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    staging_root = tmp_path / "staging"
    backup_directory.mkdir()
    staging_root.mkdir()
    create_synthetic_database(source)
    fake_age = FakeAge()
    backup = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        runner=fake_age,
        locator=fake_locator,
    )

    with pytest.raises(OperationsError, match="decryption failed"):
        verify_encrypted_backup(
            backup.artifact,
            "wrong-identity",
            runner=fake_age,
            locator=fake_locator,
            staging_root=staging_root,
        )

    assert list(staging_root.iterdir()) == []


def test_restore_rejects_corrupted_encrypted_artifact(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    backup_directory.mkdir()
    create_synthetic_database(source)
    fake_age = FakeAge()
    backup = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        runner=fake_age,
        locator=fake_locator,
    )
    backup.artifact.write_bytes(backup.artifact.read_bytes() + b"corruption")

    with pytest.raises(OperationsError, match="checksum does not match"):
        verify_encrypted_backup(
            backup.artifact,
            "test-identity",
            runner=fake_age,
            locator=fake_locator,
        )


def test_restore_rejects_decrypted_sqlite_integrity_failure_and_cleans_plaintext(
    tmp_path,
) -> None:
    artifact = tmp_path / "faria-20990101T000000Z.sqlite.age"
    staging_root = tmp_path / "staging"
    staging_root.mkdir()
    artifact.write_bytes(FAKE_AGE_HEADER + b"not sqlite")

    with pytest.raises(OperationsError, match="could not be verified"):
        verify_encrypted_backup(
            artifact,
            "test-identity",
            runner=FakeAge(),
            locator=fake_locator,
            staging_root=staging_root,
        )

    assert list(staging_root.iterdir()) == []


def test_restore_reports_temporary_storage_failure(tmp_path) -> None:
    artifact = tmp_path / "faria-20990101T000000Z.sqlite.age"
    invalid_staging_root = tmp_path / "not-a-directory"
    artifact.write_bytes(FAKE_AGE_HEADER + b"not sqlite")
    invalid_staging_root.write_text("file", encoding="utf-8")

    with pytest.raises(OperationsError, match="temporary storage operation failed"):
        verify_encrypted_backup(
            artifact,
            "test-identity",
            runner=FakeAge(),
            locator=fake_locator,
            staging_root=invalid_staging_root,
        )


def test_snapshot_integrity_and_foreign_keys_are_verified(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    create_synthetic_database(source)

    verification = verify_sqlite_database(source)

    assert verification.latest_migration == "004"
    assert "household_routines" in verification.table_names


def test_backup_accepts_valid_older_migration_without_upgrading_it(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    backup_directory = tmp_path / "external"
    backup_directory.mkdir()
    create_migration_001_database(source, tmp_path / "migrations")

    result = create_backup(
        source,
        backup_directory,
        "age1publicrecipient",
        runner=FakeAge(),
        locator=fake_locator,
    )

    assert result.latest_migration == "001"
    assert verify_sqlite_database(source).migration_versions == ("001",)
    with sqlite3.connect(source) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert "household_routines" not in tables


def test_operation_configuration_precedence(monkeypatch, tmp_path) -> None:
    explicit_database = tmp_path / "explicit.sqlite"
    environment_database = tmp_path / "environment.sqlite"
    explicit_backup = tmp_path / "explicit-backup"
    environment_backup = tmp_path / "environment-backup"
    monkeypatch.setenv("FARIA_DB_PATH", str(environment_database))
    monkeypatch.setenv("FARIA_BACKUP_DIR", str(environment_backup))
    monkeypatch.setenv("FARIA_BACKUP_RECIPIENT", "age1environment")
    monkeypatch.setenv("FARIA_BACKUP_IDENTITY", str(tmp_path / "environment-identity"))

    assert resolve_database_path(explicit_database) == explicit_database
    assert resolve_database_path(None) == environment_database
    assert resolve_backup_directory(explicit_backup) == explicit_backup
    assert resolve_backup_directory(None) == environment_backup
    assert resolve_recipient("age1explicit") == "age1explicit"
    assert resolve_recipient(None) == "age1environment"
    assert resolve_identity(tmp_path / "explicit-identity") == str(
        tmp_path / "explicit-identity"
    )

    monkeypatch.delenv("FARIA_DB_PATH")
    assert resolve_database_path(None) == DEFAULT_DATABASE_PATH
