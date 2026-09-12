# Feature Specification — Giving

> Authoritative behavior for household-selected zakat calculation, manual sedekah, and actual giving records in FARIA V1.

## 1. Household Financial Rules

Household MCP/SQLite owns one authoritative rule set:

| Rule | Value |
|---|---|
| Zakat basis | `THP` |
| Zakat rate | `250` basis points (2.5%) |
| Sedekah mode | `MANUAL` |
| Savings mode | `GOAL_BASED` |
| Remainder policy | `ASK_ALLOW_UNALLOCATED` |

These are household-selected operating rules, not universal religious advice. RF-04 exposes no rule-editing workflow.

## 2. Functional Requirements

### FR-GIVE-001 — Read Rules and Calculate Zakat

`financial_rules_get` returns the authoritative singleton. `zakat_calculate` accepts only positive integer THP and reads the stored rate; callers cannot supply a percentage. It calculates `(thp_idr × basis_points + 5,000) // 10,000`, providing deterministic ROUND_HALF_UP whole-IDR output without binary floating point.

### FR-GIVE-002 — Ask for Manual Sedekah

When completing a Monthly Allocation, FARIA asks the household for that month's intended sedekah. There is no default, percentage, or minimum. Explicit zero is valid for the PLAN line.

### FR-GIVE-003 — Record Actual Giving

A zakat/sedekah AllocationItem is PLAN only. FARIA records ACTUAL fulfillment only after presenting the type, amount, and period and receiving explicit human confirmation before `giving_record`.

### FR-GIVE-004 — Read Giving History

`giving_list` returns immutable actual records and may filter by `YYYY-MM` period and type (`zakat_penghasilan` or `sedekah`).

## 3. Data and Invariants

- Giving amounts are positive integer IDR; periods use valid `YYYY-MM`.
- A referenced MonthlyAllocation must be `CONFIRMED` and match the giving period.
- Retrying the same period + type + allocation reference + amount returns the existing record; a different amount conflicts.
- Multiple legitimate unreferenced sedekah records in one month are allowed.
- Giving records are append-only; there is no update/delete-history tool.
- Confirming a MonthlyAllocation creates no GivingRecord or other real-world side effect.

## 4. Household MCP Contract

| Tool | Purpose |
|---|---|
| `financial_rules_get` | Read authoritative household financial rules |
| `zakat_calculate` | Calculate zakat deterministically from THP |
| `giving_list` | List/filter ACTUAL giving history |
| `giving_record` | Append explicitly confirmed ACTUAL fulfillment |

## 5. Deferred

Religious-rule interpretation, nisab/deductions, automatic payments, reminders, corrections/refunds, rule editing, and transaction tracking remain out of scope.
