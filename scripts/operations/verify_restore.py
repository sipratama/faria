from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

try:
    from ._common import (
        OperationsError,
        load_manifest,
        resolve_identity,
        set_directory_permissions,
        set_file_permissions,
        sha256_file,
        verify_sqlite_database,
    )
except ImportError:
    from _common import (  # type: ignore[no-redef]
        OperationsError,
        load_manifest,
        resolve_identity,
        set_directory_permissions,
        set_file_permissions,
        sha256_file,
        verify_sqlite_database,
    )


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
CommandLocator = Callable[[str], str | None]


@dataclass(frozen=True)
class RestoreVerificationResult:
    latest_migration: str
    migration_versions: tuple[str, ...]


def run_command(arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(arguments),
        capture_output=True,
        check=False,
        text=True,
    )


def verify_encrypted_backup(
    artifact: Path,
    identity: str,
    *,
    age_command: str = "age",
    runner: CommandRunner = run_command,
    locator: CommandLocator = shutil.which,
    staging_root: Path | None = None,
) -> RestoreVerificationResult:
    artifact = artifact.expanduser()
    if not artifact.is_file():
        raise OperationsError("encrypted backup artifact does not exist")
    if locator(age_command) is None:
        raise OperationsError("age is not available; install age and re-run verification")

    manifest = load_manifest(artifact)
    if manifest is not None:
        if manifest.get("backup_format_version") != 1:
            raise OperationsError("backup manifest format version is unsupported")
        if manifest.get("encrypted_artifact") != artifact.name:
            raise OperationsError("backup manifest does not identify this artifact")
        expected_digest = manifest.get("encrypted_sha256")
        if not isinstance(expected_digest, str) or sha256_file(artifact) != expected_digest:
            raise OperationsError("encrypted backup checksum does not match its manifest")

    try:
        with tempfile.TemporaryDirectory(
            prefix="faria-restore-",
            dir=staging_root,
        ) as temporary_directory:
            staging_directory = Path(temporary_directory)
            set_directory_permissions(staging_directory)
            restored_database = staging_directory / "faria-restored.sqlite"
            decryption = runner(
                [
                    age_command,
                    "--decrypt",
                    "--identity",
                    identity,
                    "--output",
                    str(restored_database),
                    str(artifact),
                ]
            )
            if decryption.returncode != 0 or not restored_database.is_file():
                raise OperationsError("age decryption failed; backup could not be verified")
            set_file_permissions(restored_database)
            verification = verify_sqlite_database(restored_database)

            if manifest is not None:
                expected_migration = manifest.get("latest_schema_migration")
                if expected_migration != verification.latest_migration:
                    raise OperationsError(
                        "restored migration metadata does not match the manifest"
                    )
    except OperationsError:
        raise
    except OSError as error:
        raise OperationsError("restore temporary storage operation failed") from error

    return RestoreVerificationResult(
        latest_migration=verification.latest_migration,
        migration_versions=verification.migration_versions,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decrypt and verify a FARIA backup without replacing the live database."
    )
    parser.add_argument("backup", help="Encrypted FARIA .sqlite.age artifact.")
    parser.add_argument("--identity", help="Path to the operator-owned age identity.")
    parser.add_argument("--age-command", default="age", help=argparse.SUPPRESS)
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        result = verify_encrypted_backup(
            Path(arguments.backup),
            resolve_identity(arguments.identity),
            age_command=arguments.age_command,
        )
    except OperationsError as error:
        print(f"FAIL: {error}")
        return 1

    print("PASS: encrypted backup decrypted in temporary storage")
    print("PASS: SQLite integrity_check and foreign_key_check succeeded")
    print(f"PASS: migration metadata readable through {result.latest_migration}")
    print("PASS: temporary plaintext restore material removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
