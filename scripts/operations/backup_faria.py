from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

try:
    from ._common import (
        BACKUP_FILENAME_RE,
        BACKUP_FORMAT_VERSION,
        OperationsError,
        resolve_backup_directory,
        resolve_database_path,
        resolve_recipient,
        set_directory_permissions,
        set_file_permissions,
        sha256_file,
        sqlite_readonly_uri,
        verify_sqlite_database,
    )
except ImportError:
    from _common import (  # type: ignore[no-redef]
        BACKUP_FILENAME_RE,
        BACKUP_FORMAT_VERSION,
        OperationsError,
        resolve_backup_directory,
        resolve_database_path,
        resolve_recipient,
        set_directory_permissions,
        set_file_permissions,
        sha256_file,
        sqlite_readonly_uri,
        verify_sqlite_database,
    )


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
CommandLocator = Callable[[str], str | None]


@dataclass(frozen=True)
class BackupResult:
    artifact: Path
    manifest: Path
    latest_migration: str
    deleted_artifacts: tuple[Path, ...]


def run_command(arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(arguments),
        capture_output=True,
        check=False,
        text=True,
    )


def create_consistent_snapshot(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise OperationsError("source SQLite database does not exist")
    try:
        with sqlite3.connect(sqlite_readonly_uri(source), uri=True, timeout=5.0) as source_db:
            with sqlite3.connect(destination) as snapshot_db:
                source_db.backup(snapshot_db)
    except sqlite3.Error as error:
        raise OperationsError("consistent SQLite snapshot creation failed") from error
    set_file_permissions(destination)


def retention_deletions(backup_directory: Path, keep: int) -> tuple[Path, ...]:
    if keep < 1:
        raise OperationsError("retention keep count must be at least 1")
    artifacts = sorted(
        (
            path
            for path in backup_directory.iterdir()
            if path.is_file() and BACKUP_FILENAME_RE.fullmatch(path.name)
        ),
        key=lambda path: path.name,
        reverse=True,
    )
    return tuple(artifacts[keep:])


def apply_retention(backup_directory: Path, keep: int) -> tuple[Path, ...]:
    deletions = retention_deletions(backup_directory, keep)
    for artifact in deletions:
        artifact.unlink()
        manifest = artifact.with_name(f"{artifact.name}.json")
        if manifest.is_file():
            manifest.unlink()
    return deletions


def create_backup(
    source: Path,
    backup_directory: Path,
    recipient: str,
    *,
    keep: int = 14,
    age_command: str = "age",
    now: datetime | None = None,
    runner: CommandRunner = run_command,
    locator: CommandLocator = shutil.which,
    staging_root: Path | None = None,
) -> BackupResult:
    source = source.expanduser()
    backup_directory = backup_directory.expanduser()
    if not source.is_file():
        raise OperationsError("source SQLite database does not exist")
    if not backup_directory.is_dir():
        raise OperationsError("backup directory must already exist and be a directory")
    if locator(age_command) is None:
        raise OperationsError("age is not available; install age and re-run the backup")

    timestamp = (now or datetime.now(UTC)).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    snapshot_name = f"faria-{timestamp}.sqlite"
    artifact = backup_directory / f"{snapshot_name}.age"
    manifest = artifact.with_name(f"{artifact.name}.json")
    if artifact.exists() or manifest.exists():
        raise OperationsError("backup artifact already exists; refusing to overwrite it")

    temporary_artifact = backup_directory / f".{artifact.name}.{uuid4().hex}.tmp"
    temporary_manifest = backup_directory / f".{manifest.name}.{uuid4().hex}.tmp"
    try:
        with tempfile.TemporaryDirectory(
            prefix="faria-backup-",
            dir=staging_root,
        ) as temporary_directory:
            staging_directory = Path(temporary_directory)
            set_directory_permissions(staging_directory)
            snapshot = staging_directory / snapshot_name
            create_consistent_snapshot(source, snapshot)
            verification = verify_sqlite_database(snapshot)

            previous_umask = os.umask(0o077)
            try:
                encryption = runner(
                    [
                        age_command,
                        "--encrypt",
                        "--recipient",
                        recipient,
                        "--output",
                        str(temporary_artifact),
                        str(snapshot),
                    ]
                )
            finally:
                os.umask(previous_umask)
            if encryption.returncode != 0 or not temporary_artifact.is_file():
                raise OperationsError("age encryption failed; no backup was published")
            set_file_permissions(temporary_artifact)
            os.replace(temporary_artifact, artifact)
            set_file_permissions(artifact)

        manifest_data = {
            "backup_format_version": BACKUP_FORMAT_VERSION,
            "backup_timestamp_utc": timestamp,
            "encrypted_artifact": artifact.name,
            "encrypted_size_bytes": artifact.stat().st_size,
            "encrypted_sha256": sha256_file(artifact),
            "foreign_key_check": "ok",
            "latest_schema_migration": verification.latest_migration,
            "migration_versions": list(verification.migration_versions),
            "source_integrity_check": "ok",
        }
        manifest_bytes = (json.dumps(manifest_data, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        descriptor = os.open(
            temporary_manifest,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "wb") as manifest_file:
            manifest_file.write(manifest_bytes)
        set_file_permissions(temporary_manifest)
        os.replace(temporary_manifest, manifest)
        set_file_permissions(manifest)
        deleted_artifacts = apply_retention(backup_directory, keep)
    except OperationsError:
        temporary_artifact.unlink(missing_ok=True)
        temporary_manifest.unlink(missing_ok=True)
        if artifact.exists() and not manifest.exists():
            artifact.unlink()
        raise
    except OSError as error:
        temporary_artifact.unlink(missing_ok=True)
        temporary_manifest.unlink(missing_ok=True)
        if artifact.exists() and not manifest.exists():
            artifact.unlink()
        raise OperationsError("backup filesystem operation failed") from error

    return BackupResult(
        artifact=artifact,
        manifest=manifest,
        latest_migration=verification.latest_migration,
        deleted_artifacts=deleted_artifacts,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an integrity-checked, age-encrypted FARIA SQLite backup."
    )
    parser.add_argument("--source", help="Source SQLite database path.")
    parser.add_argument("--backup-dir", help="Existing external backup directory.")
    parser.add_argument("--recipient", help="Public age recipient used for encryption.")
    parser.add_argument("--keep", type=int, default=14, help="Number of backups to retain.")
    parser.add_argument("--age-command", default="age", help=argparse.SUPPRESS)
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        result = create_backup(
            resolve_database_path(arguments.source),
            resolve_backup_directory(arguments.backup_dir),
            resolve_recipient(arguments.recipient),
            keep=arguments.keep,
            age_command=arguments.age_command,
        )
    except OperationsError as error:
        print(f"FAIL: {error}")
        return 1

    print(f"PASS: encrypted backup created: {result.artifact.name}")
    print(f"PASS: SQLite integrity and migration {result.latest_migration} verified")
    print(f"PASS: retention keeps the latest {arguments.keep} FARIA backups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
