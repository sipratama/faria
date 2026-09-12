# FARIA

FARIA (FArah RIzkia Ananda) is a private, single-household **AI Household Operating System**. It helps a household owner and spouse manage monthly money allocation, zakat and sedekah, savings goals, household operating budget, personal allowances, and recurring household routines — without forcing transaction-by-transaction bookkeeping.

## Status

Personal MVP through RF-04: runtime connectivity, monthly allocation, household member identity, authoritative financial rules, savings goals/contributions, and actual giving records are implemented. The accepted local runtime uses managed Hermes on macOS, a launchd-supervised Telegram gateway, and 9Router through Docker/OrbStack. Household MCP provides a constrained Python stdio server backed by SQLite, while the repo-owned FARIA identity and Finance skill enforce the PLAN-versus-ACTUAL and explicit-confirmation boundaries. The dashboard remains deferred.

## What FARIA Does (V1)

- Turns a monthly income message into a draft allocation across zakat, sedekah, savings, household operating budget, and personal allowances — persisted only after explicit human confirmation.
- Tracks goal-based savings; only explicitly confirmed contribution records change goal progress.
- Calculates zakat using the household-selected `THP × 2.5%` rule, asks for sedekah manually each month, and records actual giving separately from planned allocations.
- Tracks simple household routines/reminders (e.g. AC maintenance, bill reminders).
- Is used through a private Telegram group restricted to an explicit allowlist.
- Is monitored through a web dashboard (Agent Control Center) showing the status of its household personas.

FARIA manages **allocations and goals, not transactions** — it deliberately does not ask the household to record every small expense.

## Architecture Summary

One Hermes agent runtime orchestrates four logical personas (Finance, Giving, Home Ops, Planner) as skills — not independent agents — routed through 9Router to OpenRouter for model access. The Finance skill currently covers allocation, rules, savings, and giving through exactly twelve `faria-household` MCP tools; the developer CLI keeps its broader tool surface. Authoritative household state lives in SQLite behind that constrained MCP boundary, with no raw SQL or shell access from Telegram. A React/Next.js dashboard remains a later read path. See `docs/02_architecture/SYSTEM_ARCHITECTURE.md` for the full picture.

## First Vertical Slice

**Household Finance**: FARIA retrieves authoritative rules, calculates zakat deterministically, asks for manual sedekah and goal allocations, saves a non-authoritative monthly plan, and records actual savings/giving only through separate explicitly confirmed actions. Dashboard reflection remains deferred. See `docs/01_features/monthly-allocation.md`, `docs/01_features/savings-goals.md`, and `docs/01_features/giving.md`.

## Documentation Map

| Document | Owns |
|---|---|
| `docs/00_product/PRODUCT_BRIEF.md` | Why FARIA exists, for whom, V1 boundary |
| `docs/00_product/PRD.md` | Product capabilities and scope |
| `docs/01_features/monthly-allocation.md` | Monthly allocation PLAN behavior |
| `docs/01_features/savings-goals.md` | Savings goals and ACTUAL contributions |
| `docs/01_features/giving.md` | Household rules and ACTUAL giving records |
| `docs/02_architecture/SYSTEM_ARCHITECTURE.md` | System structure, trust boundaries |
| `docs/02_architecture/DATA_MODEL.md` | Domain entities and ownership |
| `AGENTS.md` | Rules for AI coding agents working in this repo |
| `docs/standards/` | Reusable engineering standards |

Several conditional documents (roadmap, NFR, UX flows, design system, test strategy, threat model, deployment, runbook, risks, release checklist, known limitations) are present but marked "Not activated for V1" — each will be filled in once its own stated activation condition is met. Developer Setup and Configuration were activated once a real runtime (RF-01) existed to describe.

## Technology Direction (V1)

Hermes (agent runtime) · 9Router (model gateway) · OpenRouter (model provider) · custom Household MCP server · SQLite · React/Next.js dashboard. The accepted local development topology uses a managed Hermes install on macOS, launchd for the gateway, 9Router in Docker/OrbStack, and Docker as Hermes' terminal sandbox. Production packaging and hosting remain open decisions.

## Setup

RF-01 established Telegram → Hermes Gateway → 9Router → model. RF-02 added Hermes → Household MCP → SQLite, RF-03 added the repo-owned identity and Finance skill, and RF-04 expands the constrained MCP/Telegram surface to twelve finance tools. See `docs/05_operations/DEVELOPER_SETUP.md` for local activation and testing, and `scripts/runtime/README.md` for runtime checks.
