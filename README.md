# FARIA

FARIA (FArah RIzkia Ananda) is a private, single-household **AI Household Operating System**. It helps a household owner and spouse manage monthly money allocation, zakat and sedekah, savings goals, household operating budget, personal allowances, and recurring household routines — without forcing transaction-by-transaction bookkeeping.

## Status

Personal MVP through RF-05: runtime connectivity, household finance foundations, agent monitoring, and the local read-only Agent Control Center are implemented. Household MCP remains the sole mutation authority over SQLite; a separate loopback-only FastAPI process provides three purpose-built GET endpoints to the Next.js dashboard. Telegram remains the primary interaction and financial-mutation interface.

## What FARIA Does (V1)

- Turns a monthly income message into a draft allocation across zakat, sedekah, savings, household operating budget, and personal allowances — persisted only after explicit human confirmation.
- Tracks goal-based savings; only explicitly confirmed contribution records change goal progress.
- Calculates zakat using the household-selected `THP × 2.5%` rule, asks for sedekah manually each month, and records actual giving separately from planned allocations.
- Tracks simple household routines/reminders (e.g. AC maintenance, bill reminders).
- Is used through a private Telegram group restricted to an explicit allowlist.
- Is monitored through a web dashboard (Agent Control Center) showing the status of its household personas.

FARIA manages **allocations and goals, not transactions** — it deliberately does not ask the household to record every small expense.

## Architecture Summary

One Hermes agent runtime orchestrates four logical personas (Finance, Giving, Home Ops, Planner) as skills — not independent agents — routed through 9Router to OpenRouter for model access. The Finance skill covers allocation, rules, savings, and giving through exactly twelve `faria-household` MCP tools. Authoritative household state lives in SQLite behind that constrained MCP boundary. The React/Next.js dashboard reads only through a separate FastAPI query boundary and clearly marks Home Ops, Planner, Gateway, 9Router, and AI usage according to what is actually observable.

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
| `docs/02_architecture/SYSTEM_ARCHITECTURE.md` | System structure, trust boundaries |
| `docs/02_architecture/DATA_MODEL.md` | Domain entities and ownership |
| `AGENTS.md` | Rules for AI coding agents working in this repo |
| `docs/standards/` | Reusable engineering standards |

Several conditional documents (roadmap, NFR, UX flows, design system, test strategy, threat model, deployment, runbook, risks, release checklist, known limitations) are present but marked "Not activated for V1" — each will be filled in once its own stated activation condition is met. Developer Setup and Configuration were activated once a real runtime (RF-01) existed to describe.

## Technology Direction (V1)

Hermes (agent runtime) · 9Router (model gateway) · OpenRouter (model provider) · custom Household MCP server · SQLite · React/Next.js dashboard. The accepted local development topology uses a managed Hermes install on macOS, launchd for the gateway, 9Router in Docker/OrbStack, and Docker as Hermes' terminal sandbox. Production packaging and hosting remain open decisions.

## Setup

RF-01 established Telegram → Hermes Gateway → 9Router → model. RF-02 added Hermes → Household MCP → SQLite, RF-03 added the repo-owned identity and Finance skill, RF-04 expanded the constrained surface to twelve finance tools, and RF-05 added monitoring plus the local read-only dashboard. See `docs/05_operations/DEVELOPER_SETUP.md` for activation and testing.
