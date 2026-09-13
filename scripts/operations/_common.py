from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


BACKUP_FORMAT_VERSION = 1
BACKUP_FILENAME_RE = re.compile(r"^faria-[0-9]{8}T[0-9]{6}Z\.sqlite\.age$")
DEFAULT_DATABASE_PATH = Path("~/.faria/data/faria.db").expanduser()
EXPECTED_TABLES_BY_MIGRATION = {
    "001": frozenset(
        {
            "allocation_items",
            "monthly_allocations",
            "schema_migrations",
        }
    ),
    "002": frozenset(
        {
            "giving_records",
            "household_financial_rules",
            "savings_contributions",
            "savings_goals",
        }
    ),
    "003": frozenset(
        {
            "agent_activities",
            "agent_persona_state",
        }
    ),
    "004": frozenset({"household_routines"}),
}


class OperationsError(RuntimeError):
    """Raised when a backup or restore verification cannot complete safely."""


@dataclass(frozen=True)
class SQLiteVerification:
    latest_migration: str
    migration_versions: tuple[str, ...]
    table_names: frozenset[str]


def resolve_database_path(explicit: str | Path | None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser()
    configured = os.environ.get("FARIA_DB_PATH")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_DATABASE_PATH


def resolve_backup_directory(explicit: str | Path | None) -> Path:
    value = explicit or os.environ.get("FARIA_BACKUP_DIR")
    if value is None:
        raise OperationsError("backup directory is required via --backup-dir or FARIA_BACKUP_DIR")
    return Path(value).expanduser()


def resolve_recipient(explicit: str | None) -> str:
    value = explicit or os.environ.get("FARIA_BACKUP_RECIPIENT")
    if value is None or not value.strip():
        raise OperationsError(
            "age recipient is required via --recipient or FARIA_BACKUP_RECIPIENT"
        )
    return value.strip()


def resolve_identity(explicit: str | Path | None) -> str:
    value = explicit or os.environ.get("FARIA_BACKUP_IDENTITY")
    if value is None or not str(value).strip():
        raise OperationsError(
            "age identity is required via --identity or FARIA_BACKUP_IDENTITY"
        )
    return str(Path(value).expanduser())


def set_directory_permissions(path: Path) -> None:
    if os.name == "posix":
        path.chmod(0o700)


def set_file_permissions(path: Path) -> None:
    if os.name == "posix":
        path.chmod(0o600)


def sqlite_readonly_uri(path: Path) -> str:
    return f"file:{quote(str(path.resolve()))}?mode=ro"


def verify_sqlite_database(path: Path) -> SQLiteVerification:
    if not path.is_file():
        raise OperationsError("SQLite database file does not exist")

    try:
        with sqlite3.connect(sqlite_readonly_uri(path), uri=True, timeout=5.0) as connection:
            connection.execute("PRAGMA query_only = ON")
            integrity_rows = connection.execute("PRAGMA integrity_check").fetchall()
            if integrity_rows != [("ok",)]:
                raise OperationsError("SQLite integrity_check did not return ok")

            foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_rows:
                raise OperationsError("SQLite foreign_key_check reported violations")

            table_names = frozenset(
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            )
            migration_rows = connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).fetchall()
    except sqlite3.Error as error:
        raise OperationsError("SQLite database could not be verified") from error

    migration_versions = tuple(str(row[0]) for row in migration_rows)
    if not migration_versions:
        raise OperationsError("SQLite migration metadata is empty")

    known_versions = tuple(EXPECTED_TABLES_BY_MIGRATION)
    applied_known_versions = tuple(
        version for version in migration_versions if version in EXPECTED_TABLES_BY_MIGRATION
    )
    if not applied_known_versions:
        raise OperationsError("SQLite migration metadata has no recognized FARIA migration")
    latest_known_index = known_versions.index(applied_known_versions[-1])
    expected_known_versions = known_versions[: latest_known_index + 1]
    if applied_known_versions != expected_known_versions:
        raise OperationsError("SQLite migration metadata has an invalid FARIA sequence")

    required_tables = frozenset().union(
        *(
            tables
            for version, tables in EXPECTED_TABLES_BY_MIGRATION.items()
            if version in migration_versions
        )
    )
    missing_tables = required_tables - table_names
    if missing_tables:
        raise OperationsError("SQLite database is missing required FARIA tables")

    return SQLiteVerification(
        latest_migration=migration_versions[-1],
        migration_versions=migration_versions,
        table_names=table_names,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, object] | None:
    manifest_path = path.with_name(f"{path.name}.json")
    if not manifest_path.is_file():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise OperationsError("backup manifest is unreadable") from error
    if not isinstance(data, dict):
        raise OperationsError("backup manifest has an invalid structure")
    return data
