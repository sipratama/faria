# Feature Specification — Savings Goals

> Authoritative behavior for goal-based savings and actual contribution progress in FARIA V1.

## 1. Intent and Scope

Household members can create named savings goals, inspect progress, and record money that has actually been contributed. Bank/Jago integration, withdrawals, corrections, recommendations, and transaction tracking are out of scope.

Monthly Allocation savings lines are PLAN only. A goal's progress changes only after a separate `SavingsContribution` is explicitly confirmed and recorded.

## 2. Functional Requirements

### FR-SAVE-001 — Create Goal

FARIA must present a proposed goal and require explicit human confirmation before calling `savings_goal_create`. The goal has a non-blank name, positive integer-IDR target, optional short description, and optional ISO target date. New goals start `ACTIVE` with zero derived progress.

### FR-SAVE-002 — Read Goal Progress

`savings_goal_list` and `savings_goal_get` return authoritative progress derived from immutable contribution history. Name matching in conversation is exact or obvious case-insensitive matching; ambiguous matches require clarification.

### FR-SAVE-003 — Record Actual Contribution

FARIA must distinguish planned allocation language from statements that money was actually contributed. It presents the amount and goal, then requires explicit confirmation before calling `savings_contribution_record`. Ambiguous acknowledgement is insufficient.

### FR-SAVE-004 — Complete Goal

When summed contributions reach or exceed the target, status becomes `COMPLETED`; over-target contributions are allowed and completion does not auto-archive the goal.

## 3. Data and Invariants

- Lifecycle: `ACTIVE → COMPLETED`; `ARCHIVED` is reserved for an intentional future workflow.
- `current_amount_idr` is calculated from the sum of positive immutable contributions, never stored as an independently editable balance.
- Contributions may optionally reference a confirmed MonthlyAllocation.
- Retrying the same goal + allocation reference + amount returns the existing contribution; a different amount conflicts.
- No delete, arbitrary update, withdrawal, generic CRUD, raw SQL, or bank movement tool exists.

## 4. Household MCP Contract

| Tool | Purpose |
|---|---|
| `savings_goal_list` | List goals, optionally by status |
| `savings_goal_create` | Create a confirmed goal intent |
| `savings_goal_get` | Read one goal and derived progress |
| `savings_contribution_record` | Append an explicitly confirmed ACTUAL contribution |

## 5. Acceptance

- Valid goals can be created/listed/read and duplicate active names are rejected case-insensitively.
- Invalid names, dates, targets, goal IDs, and contribution amounts are rejected.
- Multiple contributions accumulate and complete a goal at/above target.
- Allocation confirmation creates no contribution.
- Contribution rows are append-only and cannot be updated or deleted.
