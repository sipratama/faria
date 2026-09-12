CREATE TABLE household_financial_rules (
    id INTEGER PRIMARY KEY,
    zakat_basis TEXT NOT NULL,
    zakat_rate_basis_points INTEGER NOT NULL,
    sedekah_mode TEXT NOT NULL,
    savings_mode TEXT NOT NULL,
    remainder_policy TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT household_financial_rules_singleton CHECK (id = 1),
    CONSTRAINT household_financial_rules_zakat_basis_valid CHECK (zakat_basis = 'THP'),
    CONSTRAINT household_financial_rules_zakat_rate_valid CHECK (
        typeof(zakat_rate_basis_points) = 'integer'
        AND zakat_rate_basis_points > 0
    ),
    CONSTRAINT household_financial_rules_sedekah_mode_valid CHECK (sedekah_mode = 'MANUAL'),
    CONSTRAINT household_financial_rules_savings_mode_valid CHECK (savings_mode = 'GOAL_BASED'),
    CONSTRAINT household_financial_rules_remainder_policy_valid CHECK (
        remainder_policy = 'ASK_ALLOW_UNALLOCATED'
    )
);

INSERT OR IGNORE INTO household_financial_rules (
    id,
    zakat_basis,
    zakat_rate_basis_points,
    sedekah_mode,
    savings_mode,
    remainder_policy,
    created_at,
    updated_at
) VALUES (
    1,
    'THP',
    250,
    'MANUAL',
    'GOAL_BASED',
    'ASK_ALLOW_UNALLOCATED',
    strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
    strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
);

CREATE TABLE savings_goals (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    target_amount_idr INTEGER NOT NULL,
    target_date TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT savings_goals_name_valid CHECK (length(trim(name)) > 0),
    CONSTRAINT savings_goals_description_valid CHECK (
        description IS NULL OR length(trim(description)) > 0
    ),
    CONSTRAINT savings_goals_target_positive CHECK (
        typeof(target_amount_idr) = 'integer' AND target_amount_idr > 0
    ),
    CONSTRAINT savings_goals_target_date_format CHECK (
        target_date IS NULL
        OR (
            length(target_date) = 10
            AND target_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        )
    ),
    CONSTRAINT savings_goals_status_valid CHECK (
        status IN ('ACTIVE', 'COMPLETED', 'ARCHIVED')
    )
);

CREATE UNIQUE INDEX savings_goals_non_archived_name_unique
    ON savings_goals(lower(name))
    WHERE status <> 'ARCHIVED';

CREATE INDEX savings_goals_status_created
    ON savings_goals(status, created_at, id);

CREATE TABLE savings_contributions (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    amount_idr INTEGER NOT NULL,
    recorded_at TEXT NOT NULL,
    source_allocation_reference TEXT,
    note TEXT,
    CONSTRAINT savings_contributions_goal_fk
        FOREIGN KEY (goal_id) REFERENCES savings_goals(id),
    CONSTRAINT savings_contributions_allocation_fk
        FOREIGN KEY (source_allocation_reference) REFERENCES monthly_allocations(id),
    CONSTRAINT savings_contributions_amount_positive CHECK (
        typeof(amount_idr) = 'integer' AND amount_idr > 0
    ),
    CONSTRAINT savings_contributions_reference_valid CHECK (
        source_allocation_reference IS NULL
        OR length(trim(source_allocation_reference)) > 0
    ),
    CONSTRAINT savings_contributions_note_valid CHECK (
        note IS NULL OR length(trim(note)) > 0
    )
);

CREATE UNIQUE INDEX savings_contributions_linked_retry_unique
    ON savings_contributions(goal_id, source_allocation_reference)
    WHERE source_allocation_reference IS NOT NULL;

CREATE INDEX savings_contributions_goal_recorded
    ON savings_contributions(goal_id, recorded_at, id);

CREATE TRIGGER savings_contributions_no_update
BEFORE UPDATE ON savings_contributions
BEGIN
    SELECT RAISE(ABORT, 'savings contributions are immutable');
END;

CREATE TRIGGER savings_contributions_no_delete
BEFORE DELETE ON savings_contributions
BEGIN
    SELECT RAISE(ABORT, 'savings contributions are immutable');
END;

CREATE TABLE giving_records (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    amount_idr INTEGER NOT NULL,
    period TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    monthly_allocation_reference TEXT,
    note TEXT,
    CONSTRAINT giving_records_type_valid CHECK (
        type IN ('zakat_penghasilan', 'sedekah')
    ),
    CONSTRAINT giving_records_amount_positive CHECK (
        typeof(amount_idr) = 'integer' AND amount_idr > 0
    ),
    CONSTRAINT giving_records_period_format CHECK (
        length(period) = 7
        AND period GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        AND substr(period, 6, 2) BETWEEN '01' AND '12'
    ),
    CONSTRAINT giving_records_allocation_fk
        FOREIGN KEY (monthly_allocation_reference) REFERENCES monthly_allocations(id),
    CONSTRAINT giving_records_note_valid CHECK (
        note IS NULL OR length(trim(note)) > 0
    )
);

CREATE UNIQUE INDEX giving_records_linked_retry_unique
    ON giving_records(period, type, monthly_allocation_reference)
    WHERE monthly_allocation_reference IS NOT NULL;

CREATE INDEX giving_records_period_type_recorded
    ON giving_records(period, type, recorded_at, id);

CREATE TRIGGER giving_records_no_update
BEFORE UPDATE ON giving_records
BEGIN
    SELECT RAISE(ABORT, 'giving records are immutable');
END;

CREATE TRIGGER giving_records_no_delete
BEFORE DELETE ON giving_records
BEGIN
    SELECT RAISE(ABORT, 'giving records are immutable');
END;
