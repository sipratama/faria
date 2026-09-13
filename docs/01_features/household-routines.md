# Household Routines & Reminders

> **Capability:** `CAP-ROUTINE-001`  
> **Status:** Implemented locally in RF-06  
> **Primary Interface:** allowlisted Telegram conversation through FARIA Home Ops

## 1. Purpose and Scope

FARIA lets the household create, inspect, complete, and cancel precise household reminders without becoming a general automation platform. `HouseholdRoutine` in SQLite is authoritative household intent. Hermes Cron schedules and delivers reminders but is never the routine database.

RF-06 supports one-off reminders, five-field recurring schedules, listing/detail, completion, cancellation, Telegram delivery, and read-only dashboard visibility. It excludes payments, email/push notifications, location triggers, external calendars, dependency graphs, project planning, and system/coding automation.

## 2. Actors and Preconditions

- Only a Telegram identity already authorized by the explicit Hermes allowlist may interact.
- FARIA loads `agent/skills/faria-home-ops/SKILL.md` for routine/reminder intents.
- Conversational time is normalized to a canonical schedule before Household MCP is called.
- Household timezone is `Asia/Jakarta`.
- A direct, unambiguous creation command with a precise schedule is sufficient creation intent; cancellation requires explicit, object-specific confirmation.

## 3. Functional Requirements

### FR-ROUTINE-001 — Create One-Off Routine

**Requirement**
From a direct creation command with a precise future date/time, FARIA creates a `ONE_OFF` routine using an offset-aware ISO timestamp for the intended Jakarta time without requiring a second confirmation turn.

**Acceptance Criteria**
- Household MCP receives no vague natural-language schedule.
- New state is `PENDING_SCHEDULE` with no scheduler job ID.
- FARIA does not report the reminder active until scheduler linking succeeds.

### FR-ROUTINE-002 — Create Recurring Routine

**Requirement**
From a direct creation command with a precise recurrence, FARIA creates a `RECURRING` routine using a deterministic five-field cron expression without requiring a second confirmation turn.

**Acceptance Criteria**
- Invalid, extended, or ambiguous schedules are rejected or clarified before persistence.
- A recurring schedule has a calculable next occurrence in `Asia/Jakarta`.
- Missing time is never silently replaced with a default.

### FR-ROUTINE-003 — Direct Creation Intent and Acknowledgement Safety

**Requirement**
A direct, unambiguous reminder/routine creation command is sufficient intent when the title/purpose, schedule, and timezone are safely resolved. FARIA asks clarification instead of inventing missing schedule values. Generic acknowledgements are not standalone creation commands and cannot replay a completed creation saga.

**Acceptance Criteria**
- `Ingatkan saya 3 menit lagi untuk cek galon` may proceed directly through creation, cron creation, scheduler linking, and `ACTIVE`.
- `Ingatkan service AC setiap 3 bulan tanggal 1 jam 09:00` may proceed directly as a recurring routine.
- Vague or incomplete schedules require clarification before any routine or cron mutation.
- `oke`, `sip`, `mantap`, `lanjut`, emoji, silence, or generic affirmation alone does not create a routine.
- A generic acknowledgement after successful creation does not repeat `routine_create`, cron creation, or `routine_scheduler_link`.
- Existing financial confirmation behavior is unchanged.

### FR-ROUTINE-004 — List / Retrieve Routines

**Requirement**
FARIA lists open routines and retrieves details from Household MCP authoritative state using deterministic exact/case-insensitive/unique-normalized matching.

**Acceptance Criteria**
- `PENDING_SCHEDULE` is visible as requiring scheduling attention.
- Active listing excludes completed and cancelled history unless explicitly requested.
- Ambiguous matches require clarification; embeddings are not used.

### FR-ROUTINE-005 — Deliver Reminder Through Telegram

**Requirement**
Hermes Cron delivers a concise Indonesian reminder to the origin conversation in a fresh session using a self-contained prompt and the Home Ops skill.

**Acceptance Criteria**
- The cron execution reads the routine through the read-only `routine_get` surface.
- Only `ACTIVE` authoritative state produces a normal reminder.
- Non-active state produces only `[SILENT]`.

### FR-ROUTINE-006 — Complete Routine

**Requirement**
A clear completion statement may complete exactly one matching active routine without an extra confirmation turn.

**Acceptance Criteria**
- `ONE_OFF` transitions `ACTIVE → COMPLETED` and records `last_completed_at`.
- `RECURRING` records `last_completed_at` while remaining `ACTIVE`.
- Recurring completion does not remove its cron schedule.

### FR-ROUTINE-007 — Cancel Routine

**Requirement**
FARIA explains the future-delivery consequence and obtains explicit cancellation confirmation before authoritative cancellation.

**Acceptance Criteria**
- `PENDING_SCHEDULE` and `ACTIVE` may transition to `CANCELLED`.
- Cancellation is authoritative before best-effort scheduler cleanup.
- Cleanup failure never rolls state back to `ACTIVE`.
- Routine history is not hard-deleted.

### FR-ROUTINE-008 — Scheduler Reconciliation Safety

**Requirement**
Scheduler state is operational metadata. Missing or orphaned jobs are treated as reconciliation problems rather than evidence that the routine does not exist.

**Acceptance Criteria**
- Scheduler linking is an atomic `PENDING_SCHEDULE → ACTIVE` transition.
- Repeating the same scheduler link is idempotent; a conflicting job ID is rejected.
- If cron creation fails, the routine remains inspectable as `PENDING_SCHEDULE`.
- Every run re-checks authoritative state, so a cancelled/completed/pending orphan is silent.

### FR-ROUTINE-009 — Dashboard Home Ops Reflection

**Requirement**
The read-only dashboard activates Home Ops and projects its persona state, active routine count, next active routine, and relevant persisted activity from SQLite-derived state.

**Acceptance Criteria**
- The dashboard does not read Hermes cron files or shell out to Hermes.
- Cancelled/completed routines are excluded from next task.
- Planner remains `NOT_ACTIVATED`.
- No routine mutation controls or HTTP mutation routes are added.

### FR-ROUTINE-010 — Household Timezone

**Requirement**
Conversational interpretation, cron scheduling, displayed times, and derived recurring next occurrences use `Asia/Jakarta` explicitly.

**Acceptance Criteria**
- Wrong timezone values are rejected by Household MCP.
- One-off timestamps carry Jakarta's offset.
- Tests use fixed clocks and explicit timezone data.

## 4. Business Rules

| ID | Rule |
|---|---|
| BR-ROUTINE-01 | SQLite/Household MCP owns routine state; Hermes Cron owns scheduling and delivery. |
| BR-ROUTINE-02 | Routine UUID is stable; `scheduler_job_id` is operational metadata only. |
| BR-ROUTINE-03 | Direct, unambiguous creation intent may proceed without a second confirmation turn; cancellation remains explicitly confirmed. |
| BR-ROUTINE-04 | Completion affects one occurrence; recurring completion does not terminate recurrence. |
| BR-ROUTINE-05 | Cancellation is authoritative even when scheduler cleanup fails. |
| BR-ROUTINE-06 | Cron prompts contain no credentials, Telegram IDs, financial data, or private paths. |

## 5. Lifecycle

```text
PENDING_SCHEDULE → ACTIVE → COMPLETED   (ONE_OFF)
PENDING_SCHEDULE → ACTIVE               (RECURRING occurrence completion keeps ACTIVE)
PENDING_SCHEDULE → CANCELLED
ACTIVE → CANCELLED
```

There is no hard delete tool. `SNOOZE` is deferred after RF-06.

## 6. Failure States

| State | Required Behavior |
|---|---|
| Ambiguous or incomplete schedule | Ask for the exact date/time/recurrence; do not persist or create cron state. |
| Generic acknowledgement | Acknowledge harmlessly; do not create, replay, duplicate, or cancel a routine. |
| Ambiguous cancellation confirmation | Restate the identified object/action; do not cancel. |
| Cron creation failure | Keep `PENDING_SCHEDULE`; report scheduling failure. |
| Scheduler link failure | Best-effort remove the new job; keep routine recoverable. |
| Cron removal failure after cancellation | Keep `CANCELLED`; stale run returns `[SILENT]`. |
| Multiple matching routines | Ask which routine; do not mutate. |
| Out-of-scope scheduled request | Refuse and create no cron job. |

## 7. Minimum Regression Coverage

- Migration `001 → 002 → 003 → 004` with existing finance/monitoring data preserved.
- Input validation, five-field cron validation, Jakarta timezone, and fixed-clock due calculation.
- One-off and recurring lifecycle, idempotent scheduler link, conflicting link rejection, cancellation, and no hard deletion.
- Skill evidence for direct one-off/recurring creation, schedule clarification, acknowledgement replay safety, explicit cancellation, completion, finance isolation, and general-automation refusal.
- Dashboard active/empty/cancelled states with Home Ops active and Planner inactive.

## 8. Deferred

- SNOOZE.
- Edit/reschedule flow.
- Automatic reconciliation daemon.
- Planner capability.
- External calendar integration.
- Notification channels other than existing Telegram.

## 9. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 1.1 | `2026-09-13` | Aligned direct creation intent, acknowledgement replay safety, and stricter cancellation policy in RF-06B | sipratama |
| 1.0 | `2026-09-12` | Added RF-06 authoritative routine/reminder behavior | sipratama |
