ALTER TABLE agent_persona_state RENAME TO agent_persona_state_rf05;

CREATE TABLE agent_persona_state (
    persona TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    current_task TEXT,
    last_activity_at TEXT,
    last_error_summary TEXT,
    updated_at TEXT NOT NULL,
    CONSTRAINT agent_persona_state_persona_valid CHECK (
        persona IN ('FINANCE', 'GIVING', 'HOME_OPS')
    ),
    CONSTRAINT agent_persona_state_status_valid CHECK (
        status IN ('IDLE', 'WORKING', 'ERROR')
    ),
    CONSTRAINT agent_persona_state_task_valid CHECK (
        current_task IS NULL
        OR (length(trim(current_task)) > 0 AND length(current_task) <= 160)
    ),
    CONSTRAINT agent_persona_state_error_valid CHECK (
        last_error_summary IS NULL
        OR (
            length(trim(last_error_summary)) > 0
            AND length(last_error_summary) <= 160
        )
    ),
    CONSTRAINT agent_persona_state_working_task_valid CHECK (
        (status = 'WORKING' AND current_task IS NOT NULL)
        OR (status IN ('IDLE', 'ERROR') AND current_task IS NULL)
    )
);

INSERT INTO agent_persona_state (
    persona, status, current_task, last_activity_at, last_error_summary, updated_at
)
SELECT persona, status, current_task, last_activity_at, last_error_summary, updated_at
FROM agent_persona_state_rf05;

DROP TABLE agent_persona_state_rf05;

CREATE TABLE household_routines (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    schedule_kind TEXT NOT NULL,
    schedule_expression TEXT NOT NULL,
    timezone TEXT NOT NULL,
    status TEXT NOT NULL,
    scheduler_job_id TEXT,
    last_completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT household_routines_title_valid CHECK (
        length(trim(title)) > 0 AND length(title) <= 120
    ),
    CONSTRAINT household_routines_description_valid CHECK (
        description IS NULL OR length(description) <= 500
    ),
    CONSTRAINT household_routines_schedule_kind_valid CHECK (
        schedule_kind IN ('ONE_OFF', 'RECURRING')
    ),
    CONSTRAINT household_routines_schedule_expression_valid CHECK (
        length(trim(schedule_expression)) > 0 AND length(schedule_expression) <= 120
    ),
    CONSTRAINT household_routines_timezone_valid CHECK (
        timezone = 'Asia/Jakarta'
    ),
    CONSTRAINT household_routines_status_valid CHECK (
        status IN ('PENDING_SCHEDULE', 'ACTIVE', 'COMPLETED', 'CANCELLED')
    ),
    CONSTRAINT household_routines_scheduler_job_valid CHECK (
        scheduler_job_id IS NULL
        OR (length(trim(scheduler_job_id)) > 0 AND length(scheduler_job_id) <= 160)
    ),
    CONSTRAINT household_routines_active_scheduler_valid CHECK (
        status != 'ACTIVE' OR scheduler_job_id IS NOT NULL
    ),
    CONSTRAINT household_routines_pending_scheduler_valid CHECK (
        status != 'PENDING_SCHEDULE' OR scheduler_job_id IS NULL
    ),
    CONSTRAINT household_routines_completed_kind_valid CHECK (
        status != 'COMPLETED' OR schedule_kind = 'ONE_OFF'
    ),
    CONSTRAINT household_routines_completed_timestamp_valid CHECK (
        status != 'COMPLETED' OR last_completed_at IS NOT NULL
    )
);

CREATE UNIQUE INDEX household_routines_scheduler_job_unique
    ON household_routines(scheduler_job_id)
    WHERE scheduler_job_id IS NOT NULL;

CREATE INDEX household_routines_open_newest
    ON household_routines(status, created_at DESC, id DESC);

CREATE TRIGGER household_routines_no_delete
BEFORE DELETE ON household_routines
BEGIN
    SELECT RAISE(ABORT, 'household routine history cannot be deleted');
END;
