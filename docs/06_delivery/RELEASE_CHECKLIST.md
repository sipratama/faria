# Release Checklist — <PROJECT_NAME>

> **Document role:** A concise release gate to confirm that a specific release is ready to promote.
>
> This checklist references authoritative documentation; it does not duplicate deployment procedures or test strategy.

---

## Release Metadata

| Field | Value |
|---|---|
| Release | `<VERSION / TAG>` |
| Commit / Artifact | `<SHA / IMAGE>` |
| Target Environment | `<ENV>` |
| Release Owner | `<OWNER>` |
| Date | `<YYYY-MM-DD>` |

---

## 1. Scope

- [ ] release scope matches intended PRD/feature scope;
- [ ] no unintended features/refactors are included;
- [ ] known deferred items are explicit;
- [ ] breaking changes are identified.

---

## 2. Requirements and Documentation

- [ ] relevant feature specs are current;
- [ ] required acceptance criteria are met;
- [ ] API/event contracts are synchronized;
- [ ] architecture docs/ADRs are updated where required;
- [ ] known limitations are current.

---

## 3. Build and Artifact

- [ ] CI required checks pass;
- [ ] release artifact is immutable/versioned;
- [ ] artifact provenance/version is identifiable;
- [ ] no local/uncommitted dependency is required.

---

## 4. Testing

- [ ] required unit tests pass;
- [ ] required integration/contract tests pass;
- [ ] selected E2E/critical journey tests pass;
- [ ] regression tests for included defect fixes pass;
- [ ] performance/security verification completed when required.

Record evidence:

```text
<CI RUN / COMMAND / RESULT>
```

---

## 5. Security

- [ ] no known exposed secrets;
- [ ] required dependency/security scans completed;
- [ ] authorization/security-sensitive changes reviewed;
- [ ] new trust boundaries reflected in threat model;
- [ ] critical unresolved vulnerabilities have explicit disposition.

---

## 6. Database / Data

- [ ] migrations reviewed;
- [ ] existing data impact assessed;
- [ ] migration order is compatible with deployment order;
- [ ] destructive changes have recovery/rollout plan;
- [ ] backup/recovery requirements are satisfied when needed.

---

## 7. Configuration and Secrets

- [ ] required configuration exists in target environment;
- [ ] new variables are documented;
- [ ] production secrets are sourced from approved mechanism;
- [ ] feature flags/defaults match release intent.

---

## 8. Deployment Readiness

- [ ] deployment procedure is current;
- [ ] target artifact/version is confirmed;
- [ ] rollback or roll-forward recovery is understood;
- [ ] required access/approval is available;
- [ ] maintenance window is known if needed.

---

## 9. Observability

- [ ] critical metrics/logs/traces exist for changed behavior;
- [ ] dashboards/alerts updated where required;
- [ ] release can be correlated to telemetry;
- [ ] expected post-deploy signals are known.

---

## 10. External Dependencies

- [ ] third-party production credentials/config are valid;
- [ ] quota/capacity risk considered;
- [ ] contract/provider changes verified;
- [ ] webhook/callback configuration verified where relevant.

---

## 11. Product / UX

- [ ] critical user journeys verified;
- [ ] loading/empty/error states are acceptable;
- [ ] permissions/roles verified;
- [ ] responsive/accessibility checks completed where required;
- [ ] user-facing copy/config is production-ready.

---

## 12. Go / No-Go

### Remaining Risks

- `<RISK>`

### Accepted Limitations

- `<LIMITATION>`

### Decision

`GO / NO-GO`

**Approved By:** `<OWNER>`  
**Time:** `<TIMESTAMP>`

---

## 13. Post-Deploy Verification

- [ ] deployment completed;
- [ ] health/readiness passes;
- [ ] migrations completed as expected;
- [ ] smoke tests pass;
- [ ] critical user journey works;
- [ ] error/latency metrics are within expected range;
- [ ] queues/workers healthy where relevant;
- [ ] no unexpected security/data issue observed.

---

## 14. Release Completion

- [ ] release tag/version recorded;
- [ ] changelog/release notes updated if project uses them;
- [ ] rollback window/monitoring period completed as required;
- [ ] follow-up items created for non-blocking issues.

---

## 15. References

- Deployment: `../05_operations/DEPLOYMENT.md`
- Test Strategy: `../04_engineering/TEST_STRATEGY.md`
- Threat Model: `../04_engineering/THREAT_MODEL.md`
- Risks: `./RISKS.md`
- Known Limitations: `./KNOWN_LIMITATIONS.md`
- CI/CD Standard: `../standards/13_CI_CD_RELEASE.md`
