# Developer Setup — <PROJECT_NAME>

> **Document role:** Authoritative instructions for getting a development environment from a clean machine to a verified local run.
>
> Keep this document executable and current. Do not duplicate configuration definitions that belong in `.env.example` or `CONFIGURATION.md`.

---

## 1. Supported Development Environment

| Tool / Platform | Supported Version |
|---|---|
| OS | `<macOS / Linux / Windows/WSL>` |
| Runtime | `<VERSION>` |
| Package Manager | `<VERSION>` |
| Container Runtime | `<Docker / Podman / N/A>` |
| Database Client | `<OPTIONAL>` |

Pin versions where incompatibility is material.

---

## 2. Prerequisites

Install:
- `<TOOL>`;
- `<TOOL>`;
- `<TOOL>`.

Verify:

```bash
<command> --version
```

---

## 3. Clone

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

---

## 4. Environment Configuration

Copy the example:

```bash
cp .env.example .env
```

Then configure required local values.

Never copy production secrets into a local `.env`.

See:

`docs/05_operations/CONFIGURATION.md`

---

## 5. Local Dependencies

### Option A — Containers

```bash
<docker/podman compose command>
```

### Option B — Native

`<INSTRUCTIONS>`

Choose one canonical path where possible. Too many setup paths increase maintenance cost.

---

## 6. Database Initialization

```bash
<CREATE/START DB>
<MIGRATION COMMAND>
<SEED COMMAND IF NEEDED>
```

Describe:
- required database name;
- migration tool;
- optional seed/demo data;
- reset command.

---

## 7. Install Dependencies

### Backend

```bash
<COMMAND>
```

### Frontend

```bash
<COMMAND>
```

Remove sections that do not apply.

---

## 8. Run Locally

### Backend

```bash
<COMMAND>
```

Expected:

```text
<PORT / HEALTH URL>
```

### Frontend

```bash
<COMMAND>
```

Expected:

```text
<LOCAL URL>
```

---

## 9. Verify Setup

A successful setup should prove more than process startup.

### Health

```bash
<COMMAND>
```

### Tests

```bash
<FAST TEST COMMAND>
```

### Critical Local Flow

`<SHORT MANUAL OR AUTOMATED CHECK>`

---

## 10. Common Development Commands

| Task | Command |
|---|---|
| Build | `<COMMAND>` |
| Unit tests | `<COMMAND>` |
| Integration tests | `<COMMAND>` |
| Lint | `<COMMAND>` |
| Format | `<COMMAND>` |
| Migrations | `<COMMAND>` |
| Generate contracts/client | `<COMMAND>` |
| Start local stack | `<COMMAND>` |
| Stop local stack | `<COMMAND>` |

---

## 11. Test Accounts / Local Identity

Do not place real credentials here.

Use documented local-only seeded identities:

| Role | Username | Credential Source |
|---|---|---|
| `<ROLE>` | `<USER>` | `<LOCAL SEED / ENV>` |

---

## 12. External Service Sandboxes

| Service | Environment | Setup |
|---|---|---|
| `<SERVICE>` | Sandbox / Mock | `<LINK/INSTRUCTION>` |

Prefer fake/local adapters for repeatable development where appropriate.

---

## 13. IDE / Editor

Optional recommended configuration:
- formatting;
- linting;
- language server;
- test integration.

Do not require a specific commercial IDE unless project tooling truly depends on it.

---

## 14. AI Agent Setup

Agents should start from:
- `AGENTS.md`;
- `CLAUDE.md` for Claude Code adapter;
- relevant project documentation only.

Do not require agents to read all docs.

---

## 15. Troubleshooting

### <PROBLEM>

**Symptom**
`<ERROR>`

**Cause**
`<CAUSE>`

**Fix**
```bash
<COMMAND>
```

Only include recurring project-specific issues.

---

## 16. Clean Reset

```bash
<COMMANDS>
```

Clearly warn if the command deletes local data.

---

## 17. Setup Acceptance Checklist

- [ ] required runtimes installed;
- [ ] dependencies installed;
- [ ] local configuration created;
- [ ] infrastructure running;
- [ ] migrations applied;
- [ ] backend starts;
- [ ] frontend starts where applicable;
- [ ] health check passes;
- [ ] fast test suite passes.

---

## 18. Related Documents

- Configuration: `./CONFIGURATION.md`
- Deployment: `./DEPLOYMENT.md`
- Runbook: `./RUNBOOK.md`
- Test Strategy: `../04_engineering/TEST_STRATEGY.md`

---

## 19. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
