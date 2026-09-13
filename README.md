# FARIA

FARIA (FArah RIzkia Ananda) is a private, single-household **AI Household Operating System**. It helps a household owner and spouse manage monthly money allocation, zakat and sedekah, savings goals, household operating budget, personal allowances, and recurring household routines — without forcing transaction-by-transaction bookkeeping.

## Status

Personal MVP through RF-06 is implemented. RF-07A adds provider-neutral personal operations hardening: consistent SQLite snapshots, mandatory `age` encryption, restore verification, bounded retention, non-mutating runtime diagnostics, and a concise recovery runbook. Household MCP remains the sole mutation authority over SQLite; Hermes Cron is only the reminder scheduling/delivery engine. A separate loopback-only FastAPI process provides three purpose-built GET endpoints to the Next.js dashboard. Telegram remains the primary interaction and mutation interface.

## What FARIA Does (V1)

- Turns a monthly income message into a draft allocation across zakat, sedekah, savings, household operating budget, and personal allowances — persisted only after explicit human confirmation.
- Tracks goal-based savings; only explicitly confirmed contribution records change goal progress.
- Calculates zakat using the household-selected `THP × 2.5%` rule, asks for sedekah manually each month, and records actual giving separately from planned allocations.
- Tracks simple household routines/reminders (e.g. AC maintenance, bill reminders).
- Is used through a private Telegram group restricted to an explicit allowlist.
- Is monitored through a web dashboard (Agent Control Center) showing the status of its household personas.

FARIA manages **allocations and goals, not transactions** — it deliberately does not ask the household to record every small expense.

## Architecture Summary

One Hermes agent runtime orchestrates four logical personas (Finance, Giving, Home Ops, Planner) as skills — not independent agents — routed through 9Router to OpenRouter for model access. Finance and Home Ops use exactly eighteen constrained `faria-household` MCP tools. Authoritative household state lives in SQLite behind that boundary; Hermes Cron stores only runtime scheduling/delivery machinery. The React/Next.js dashboard reads only through a separate FastAPI query boundary, activates Home Ops from persisted persona state, and keeps Planner and unobservable integrations honestly inactive/unmonitored.

## First Vertical Slice

**Household Finance**: FARIA retrieves authoritative rules, calculates zakat deterministically, asks for manual sedekah and goal allocations, saves a non-authoritative monthly plan, and records actual savings/giving only through separate explicitly confirmed actions. The local dashboard reflects pending drafts, recent monitored actions, persona state, and a small household snapshot without exposing financial controls.

## Documentation Map

| Document | Owns |
|---|---|
| `docs/00_product/PRODUCT_BRIEF.md` | Why FARIA exists, for whom, V1 boundary |
| `docs/00_product/PRD.md` | Product capabilities and scope |
| `docs/01_features/monthly-allocation.md` | Monthly allocation PLAN behavior |
| `docs/01_features/savings-goals.md` | Savings goals and ACTUAL contributions |
| `docs/01_features/giving.md` | Household rules and ACTUAL giving records |
| `docs/01_features/household-routines.md` | Household routine/reminder lifecycle and confirmation behavior |
| `docs/02_architecture/SYSTEM_ARCHITECTURE.md` | System structure, trust boundaries |
| `docs/02_architecture/DATA_MODEL.md` | Domain entities and ownership |
| `AGENTS.md` | Rules for AI coding agents working in this repo |
| `docs/standards/` | Reusable engineering standards |

Several conditional documents remain marked "Not activated for V1" until their own activation conditions are met. Developer Setup and Configuration were activated in RF-01; the operations runbook is activated in RF-07A. Provider-specific deployment documentation remains deferred until RF-07B selects a host.

## Technology Direction (V1)

Hermes (agent runtime) · 9Router (model gateway) · OpenRouter (model provider) · custom Household MCP server · SQLite · React/Next.js dashboard. The accepted local development topology uses a managed Hermes install on macOS, launchd for the gateway, 9Router in Docker/OrbStack, and Docker as Hermes' terminal sandbox. Production packaging and hosting remain open decisions.

## Setup

RF-01 established Telegram → Hermes Gateway → 9Router → model. RF-02 added Hermes → Household MCP → SQLite, RF-03 added the repo-owned identity and Finance skill, RF-04 expanded the constrained finance surface, RF-05 added monitoring plus the local read-only dashboard, and RF-06 added authoritative routines with Hermes Cron delivery plus Home Ops visibility. RF-07A adds backup, restore verification, runtime diagnostics, and recovery procedures without selecting or provisioning a remote host. See `docs/05_operations/DEVELOPER_SETUP.md` and `docs/05_operations/RUNBOOK.md`.
