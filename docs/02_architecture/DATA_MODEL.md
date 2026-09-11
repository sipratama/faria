# Data Model — FARIA

> **Document role:** Authoritative **human-readable reference** for domain data ownership, core entities, relationships, invariants, lifecycle, and data classification.
>
> The executable source of truth for the physical database schema will be the version-controlled schema/migrations, once they exist. This document must not duplicate every column or migration detail.

---

## Document Metadata

| Field | Value |
|---|---|
| Project | FARIA |
| Status | Draft |
| Version | `0.1` |
| Owner | sipratama |
| Last Updated | `2026-09-11` |

---

## 1. Modeling Principles

- Model business concepts before storage-specific details.
- Give mutable data a clear owning module/domain.
- Avoid shared write ownership.
- Express important invariants explicitly.
- Treat migrations/schema as the physical source of truth once they exist.
- Record sensitive-data classification and lifecycle.
- Do not introduce entities for hypothetical future requirements.

---

## 2. Domain Data Ownership

| Domain / Module | Owned Data | Write Authority | Notes |
|---|---|---|---|
| Household Core | Household, Member | Household MCP | Shared context for both spouses |
| Finance | MonthlyAllocation, AllocationItem | Household MCP | |
| Savings | SavingsGoal, SavingsContribution | Household MCP | |
| Giving | GivingRecord | Household MCP | Zakat penghasilan + sedekah |
| Home Ops | HouseholdRoutine | Household MCP | Reminders/maintenance |
| Agent Monitoring | AgentActivity | Household MCP (ownership TBD, see Open Data Decisions) | Feeds dashboard |

Ownership means the component authorized to define and mutate authoritative state. Hermes skills interact through Household MCP rather than writing owned data directly.

---

## 3. Core Entity Map

```text
Household 1 -------- * Member
    |
    | 1
    |
    * MonthlyAllocation 1 -------- * AllocationItem
    |
    * SavingsGoal 1 -------- * SavingsContribution
    |
    * GivingRecord
    |
    * HouseholdRoutine
    |
    * AgentActivity
```

---

## 4. Entity Catalog

### Household

**Purpose**
Represents the single household using FARIA (V1 supports exactly one).

**Owner**
Household MCP.

**Identity**
Internal identifier (strategy TBD — UUID recommended).

**Lifecycle**
`Created → Active`

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| name | Household display name | Yes | No |
| created_at | Creation timestamp | Yes | No |

**Relationships**
- Has many Member, MonthlyAllocation, SavingsGoal, GivingRecord, HouseholdRoutine, AgentActivity.

**Invariants**
- Exactly one Household exists in V1 (multi-household is explicitly out of scope).

**Deletion / Retention**
Not deleted in normal operation; the household owns its own data.

---

### Member

**Purpose**
Represents a household participant (household owner or spouse).

**Owner**
Household MCP.

**Identity**
Internal identifier + Telegram identity reference.

**Lifecycle**
`Created → Active`

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| display_name | Human-readable name | Yes | No |
| telegram_user_id | Allowlisted Telegram identity | Yes | Yes |
| role | Informational label (not a permission gate in V1) | No | No |

**Relationships**
- Belongs to one Household.

**Invariants**
- Only a Member with an allowlisted `telegram_user_id` may act on behalf of the household (enforced at the application boundary, not only by this record).

**Deletion / Retention**
Not deleted in normal operation.

---

### MonthlyAllocation

**Purpose**
Represents one period's (e.g. calendar month) proposed/confirmed allocation of income.

**Owner**
Household MCP.

**Identity**
Internal identifier; unique per `(household, period)`.

**Lifecycle**
`Draft → Confirmed` or `Draft → Discarded`

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| period | Allocation period (e.g. month/year) | Yes | No |
| income_amount | Recorded monthly income | Yes | Yes |
| status | Draft / Confirmed / Discarded | Yes | No |
| confirmed_at | Confirmation timestamp | No | No |
| confirmed_by | Member who confirmed | No | No |

**Relationships**
- Has many AllocationItem. Belongs to one Household.

**Invariants**
- Only a Confirmed MonthlyAllocation is authoritative for its period (see `docs/01_features/monthly-allocation.md`, BR-01).
- At most one Confirmed MonthlyAllocation per `(household, period)`.

**Deletion / Retention**
Confirmed allocations are not deleted; a Draft may be discarded/superseded.

---

### AllocationItem

**Purpose**
One bucket within a MonthlyAllocation (zakat, sedekah, savings, household budget, personal allowance — per member where applicable).

**Owner**
Household MCP.

**Identity**
Internal identifier.

**Lifecycle**
Tied to parent MonthlyAllocation's lifecycle.

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| category | zakat / sedekah / savings / household_budget / personal_allowance | Yes | No |
| amount | Nominal for this bucket | Yes | Yes |
| member_reference | Member this item applies to (for personal allowances) | No | No |

**Relationships**
- Belongs to one MonthlyAllocation.

**Invariants**
- Amounts are non-negative.
- The sum of AllocationItem amounts plus buffer must not exceed the period's `income_amount`.

**Deletion / Retention**
Tied to parent MonthlyAllocation.

---

### SavingsGoal

**Purpose**
Represents a named savings goal (emergency fund, travel, major purchase, etc.).

**Owner**
Household MCP.

**Identity**
Internal identifier.

**Lifecycle**
`Active → Completed (target reached) → Archived (optional)`

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| name | Goal name | Yes | No |
| target_amount | Target nominal | Yes | Yes |
| current_amount | Current progress | Yes | Yes |
| target_date | Optional target date | No | No |
| recurring_contribution | Optional recurring contribution amount | No | Yes |

**Relationships**
- Has many SavingsContribution. Belongs to one Household.

**Invariants**
- `current_amount` is derived from/consistent with the sum of its SavingsContribution records.

**Deletion / Retention**
Not deleted in normal operation; may be archived once no longer relevant.

---

### SavingsContribution

**Purpose**
One recorded contribution toward a SavingsGoal.

**Owner**
Household MCP.

**Identity**
Internal identifier.

**Lifecycle**
`Created` (immutable once recorded).

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| amount | Contribution amount | Yes | Yes |
| recorded_at | Timestamp | Yes | No |
| source_allocation_reference | Optional link to the MonthlyAllocation it came from | No | No |

**Relationships**
- Belongs to one SavingsGoal.

**Invariants**
- `amount` is positive.

**Deletion / Retention**
Not deleted in normal operation (financial history).

---

### GivingRecord

**Purpose**
Represents a recorded zakat penghasilan or sedekah payment for a period.

**Owner**
Household MCP.

**Identity**
Internal identifier.

**Lifecycle**
`Recorded` (immutable once recorded).

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| type | `zakat_penghasilan` or `sedekah` | Yes | No |
| amount | Nominal amount | Yes | Yes |
| period | Related allocation period | Yes | No |
| recorded_at | Timestamp | Yes | No |

**Relationships**
- Belongs to one Household; may reference the MonthlyAllocation it fulfills.

**Invariants**
- `type` must be one of `zakat_penghasilan` or `sedekah` — they remain distinct records even when both relate to the same period (see Product Brief: Sedekah must remain distinct from Zakat Penghasilan).

**Deletion / Retention**
Not deleted in normal operation.

---

### HouseholdRoutine

**Purpose**
Represents a recurring or one-off household obligation/reminder (e.g. AC maintenance, bill reminder).

**Owner**
Household MCP.

**Identity**
Internal identifier.

**Lifecycle**
`Scheduled → Completed` (recurring: `→ Scheduled` again) or `→ Snoozed`

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| title | Routine description | Yes | No |
| recurrence_rule | Optional recurrence definition | No | No |
| next_due_at | Next due timestamp | Yes | No |
| last_completed_at | Last completion timestamp | No | No |

**Relationships**
- Belongs to one Household.

**Invariants**
- A completed one-off routine does not recreate itself; a recurring routine reschedules `next_due_at` on completion.

**Deletion / Retention**
May be deleted by the household when no longer relevant.

---

### AgentActivity

**Purpose**
Represents a logged activity/status entry for a persona (Finance/Giving/Home Ops/Planner), feeding the dashboard.

**Owner**
Household MCP (ownership between Household MCP and Hermes is TBD — see Open Data Decisions).

**Identity**
Internal identifier.

**Lifecycle**
`Created` (append-only log entry).

**Key Attributes**

| Attribute | Meaning | Required? | Sensitive? |
|---|---|---:|---:|
| persona | Finance / Giving / Home Ops / Planner | Yes | No |
| status | Idle / Working / Scheduled / Error | Yes | No |
| task_description | Human-readable description of the activity | Yes | No |
| occurred_at | Timestamp | Yes | No |
| model_alias | Logical model alias used (e.g. `household-main`) | No | No |

**Relationships**
- Belongs to one Household.

**Invariants**
- Does not itself carry authoritative financial amounts; it references what happened, not authoritative financial values.

**Deletion / Retention**
May be pruned/rotated once the dashboard no longer needs old entries (retention policy TBD).

---

## 5. Aggregates and Transaction Boundaries

| Aggregate | Root | Members | Invariants Requiring Atomicity |
|---|---|---|---|
| MonthlyAllocation | MonthlyAllocation | AllocationItem(s) | Confirming an allocation must atomically persist the allocation and all its items together. |

---

## 6. Relationships

| From | Relationship | To | Cardinality | Ownership Meaning |
|---|---|---|---|---|
| Household | has | Member | 1:N | Lifecycle ownership |
| Household | has | MonthlyAllocation | 1:N | Lifecycle ownership |
| MonthlyAllocation | has | AllocationItem | 1:N | Lifecycle ownership |
| Household | has | SavingsGoal | 1:N | Lifecycle ownership |
| SavingsGoal | has | SavingsContribution | 1:N | Lifecycle ownership |
| Household | has | GivingRecord | 1:N | Lifecycle ownership |
| Household | has | HouseholdRoutine | 1:N | Lifecycle ownership |
| Household | has | AgentActivity | 1:N | Reference/log only |

---

## 7. State Models

### MonthlyAllocation State

| State | Meaning | Allowed Next States |
|---|---|---|
| Draft | Proposed, not authoritative | Confirmed, Discarded |
| Confirmed | Authoritative | (terminal for the period) |
| Discarded | Abandoned draft | Draft (a new draft may be created) |

### HouseholdRoutine State

| State | Meaning | Allowed Next States |
|---|---|---|
| Scheduled | Due at `next_due_at` | Completed, Snoozed |
| Completed | Done for this occurrence | Scheduled (if recurring) |
| Snoozed | Postponed | Scheduled |

### Invariants

See `docs/01_features/monthly-allocation.md`, Section 6, for MonthlyAllocation state invariants.

---

## 8. Identifiers

### Identifier Strategy

| Entity | Identifier | Generated By | Externally Exposed? |
|---|---|---|---:|
| All entities in this catalog | UUID (recommended) | Household MCP | No — internal use only for V1 |

### Rules

- Identifiers should be stable for the entity's lifecycle.
- No entity is exposed to a public API in V1 (single private household), so external-exposure risk is low, but identifiers should still avoid trivially guessable sequential values.

---

## 9. Audit and Temporal Data

| Concern | Strategy |
|---|---|
| Created timestamp | Every entity has a `created_at` |
| Updated timestamp | Mutable entities (e.g. `SavingsGoal.current_amount`) have an `updated_at` |
| Actor / changed by | `MonthlyAllocation.confirmed_by`; other write actions may be attributed via `AgentActivity` or an equivalent mechanism |
| History | Append-only `SavingsContribution` and `GivingRecord` entries serve as history; no separate audit table is planned for V1 |
| Soft delete | Not used for V1 — `HouseholdRoutine` deletion is a hard delete; financial records are not deleted |

---

## 10. Data Classification

| Data | Classification | Rationale | Handling Notes |
|---|---|---|---|
| Household income/allocation amounts | Sensitive | Household financial data | Avoid unnecessary exposure/logging |
| Savings goal amounts/progress | Sensitive | Household financial data | Avoid unnecessary exposure/logging |
| Zakat/sedekah amounts | Sensitive | Household financial data | Avoid unnecessary exposure/logging |
| Telegram user IDs | Confidential | Identity/allowlist data | Not logged unnecessarily |
| Routine titles/schedules | Internal | Household operational data | Low sensitivity |

---

## 11. Personal and Sensitive Data

| Data | Purpose | Legal/Product Basis | Retention | Deletion / Export |
|---|---|---|---|---|
| Telegram user ID | Identify allowlisted household members | Household consent (private personal system) | Indefinite while used | Removed if the household stops using FARIA |
| Personal allowance amount (not spend detail) | Track that an allowance was allocated | Household consent | Indefinite | Removed if the household stops using FARIA |

FARIA explicitly does not collect personal allowance spend detail (see Product Brief).

---

## 12. Persistence Mapping

| Domain Data | Store | Persistence Model | Notes |
|---|---|---|---|
| Household, Member, MonthlyAllocation, AllocationItem, SavingsGoal, SavingsContribution, GivingRecord, HouseholdRoutine, AgentActivity | SQLite | Table per entity (expected) | Exact table/column design deferred to migration implementation |

---

## 13. Database Constraints and Invariants

| Invariant | Enforcement |
|---|---|
| AllocationItem amounts are non-negative | Application + DB constraint |
| At most one Confirmed MonthlyAllocation per `(household, period)` | Application + DB constraint |
| SavingsContribution.amount is positive | Application + DB constraint |
| GivingRecord.type is one of a fixed enum (`zakat_penghasilan`, `sedekah`) | Application + DB constraint |

---

## 14. Indexing Intent

| Query / Access Pattern | Data | Expected Scale | Index Intent |
|---|---|---:|---|
| Get current/latest MonthlyAllocation for a period | MonthlyAllocation | Single household, low volume | Index on `(household_id, period)` |
| Get SavingsGoal progress | SavingsGoal + SavingsContribution | Single household, low volume | Index on `(goal_id)` for contributions |

---

## 15. Consistency Model

| Data / Operation | Required Consistency | Rationale |
|---|---|---|
| All FARIA data | Strong | Single SQLite instance, single household — no distributed consistency concerns |

---

## 16. Cache and Derived Data

None in V1 — no cache layer exists (see System Architecture).

---

## 17. Events and Data Replication

None in V1 — no event/replication mechanism exists; the dashboard reads through the application/API boundary directly, not via a replicated read model.

---

## 18. Migration Principles

- All persistent schema changes are version controlled.
- Production migrations must consider existing data.
- Prefer backward-compatible expand/contract patterns when phased deployment requires them.
- Separate large data backfills from schema changes when operational risk warrants it.
- Destructive changes require an explicit migration/rollout strategy.
- Do not reuse removed columns/fields with new semantics without deliberate compatibility analysis.

Detailed rules belong in `../standards/07_DATA_PERSISTENCE_STANDARD.md`.

---

## 19. Data Lifecycle

| Data | Created When | Updated When | Archived / Deleted When |
|---|---|---|---|
| MonthlyAllocation | Created on first income message for a period | Updated when re-drafted | Never deleted; superseded drafts marked Discarded |
| SavingsContribution / GivingRecord | Created when recorded | Immutable | Never deleted (financial history) |
| HouseholdRoutine | Created when defined | Updated on completion/snooze | Deleted when the household removes it |

---

## 20. Backup and Recovery Requirements

- RPO/RTO: not yet defined numerically for V1 (see Open Data Decisions); qualitatively, household financial data must not depend solely on the host's local disk.
- Backup retention: TBD.
- Restore validation: TBD.

---

## 21. Open Data Decisions

| ID | Question | Impact | Owner |
|---|---|---|---|
| DQ-01 | Exact migration/schema tooling for SQLite | Blocks first schema creation | Implementation |
| DQ-02 | Whether AgentActivity is owned by Household MCP or Hermes directly | Affects dashboard read path | Implementation |
| DQ-03 | Backup retention/RPO/RTO numeric targets | Affects backup implementation | Household |

Material persistence decisions should become ADRs when resolved.

---

## 22. Related Documents

- System Architecture: `./SYSTEM_ARCHITECTURE.md`
- Feature Specs: `../01_features/`
- Security Standard: `../standards/08_SECURITY_STANDARD.md`
- Data Persistence Standard: `../standards/07_DATA_PERSISTENCE_STANDARD.md`

---

## 23. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `2026-09-11` | Initial draft | sipratama |
