# Known Limitations — <PROJECT_NAME>

> **Document role:** Authoritative list of intentionally unsupported, incomplete, degraded, or constrained behavior that users, operators, contributors, or AI agents must not mistake for fully supported functionality.
>
> A limitation is not a hidden bug backlog. Track actionable defects/tasks in the issue tracker.

---

## 1. Purpose

Record limitations when they affect:
- user expectations;
- implementation decisions;
- operational behavior;
- compatibility;
- data behavior;
- security assumptions;
- release decisions.

Do not record trivial internal imperfections that have no meaningful consequence.

---

## 2. Active Limitations

| ID | Limitation | Impact | Workaround | Planned? |
|---|---|---|---|---|
| LIM-001 | `<LIMITATION>` | `<IMPACT>` | `<WORKAROUND/NONE>` | Yes / No / TBD |

---

## 3. Limitation Detail

### LIM-001 — <TITLE>

**Status**  
Active / Planned Removal / Accepted

**Description**  
<What is not supported or constrained?>

**Affected Users / Components**
- `<AREA>`

**Impact**
`<IMPACT>`

**Reason**
`<WHY THIS LIMITATION EXISTS>`

**Workaround**
`<WORKAROUND / NONE>`

**Risk**
`<RISK>`

**Removal Condition**
`<WHEN IT CAN BE REMOVED / NOT PLANNED>`

**Related**
- `<FEATURE / ISSUE / ADR / ROADMAP>`

---

## 4. Categories

Possible categories:
- product scope;
- browser/platform compatibility;
- performance/capacity;
- integration;
- data migration;
- accessibility;
- security;
- operations;
- offline/degraded behavior;
- localization.

Use only categories that help discovery.

---

## 5. Explicit Non-Support

Examples:

```text
- Internet Explorer is not supported.
- Multi-region active-active deployment is not currently supported.
- Offline editing is not supported.
```

Only state facts applicable to the project.

---

## 6. Removed Limitations

| ID | Removed On | Resolution |
|---|---|---|
| `<ID>` | `<DATE>` | `<WHAT CHANGED>` |

Preserving resolved entries can help explain past constraints; archive if the list becomes noisy.

---

## 7. Update Triggers

Update this document when:
- a release introduces a meaningful temporary limitation;
- a known limitation is removed;
- a workaround changes;
- a scope decision makes unsupported behavior explicit;
- operations discover a stable constraint users/operators need to know.

---

## 8. Related Documents

- Product Roadmap: `../00_product/ROADMAP.md`
- Feature Specs: `../01_features/`
- Risks: `./RISKS.md`
- Release Checklist: `./RELEASE_CHECKLIST.md`

---

## 9. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
