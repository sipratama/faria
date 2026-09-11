# ADR-XXXX — <DECISION_TITLE>

> **Document role:** Record one material architecture decision, its context, alternatives, and consequences.
>
> ADRs explain **why a decision was made**. `SYSTEM_ARCHITECTURE.md` describes the resulting current architecture.

---

## Metadata

| Field | Value |
|---|---|
| ADR | `ADR-XXXX` |
| Status | Proposed / Accepted / Rejected / Superseded / Deprecated |
| Date | `<YYYY-MM-DD>` |
| Decision Owners | `<OWNER(S)>` |
| Related Requirements | `<FEATURE / NFR / CAPABILITY IDs>` |
| Supersedes | `<ADR OR N/A>` |
| Superseded By | `<ADR OR N/A>` |

---

## 1. Context

<Describe the problem, constraints, forces, and why a decision is needed now.>

Include only context necessary to understand the decision.

Relevant considerations may include:

- product requirements;
- architecture boundaries;
- expected scale;
- security;
- reliability;
- team capability;
- operational complexity;
- cost;
- compatibility;
- migration constraints.

---

## 2. Decision Drivers

Prioritized drivers:

1. `<DRIVER>`
2. `<DRIVER>`
3. `<DRIVER>`

Do not list every desirable property. Identify what actually determines the choice.

---

## 3. Considered Options

### Option A — <NAME>

**Summary**  
<DESCRIPTION>

**Advantages**
- `<ADVANTAGE>`

**Disadvantages**
- `<DISADVANTAGE>`

**Risks**
- `<RISK>`

---

### Option B — <NAME>

**Summary**  
<DESCRIPTION>

**Advantages**
- `<ADVANTAGE>`

**Disadvantages**
- `<DISADVANTAGE>`

**Risks**
- `<RISK>`

---

### Option C — <NAME>

Optional.

---

## 4. Decision

We will:

> **<CLEAR DECISION STATEMENT>**

### Scope

This decision applies to:

- `<SCOPE>`

This decision does not imply:

- `<NON-SCOPE / MISINTERPRETATION>`

---

## 5. Rationale

<Explain why the selected option best satisfies the decision drivers.>

Focus on tradeoffs rather than claiming the chosen option is universally superior.

---

## 6. Consequences

### Positive

- `<CONSEQUENCE>`

### Negative / Cost

- `<CONSEQUENCE>`

### Risks

- `<RISK>`

### Required Follow-Up

- `<ACTION>`
- `<ACTION>`

---

## 7. Architecture Invariants Introduced or Changed

If applicable:

- `INV-XX — <INVARIANT>`

If this ADR changes an invariant in `SYSTEM_ARCHITECTURE.md`, update that document when the ADR is accepted.

---

## 8. Compatibility and Migration

`<N/A OR DESCRIPTION>`

Cover when relevant:

- existing data;
- API consumers;
- event consumers;
- deployment sequencing;
- rollback;
- deprecation.

---

## 9. Security / Reliability Impact

### Security

`<NONE / IMPACT>`

### Reliability

`<NONE / IMPACT>`

### Operational Complexity

`<NONE / IMPACT>`

---

## 10. Validation

How will we know the decision works as intended?

- `<TEST / METRIC / SPIKE / PRODUCTION SIGNAL>`

If a time-boxed experiment is required before acceptance, keep the ADR `Proposed` until evidence is sufficient.

---

## 11. References

- `<PRD / FEATURE SPEC / NFR>`
- `<EXTERNAL DOCUMENTATION>`
- `<BENCHMARK / PROTOTYPE>`
- `<RELATED ADR>`

---

## 12. Decision History

| Date | Status | Change |
|---|---|---|
| `<YYYY-MM-DD>` | Proposed | Initial proposal |
| `<YYYY-MM-DD>` | Accepted | `<WHY>` |
