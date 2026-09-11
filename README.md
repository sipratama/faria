# FARIA

FARIA (FArah RIzkia Ananda) is a private, single-household **AI Household Operating System**. It helps a household owner and spouse manage monthly money allocation, zakat and sedekah, savings goals, household operating budget, personal allowances, and recurring household routines — without forcing transaction-by-transaction bookkeeping.

## Status

Documentation-initialized personal MVP. RF-01 runtime connectivity is proven with a managed Hermes installation on macOS, a launchd-supervised Telegram gateway, and 9Router running locally through Docker/OrbStack. FARIA application code, Household MCP, business persistence, and product features have not been implemented yet.

## What FARIA Does (V1)

- Turns a monthly income message into a draft allocation across zakat, sedekah, savings, household operating budget, and personal allowances — persisted only after explicit human confirmation.
- Tracks savings goals and contributions.
- Records zakat penghasilan and sedekah as distinct recurring allocations (the calculation/amount rule is configured by the household, not hardcoded).
- Tracks simple household routines/reminders (e.g. AC maintenance, bill reminders).
- Is used through a private Telegram group restricted to an explicit allowlist.
- Is monitored through a web dashboard (Agent Control Center) showing the status of its household personas.

FARIA manages **allocations and goals, not transactions** — it deliberately does not ask the household to record every small expense.

## Architecture Summary

One Hermes agent runtime orchestrates four logical personas (Finance, Giving, Home Ops, Planner) as skills — not independent agents — routed through 9Router to OpenRouter for model access. Authoritative household state lives in SQLite behind a constrained Household MCP tool boundary, with no raw SQL access for the LLM. Hermes terminal execution is isolated in Docker; tighter restriction of its broader tools and skills remains a security follow-up. A React/Next.js dashboard reads state through an application/API boundary. See `docs/02_architecture/SYSTEM_ARCHITECTURE.md` for the full picture.

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

Several conditional documents (roadmap, NFR, UX flows, design system, test strategy, threat model, deployment, runbook, risks, release checklist, known limitations) are present but marked "Not activated for V1" — each will be filled in once its own stated activation condition is met. Developer Setup and Configuration were activated once a real runtime (RF-01) existed to describe.

## Technology Direction (V1)

Hermes (agent runtime) · 9Router (model gateway) · OpenRouter (model provider) · custom Household MCP server · SQLite · React/Next.js dashboard. The accepted local development topology uses a managed Hermes install on macOS, launchd for the gateway, 9Router in Docker/OrbStack, and Docker as Hermes' terminal sandbox. Production packaging and hosting remain open decisions.

## Setup

RF-01 (Runtime Foundation) established the minimum runtime path: Telegram → Hermes Gateway → 9Router → model. See `docs/05_operations/DEVELOPER_SETUP.md` to configure the managed local installation and `scripts/runtime/README.md` for acceptance evidence and repeatable checks. Household MCP, SQLite, Monthly Allocation, and the dashboard app are not part of this yet.
