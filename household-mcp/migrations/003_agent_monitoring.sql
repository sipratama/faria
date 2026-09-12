CREATE TABLE agent_activities (
    id TEXT PRIMARY KEY,
    persona TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT NOT NULL,
    reference_type TEXT,
    reference_id TEXT,
    occurred_at TEXT NOT NULL,
    CONSTRAINT agent_activities_persona_valid CHECK (
        persona IN ('FINANCE', 'GIVING', 'HOME_OPS', 'PLANNER')
    ),
    CONSTRAINT agent_activities_type_valid CHECK (
        length(trim(activity_type)) > 0 AND length(activity_type) <= 80
    ),
    CONSTRAINT agent_activities_status_valid CHECK (status IN ('SUCCEEDED', 'FAILED')),
    CONSTRAINT agent_activities_summary_valid CHECK (
        length(trim(summary)) > 0 AND length(summary) <= 160
    ),
    CONSTRAINT agent_activities_reference_pair_valid CHECK (
        (reference_type IS NULL AND reference_id IS NULL)
        OR
        (
            reference_type IS NOT NULL
            AND length(trim(reference_type)) > 0
            AND length(reference_type) <= 80
            AND reference_id IS NOT NULL
            AND length(trim(reference_id)) > 0
            AND length(reference_id) <= 160
        )
    )
);

CREATE INDEX agent_activities_newest
    ON agent_activities(occurred_at DESC, id DESC);

CREATE TRIGGER agent_activities_no_update
BEFORE UPDATE ON agent_activities
BEGIN
    SELECT RAISE(ABORT, 'agent activities are immutable');
END;

CREATE TRIGGER agent_activities_no_delete
BEFORE DELETE ON agent_activities
BEGIN
    SELECT RAISE(ABORT, 'agent activities are immutable');
END;

CREATE TABLE agent_persona_state (
    persona TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    current_task TEXT,
    last_activity_at TEXT,
    last_error_summary TEXT,
    updated_at TEXT NOT NULL,
    CONSTRAINT agent_persona_state_persona_valid CHECK (
        persona IN ('FINANCE', 'GIVING')
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
