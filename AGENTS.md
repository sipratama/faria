# AGENTS.md

Repository-wide instructions for AI coding agents working on **FARIA** — a private, single-household AI Household Operating System.

This file is intentionally small. It routes agents to authoritative sources and states non-negotiable guardrails. Detailed product, architecture, and engineering rules live in the documents below.

## 1. Core Rule

FARIA is currently **documentation-initialized only** — no source code, Household MCP, Hermes configuration, dashboard, or deployment exists yet. Do not silently create source structure, contracts, migrations, or deployment config; follow the plan already recorded in the documents below instead of inventing a new one.

Before non-trivial work, identify: what behavior is requested; which document owns it; which architecture boundaries apply; which contracts/data may change; which standards apply; what evidence is needed. Do not invent product or architecture decisions.

## 2. Source of Truth

| Concern | Authoritative Source |
|---|---|
| Product purpose, users, outcomes, non-goals | `docs/00_product/PRODUCT_BRIEF.md` |
| Product capabilities and scope | `docs/00_product/PRD.md` |
| Feature behavior | `docs/01_features/<feature>.md` |
| System structure and boundaries | `docs/02_architecture/SYSTEM_ARCHITECTURE.md` |
| Domain data model | `docs/02_architecture/DATA_MODEL.md` (+ migrations/schema once they exist) |
| Engineering rules | `docs/standards/` |
| New-project / re-initialization workflow | `docs/PROJECT_INITIALIZATION.md` |

Several conditional documents (roadmap, NFR, UX flows, design system, test strategy, threat model, developer setup, configuration, deployment, runbook, risks, release checklist, known limitations) currently exist but are marked **"Not activated for V1"** in place. Read each file's own activation condition before filling it in — do not populate it with speculative content preemptively.

## 3. Read Selectively

Default order: this file → relevant PRD capability → relevant feature spec → the relevant `SYSTEM_ARCHITECTURE.md` section → `DATA_MODEL.md` (if data changes) → relevant standard → source/tests. Do not read the entire `docs/` tree for a small task.

## 4. Non-Negotiable Guardrails

Do not:

- persist a proposed financial allocation (or other material household state change) as authoritative without explicit human confirmation (PRD `PR-001`; `SYSTEM_ARCHITECTURE.md` `INV-03`);
- give the LLM/agent unrestricted raw SQL or shell access — all authoritative state changes go through Household MCP tools (`INV-01`, `INV-02`);
- let FARIA autonomously transfer money, pay bills, move savings, change zakat/sedekah rules, or delete financial history (PRD `PR-002`);
- process a request from a Telegram identity outside the explicit allowlist (PRD `PR-004`);
- commit secrets (Telegram bot token, OpenRouter/9Router keys) — use environment/runtime secret configuration;
- implement transaction-level expense tracking — FARIA manages allocations and goals, not transactions (Product Brief, `P-01`);
- turn the Finance/Giving/Home Ops/Planner personas into independent autonomous agents without an explicit ADR changing `INV-04`;
- expand scope toward SaaS/multi-tenancy, 2D/3D dashboard visualization, or a mobile app — explicit V1 non-goals;
- let FARIA respond to requests outside household finance/operations scope (PRD `PR-003`) — enforce this through domain instructions and tool allowlists, not only a system prompt.

## 5. Standards Routing

Load only the relevant standard from `docs/standards/` (see `00_STANDARD_INDEX.md` for the full routing table) — e.g. `04_BACKEND_STANDARD.md` for Household MCP/Hermes backend work, `07_DATA_PERSISTENCE_STANDARD.md` for schema/migration work, `08_SECURITY_STANDARD.md` for anything touching secrets/auth/the Telegram allowlist, `14_AI_ASSISTED_DEVELOPMENT.md` for AI-assisted workflow rules.

## 6. Change Discipline

- Feature behavior changes → update the relevant `docs/01_features/<feature>.md`, preserving stable `FR-<FEATURE>-<NUMBER>` IDs.
- Capability/scope changes → update `docs/00_product/PRD.md`.
- Product purpose/outcome changes → update `docs/00_product/PRODUCT_BRIEF.md`.
- Architecture-boundary changes (e.g. personas becoming independent agents, changing the authoritative store, adding a new trust boundary) → create/update an ADR in `docs/02_architecture/adr/` and update `SYSTEM_ARCHITECTURE.md`.
- Persistent schema changes → version-controlled migration + update `DATA_MODEL.md`.

## 7. Testing and Evidence

Run the smallest meaningful test set while iterating; run broader checks before completion. Never claim a command or test passed without executing it. The confirmation boundary (`FR-ALLOC-004` and equivalents in future features) must always have regression coverage once implementation exists.

## 8. Completion Report

For non-trivial work, report: **Changed / Requirements / Contracts-Data / Tests / Architecture / Risks-Limitations.**
