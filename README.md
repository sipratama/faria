# FARIA

FARIA (FArah RIzkia Ananda) is a private, single-household **AI Household Operating System**. It helps a household owner and spouse manage monthly money allocation, zakat and sedekah, savings goals, household operating budget, personal allowances, and recurring household routines — without forcing transaction-by-transaction bookkeeping.

## Status

Documentation-initialized personal MVP. No implementation exists yet. This repository currently contains only the product/architecture baseline needed to start building the first vertical slice.

## What FARIA Does (V1)

- Turns a monthly income message into a draft allocation across zakat, sedekah, savings, household operating budget, and personal allowances — persisted only after explicit human confirmation.
- Tracks savings goals and contributions.
- Records zakat penghasilan and sedekah as distinct recurring allocations (the calculation/amount rule is configured by the household, not hardcoded).
- Tracks simple household routines/reminders (e.g. AC maintenance, bill reminders).
- Is used through a private Telegram group restricted to an explicit allowlist.
- Is monitored through a web dashboard (Agent Control Center) showing the status of its household personas.

FARIA manages **allocations and goals, not transactions** — it deliberately does not ask the household to record every small expense.

## Architecture Summary

One Hermes agent runtime orchestrates four logical personas (Finance, Giving, Home Ops, Planner) as skills — not independent agents — routed through 9Router to OpenRouter for model access. Authoritative household state lives in SQLite behind a constrained Household MCP tool boundary; the LLM never gets raw SQL or shell access. A React/Next.js dashboard reads state through an application/API boundary. See `docs/02_architecture/SYSTEM_ARCHITECTURE.md` for the full picture.

## First Vertical Slice

**Monthly Allocation**: Telegram income message → Hermes drafts an allocation → household confirms → Household MCP persists to SQLite → dashboard reflects the confirmed state. See `docs/01_features/monthly-allocation.md`.

## Documentation Map

| Document | Owns |
|---|---|
| `docs/00_product/PRODUCT_BRIEF.md` | Why FARIA exists, for whom, V1 boundary |
| `docs/00_product/PRD.md` | Product capabilities and scope |
| `docs/01_features/monthly-allocation.md` | First vertical slice behavior |
| `docs/02_architecture/SYSTEM_ARCHITECTURE.md` | System structure, trust boundaries |
| `docs/02_architecture/DATA_MODEL.md` | Domain entities and ownership |
| `AGENTS.md` | Rules for AI coding agents working in this repo |
| `docs/standards/` | Reusable engineering standards |

Several conditional documents (roadmap, NFR, UX flows, design system, test strategy, threat model, developer setup, configuration, deployment, runbook, risks, release checklist, known limitations) are present but marked "Not activated for V1" — each will be filled in once its own stated activation condition is met.

## Technology Direction (V1)

Hermes (agent runtime) · 9Router (model gateway) · OpenRouter (model provider) · custom Household MCP server · SQLite · React/Next.js dashboard · Docker on an always-on host. See System Architecture for rationale and open decisions (hosting provider, backup destination).

## Setup

Not applicable yet — no source code exists. Setup instructions will be added to `docs/05_operations/DEVELOPER_SETUP.md` once implementation begins.
