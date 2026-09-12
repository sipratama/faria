from __future__ import annotations

import hashlib
import os
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from faria_household_mcp.allocation import (
    AllocationConflictError,
    AllocationItemInput,
    AllocationItemView,
    AllocationNotFoundError,
    AllocationView,
    InvalidAllocationStateError,
    PeriodAllocationView,
)


class MigrationError(RuntimeError):
    """Raised when the migration history cannot be applied safely."""


def default_database_path() -> Path:
    configured = os.environ.get("FARIA_DB_PATH")
    if configured:
        return Path(configured).expanduser()
    return Path("~/.faria/data/faria.db").expanduser()


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _migration_directory() -> Path:
    package_migrations = Path(__file__).resolve().parent / "migrations"
    if package_migrations.is_dir():
        return package_migrations
    return Path(__file__).resolve().parents[2] / "migrations"


def _split_sql_script(script: str) -> Iterator[str]:
    statement_lines: list[str] = []
    for line in script.splitlines():
        statement_lines.append(line)
        candidate = "\n".join(statement_lines).strip()
        if candidate and sqlite3.complete_statement(candidate):
            yield candidate
            statement_lines.clear()

    if "\n".join(statement_lines).strip():
        raise MigrationError("migration contains an incomplete SQL statement")


class HouseholdDatabase:
    """SQLite persistence owned exclusively by the FARIA Household MCP."""

    def __init__(self, path: str | Path | None = None, migrations: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_database_path()
        self._migrations = Path(migrations) if migrations is not None else _migration_directory()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        connection = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        os.chmod(self.path, 0o600)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        migration_files = sorted(self._migrations.glob("[0-9][0-9][0-9]_*.sql"))
        if not migration_files:
            raise MigrationError(f"no migrations found in {self._migrations}")

        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    checksum TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                )
                """
            )

            for migration_file in migration_files:
                version = migration_file.name.split("_", 1)[0]
                script = migration_file.read_text(encoding="utf-8")
                checksum = hashlib.sha256(script.encode("utf-8")).hexdigest()
                applied = connection.execute(
                    "SELECT checksum FROM schema_migrations WHERE version = ?",
                    (version,),
                ).fetchone()
                if applied is not None:
                    if applied["checksum"] != checksum:
                        raise MigrationError(f"applied migration {version} has changed")
                    continue

                connection.execute("BEGIN IMMEDIATE")
                try:
                    for statement in _split_sql_script(script):
                        connection.execute(statement)
                    connection.execute(
                        "INSERT INTO schema_migrations (version, checksum, applied_at) VALUES (?, ?, ?)",
                        (version, checksum, utc_now()),
                    )
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise

            rules_table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'household_financial_rules'"
            ).fetchone()
            if rules_table_exists is not None:
                now = utc_now()
                connection.execute(
                    """
                    INSERT OR IGNORE INTO household_financial_rules (
                        id, zakat_basis, zakat_rate_basis_points, sedekah_mode,
                        savings_mode, remainder_policy, created_at, updated_at
                    ) VALUES (1, 'THP', 250, 'MANUAL', 'GOAL_BASED',
                              'ASK_ALLOW_UNALLOCATED', ?, ?)
                    """,
                    (now, now),
                )

            persona_state_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'agent_persona_state'"
            ).fetchone()
            if persona_state_exists is not None:
                now = utc_now()
                connection.executemany(
                    """
                    INSERT OR IGNORE INTO agent_persona_state (
                        persona, status, current_task, last_activity_at,
                        last_error_summary, updated_at
                    ) VALUES (?, 'IDLE', NULL, NULL, NULL, ?)
                    """,
                    (("FINANCE", now), ("GIVING", now)),
                )

    def get_period_state(self, period: str) -> PeriodAllocationView:
        self.initialize()
        with self.connect() as connection:
            confirmed_row = connection.execute(
                """
                SELECT * FROM monthly_allocations
                WHERE period = ? AND status = 'CONFIRMED'
                LIMIT 1
                """,
                (period,),
            ).fetchone()
            draft_row = connection.execute(
                """
                SELECT * FROM monthly_allocations
                WHERE period = ? AND status = 'DRAFT'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (period,),
            ).fetchone()
            return PeriodAllocationView(
                period=period,
                confirmed=self._allocation_from_row(connection, confirmed_row),
                draft=self._allocation_from_row(connection, draft_row),
            )

    def save_draft(
        self,
        period: str,
        income_idr: int,
        items: Sequence[AllocationItemInput],
    ) -> AllocationView:
        self.initialize()
        now = utc_now()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT id FROM monthly_allocations WHERE period = ? AND status = 'DRAFT' LIMIT 1",
                    (period,),
                ).fetchone()
                if row is None:
                    allocation_id = str(uuid4())
                    connection.execute(
                        """
                        INSERT INTO monthly_allocations (
                            id, period, income_idr, status, created_at, updated_at,
                            confirmed_at, confirmation_reference
                        ) VALUES (?, ?, ?, 'DRAFT', ?, ?, NULL, NULL)
                        """,
                        (allocation_id, period, income_idr, now, now),
                    )
                else:
                    allocation_id = row["id"]
                    connection.execute(
                        """
                        UPDATE monthly_allocations
                        SET income_idr = ?, updated_at = ?
                        WHERE id = ? AND status = 'DRAFT'
                        """,
                        (income_idr, now, allocation_id),
                    )
                    connection.execute(
                        "DELETE FROM allocation_items WHERE allocation_id = ?",
                        (allocation_id,),
                    )

                for position, item in enumerate(items):
                    connection.execute(
                        """
                        INSERT INTO allocation_items (
                            id, allocation_id, position, category, label, amount_idr
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(uuid4()),
                            allocation_id,
                            position,
                            item.category,
                            item.label,
                            item.amount_idr,
                        ),
                    )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

            allocation_row = connection.execute(
                "SELECT * FROM monthly_allocations WHERE id = ?",
                (allocation_id,),
            ).fetchone()
            allocation = self._allocation_from_row(connection, allocation_row)
            assert allocation is not None
            return allocation

    def confirm(self, allocation_id: str, confirmation_reference: str | None) -> AllocationView:
        self.initialize()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT * FROM monthly_allocations WHERE id = ?",
                    (allocation_id,),
                ).fetchone()
                if row is None:
                    raise AllocationNotFoundError(f"allocation {allocation_id} was not found")
                if row["status"] == "CONFIRMED":
                    connection.commit()
                    allocation = self._allocation_from_row(connection, row)
                    assert allocation is not None
                    return allocation
                if row["status"] != "DRAFT":
                    raise InvalidAllocationStateError(
                        f"allocation {allocation_id} is {row['status']} and cannot be confirmed"
                    )

                conflict = connection.execute(
                    """
                    SELECT id FROM monthly_allocations
                    WHERE period = ? AND status = 'CONFIRMED' AND id <> ?
                    LIMIT 1
                    """,
                    (row["period"], allocation_id),
                ).fetchone()
                if conflict is not None:
                    raise AllocationConflictError(
                        f"period {row['period']} already has a confirmed allocation"
                    )

                now = utc_now()
                connection.execute(
                    """
                    UPDATE monthly_allocations
                    SET status = 'CONFIRMED', confirmed_at = ?, confirmation_reference = ?, updated_at = ?
                    WHERE id = ? AND status = 'DRAFT'
                    """,
                    (now, confirmation_reference, now, allocation_id),
                )
                connection.commit()
            except sqlite3.IntegrityError as error:
                connection.rollback()
                raise AllocationConflictError(
                    f"period {row['period']} already has a confirmed allocation"
                ) from error
            except Exception:
                connection.rollback()
                raise

            confirmed_row = connection.execute(
                "SELECT * FROM monthly_allocations WHERE id = ?",
                (allocation_id,),
            ).fetchone()
            allocation = self._allocation_from_row(connection, confirmed_row)
            assert allocation is not None
            return allocation

    def discard_draft(self, allocation_id: str) -> AllocationView:
        self.initialize()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT * FROM monthly_allocations WHERE id = ?",
                    (allocation_id,),
                ).fetchone()
                if row is None:
                    raise AllocationNotFoundError(f"allocation {allocation_id} was not found")
                if row["status"] != "DRAFT":
                    raise InvalidAllocationStateError(
                        f"allocation {allocation_id} is {row['status']} and cannot be discarded"
                    )

                now = utc_now()
                connection.execute(
                    """
                    UPDATE monthly_allocations
                    SET status = 'DISCARDED', updated_at = ?
                    WHERE id = ? AND status = 'DRAFT'
                    """,
                    (now, allocation_id),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

            discarded_row = connection.execute(
                "SELECT * FROM monthly_allocations WHERE id = ?",
                (allocation_id,),
            ).fetchone()
            allocation = self._allocation_from_row(connection, discarded_row)
            assert allocation is not None
            return allocation

    @staticmethod
    def _allocation_from_row(
        connection: sqlite3.Connection,
        row: sqlite3.Row | None,
    ) -> AllocationView | None:
        if row is None:
            return None
        item_rows = connection.execute(
            """
            SELECT category, label, amount_idr
            FROM allocation_items
            WHERE allocation_id = ?
            ORDER BY position
            """,
            (row["id"],),
        ).fetchall()
        items = tuple(
            AllocationItemView(
                category=item["category"],
                label=item["label"],
                amount_idr=item["amount_idr"],
            )
            for item in item_rows
        )
        allocated_total = sum(item.amount_idr for item in items)
        return AllocationView(
            allocation_id=row["id"],
            period=row["period"],
            income_idr=row["income_idr"],
            status=row["status"],
            items=items,
            allocated_total_idr=allocated_total,
            remainder_idr=row["income_idr"] - allocated_total,
            authoritative=row["status"] == "CONFIRMED",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            confirmed_at=row["confirmed_at"],
            confirmation_reference=row["confirmation_reference"],
        )
