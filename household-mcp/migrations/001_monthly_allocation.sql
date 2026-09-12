CREATE TABLE monthly_allocations (
    id TEXT PRIMARY KEY,
    period TEXT NOT NULL,
    income_idr INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confirmed_at TEXT,
    confirmation_reference TEXT,
    CONSTRAINT monthly_allocations_period_format CHECK (
        length(period) = 7
        AND period GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        AND substr(period, 6, 2) BETWEEN '01' AND '12'
    ),
    CONSTRAINT monthly_allocations_income_positive CHECK (
        typeof(income_idr) = 'integer' AND income_idr > 0
    ),
    CONSTRAINT monthly_allocations_status_valid CHECK (
        status IN ('DRAFT', 'CONFIRMED', 'DISCARDED')
    ),
    CONSTRAINT monthly_allocations_confirmation_state_valid CHECK (
        (status = 'CONFIRMED' AND confirmed_at IS NOT NULL)
        OR
        (status IN ('DRAFT', 'DISCARDED') AND confirmed_at IS NULL AND confirmation_reference IS NULL)
    )
);

CREATE TABLE allocation_items (
    id TEXT PRIMARY KEY,
    allocation_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    category TEXT NOT NULL,
    label TEXT,
    amount_idr INTEGER NOT NULL,
    CONSTRAINT allocation_items_allocation_fk
        FOREIGN KEY (allocation_id) REFERENCES monthly_allocations(id) ON DELETE CASCADE,
    CONSTRAINT allocation_items_position_unique UNIQUE (allocation_id, position),
    CONSTRAINT allocation_items_position_non_negative CHECK (position >= 0),
    CONSTRAINT allocation_items_category_valid CHECK (
        category IN (
            'zakat',
            'sedekah',
            'savings',
            'household_budget',
            'personal_allowance',
            'buffer'
        )
    ),
    CONSTRAINT allocation_items_label_valid CHECK (
        label IS NULL OR length(trim(label)) > 0
    ),
    CONSTRAINT allocation_items_amount_non_negative CHECK (
        typeof(amount_idr) = 'integer' AND amount_idr >= 0
    )
);

CREATE UNIQUE INDEX monthly_allocations_one_confirmed_per_period
    ON monthly_allocations(period)
    WHERE status = 'CONFIRMED';

CREATE UNIQUE INDEX monthly_allocations_one_active_draft_per_period
    ON monthly_allocations(period)
    WHERE status = 'DRAFT';

CREATE INDEX monthly_allocations_period_status
    ON monthly_allocations(period, status);

CREATE INDEX allocation_items_allocation
    ON allocation_items(allocation_id, position);
