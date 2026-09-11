# Threat Model — <PROJECT_NAME>

> **Document role:** Authoritative project-level reference for assets, trust boundaries, threat scenarios, security assumptions, mitigations, and residual risk.
>
> Implementation rules belong in `08_SECURITY_STANDARD.md`. Feature-specific security behavior belongs in relevant feature specs.

---

## 1. Scope

### In Scope
- `<SYSTEM / COMPONENT>`
- `<DATA FLOW>`
- `<INTEGRATION>`

### Out of Scope
- `<ITEM>`

### Assumptions
- `<ASSUMPTION>`

---

## 2. Security Objectives

1. Protect `<ASSET>` from unauthorized disclosure.
2. Protect `<ASSET>` from unauthorized modification.
3. Preserve availability of `<CRITICAL CAPABILITY>`.
4. Ensure privileged actions are attributable where required.

Adapt to actual risk.

---

## 3. Assets

| Asset | Sensitivity | Impact if Compromised |
|---|---|---|
| `<ASSET>` | Public / Internal / Confidential / Sensitive / Restricted | `<IMPACT>` |

Examples:
- credentials/tokens;
- personal data;
- payment state;
- business records;
- admin capability;
- cryptographic keys;
- source/config secrets.

---

## 4. Actors

| Actor | Trust Level | Capabilities |
|---|---|---|
| Anonymous user | Untrusted | `<CAPABILITY>` |
| Authenticated user | Partially trusted | `<CAPABILITY>` |
| Admin | Privileged | `<CAPABILITY>` |
| External service | External trust | `<CAPABILITY>` |
| Operator | Privileged | `<CAPABILITY>` |

---

## 5. Trust Boundaries

```text
Internet
   |
   | TB-01
   v
Frontend / Edge
   |
   | TB-02
   v
Backend
   |
   +---- TB-03 ----> Third Party
   |
   | TB-04
   v
Database / Internal Infrastructure
```

### Boundary Catalog

| ID | Boundary | Validation / Control |
|---|---|---|
| TB-01 | `<BOUNDARY>` | `<CONTROL>` |

---

## 6. Entry Points

| Entry Point | Actor | Data | Authentication |
|---|---|---|---|
| `<ENDPOINT/UI/EVENT>` | `<ACTOR>` | `<DATA>` | `<MECHANISM>` |

Include:
- HTTP APIs;
- webhooks;
- file uploads;
- message consumers;
- admin interfaces;
- background job inputs;
- import/export;
- callback URLs.

---

## 7. Data Flow

Document security-relevant flows.

### DF-01 — <FLOW>

```text
Actor
  ↓
Entry Point
  ↓
Validation
  ↓
Authorization
  ↓
Processing
  ↓
Storage / External System
```

**Sensitive Data:** `<DATA>`  
**Trust Boundaries Crossed:** `TB-...`

---

## 8. Threat Identification

Use STRIDE or another appropriate method as a prompt, not as bureaucracy.

### Threat Catalog

| ID | Threat | Asset / Boundary | Likelihood | Impact | Status |
|---|---|---|---|---|---|
| T-001 | `<THREAT>` | `<ASSET>` | Low/Med/High | Low/Med/High | Open/Mitigated/Accepted |

Potential categories:
- spoofing;
- tampering;
- repudiation;
- information disclosure;
- denial of service;
- elevation of privilege.

---

## 9. Threat Detail

### T-001 — <THREAT_NAME>

**Scenario**  
<How could the threat occur?>

**Preconditions**
- `<PRECONDITION>`

**Affected Assets**
- `<ASSET>`

**Impact**
`<IMPACT>`

**Likelihood**
`Low / Medium / High`

**Mitigations**
- `<CONTROL>`
- `<CONTROL>`

**Detection**
- `<LOG/METRIC/ALERT/AUDIT>`

**Residual Risk**
`<RISK>`

**Owner**
`<OWNER>`

---

## 10. Authentication Threats

Consider:
- credential stuffing;
- brute force;
- token theft;
- session fixation;
- session expiration;
- password reset abuse;
- MFA bypass;
- OAuth/OIDC redirect abuse.

Project requirements:
- `<REQUIREMENT>`

---

## 11. Authorization Threats

Consider:
- IDOR/BOLA;
- horizontal privilege escalation;
- vertical privilege escalation;
- tenant isolation;
- admin action abuse;
- missing ownership validation.

Authoritative authorization must be enforced server-side at the defined security boundary.

---

## 12. Input and Injection Threats

Consider:
- SQL/NoSQL injection;
- command injection;
- template injection;
- XSS;
- path traversal;
- unsafe deserialization;
- malformed payload;
- oversized input.

Controls:
- `<CONTROL>`

---

## 13. File Handling

If applicable, assess:
- file type validation;
- content sniffing;
- filename/path handling;
- malware;
- oversized files;
- public/private access;
- signed URLs;
- metadata leakage;
- decompression bombs.

---

## 14. Integration and Webhook Threats

Consider:
- forged callback;
- replay;
- signature validation;
- SSRF;
- DNS/rebinding risks;
- timeout/resource exhaustion;
- credential leakage;
- untrusted third-party response.

---

## 15. Event/Messaging Threats

Consider:
- unauthorized producer/consumer;
- forged event;
- replay/duplicate;
- poison message;
- sensitive payload;
- schema abuse;
- cross-tenant event leakage.

---

## 16. Secrets and Cryptography

Requirements:
- secrets are not committed;
- secrets come from approved runtime secret/config mechanism;
- key rotation is possible where risk requires;
- approved cryptographic primitives/libraries are used;
- do not design custom cryptography without exceptional justification.

---

## 17. Logging and Telemetry Threats

Do not log:
- passwords;
- access/refresh tokens;
- private keys;
- full payment credentials;
- unnecessary PII;
- sensitive request bodies.

Audit/security logs should still provide sufficient attribution and correlation.

---

## 18. Privacy Threats

Consider:
- over-collection;
- excessive retention;
- unauthorized analytics;
- export leakage;
- account deletion gaps;
- inference from metadata;
- cross-user exposure.

Reference `DATA_MODEL.md`.

---

## 19. Availability / Abuse

Consider:
- rate abuse;
- resource exhaustion;
- expensive search/query;
- upload abuse;
- queue flooding;
- third-party quota exhaustion;
- automated spam.

Controls should be proportional to actual risk.

---

## 20. Security Verification

| Threat / Control | Verification |
|---|---|
| `<CONTROL>` | Unit / integration / security test / review / scan |

High-risk controls should have repeatable evidence where practical.

---

## 21. Accepted Risks

| Risk | Reason Accepted | Owner | Review / Expiry |
|---|---|---|---|
| `<RISK>` | `<RATIONALE>` | `<OWNER>` | `<DATE>` |

Accepted risk is a decision, not an ignored open threat.

---

## 22. Update Triggers

Review/update threat model when:
- new trust boundary is introduced;
- authentication/authorization changes;
- sensitive data changes;
- payment/admin/file upload capability is added;
- new external integration is added;
- deployment exposure changes;
- significant vulnerability/incident reveals a missing threat.

---

## 23. Related Documents

- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- Data Model: `../02_architecture/DATA_MODEL.md`
- NFR: `../02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`
- Security Standard: `../standards/08_SECURITY_STANDARD.md`
- Test Strategy: `./TEST_STRATEGY.md`
- Risks: `../06_delivery/RISKS.md`

---

## 24. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
