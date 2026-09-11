# Risk Register — <PROJECT_NAME>

> **Document role:** Track material product, engineering, security, operational, and delivery risks that require explicit ownership or mitigation.
>
> Do not use this file as a list of every imaginable bad outcome.

---

## 1. Risk Scale

### Likelihood
- Low
- Medium
- High

### Impact
- Low
- Medium
- High
- Critical

### Status
- Open
- Mitigating
- Accepted
- Closed
- Materialized

---

## 2. Active Risks

| ID | Risk | Category | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R-001 | `<RISK>` | Product / Tech / Security / Ops / Delivery | `<L>` | `<I>` | `<ACTION>` | `<OWNER>` | Open |

---

## 3. Risk Detail

### R-001 — <RISK_NAME>

**Description**  
<Describe the risk and trigger condition.>

**Potential Impact**
- `<IMPACT>`

**Likelihood**  
`Low / Medium / High`

**Impact**  
`Low / Medium / High / Critical`

**Early Signals**
- `<SIGNAL>`

**Mitigation**
1. `<ACTION>`
2. `<ACTION>`

**Contingency**
`<WHAT TO DO IF IT MATERIALIZES>`

**Owner**
`<OWNER>`

**Review**
`<DATE / MILESTONE>`

---

## 4. Accepted Risks

| ID | Risk | Acceptance Rationale | Owner | Review/Expiry |
|---|---|---|---|---|
| `<ID>` | `<RISK>` | `<RATIONALE>` | `<OWNER>` | `<DATE>` |

Risk acceptance should be deliberate, not merely lack of action.

---

## 5. Materialized Risks / Issues

When a risk becomes an active issue, track operational work in the issue/incident system and keep only the relevant risk context here.

| ID | Materialized On | Tracking Reference | Outcome |
|---|---|---|---|
| `<ID>` | `<DATE>` | `<ISSUE>` | `<STATUS>` |

---

## 6. Closed Risks

| ID | Closed | Reason |
|---|---|---|
| `<ID>` | `<DATE>` | `<MITIGATED / NO LONGER RELEVANT>` |

---

## 7. Review Cadence

Review when:
- roadmap milestone changes;
- major architecture decision is made;
- new critical integration is added;
- new sensitive data is introduced;
- security incident or major defect occurs;
- release risk materially changes.

Avoid arbitrary recurring review if the project does not need it.

---

## 8. Related Documents

- Product Roadmap: `../00_product/ROADMAP.md`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- Threat Model: `../04_engineering/THREAT_MODEL.md`
- Known Limitations: `./KNOWN_LIMITATIONS.md`

---

## 9. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
