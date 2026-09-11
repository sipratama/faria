# Deployment — <PROJECT_NAME>

> **Document role:** Authoritative reference for environment topology, build/release flow, deployment sequencing, migration handling, verification, and rollback.
>
> CI implementation details belong in pipeline configuration and `13_CI_CD_RELEASE.md`.

---

## 1. Deployment Objectives

Deployment should be:
- repeatable;
- observable;
- reversible/recoverable where practical;
- compatible with data migration strategy;
- explicit about environment differences.

---

## 2. Environments

| Environment | Purpose | Promotion Source | Approval |
|---|---|---|---|
| Local | Development | N/A | Developer |
| Test | Automated verification | CI | Automated |
| Staging | Production-like validation | Built artifact | `<RULE>` |
| Production | Live | Same promoted artifact | `<RULE>` |

Adjust to project reality.

---

## 3. Runtime Topology

```text
Internet
   |
<Edge / LB>
   |
   +------ <Frontend>
   |
   +------ <Backend>
               |
        +------+------+
        |             |
      <DB>        <Broker/Cache>
```

Reference System Architecture for detailed boundaries.

---

## 4. Artifact Strategy

Define:
- build once / promote same artifact;
- container/image/package naming;
- immutable version identifier;
- provenance/signing if required.

Example:

```text
<registry>/<service>:<git-sha>
```

Avoid rebuilding different binaries for staging and production when configuration can provide environment variation.

---

## 5. Build

```bash
<BUILD COMMAND>
```

Required checks before artifact publication:
- `<CHECK>`;
- `<CHECK>`.

---

## 6. Database Migration

### Strategy

`<BEFORE APP / DURING DEPLOY / SEPARATE JOB>`

### Rules

- migrations are version controlled;
- production data impact is assessed;
- phased deploys require backward-compatible schema when necessary;
- destructive migration requires explicit rollout/recovery;
- large backfills should be separated when appropriate.

### Sequence

```text
<EXPAND MIGRATION>
      ↓
<COMPATIBLE APP DEPLOY>
      ↓
<DATA BACKFILL>
      ↓
<REMOVE OLD USAGE>
      ↓
<CONTRACT MIGRATION>
```

Use only if project requires expand/contract.

---

## 7. Deployment Procedure

1. `<PRE-CHECK>`
2. `<PUBLISH ARTIFACT>`
3. `<MIGRATION>`
4. `<DEPLOY>`
5. `<HEALTH/READINESS>`
6. `<SMOKE>`
7. `<MONITOR>`
8. `<COMPLETE>`

Automate repeatable steps where practical.

---

## 8. Health and Readiness

Define:
- liveness;
- readiness;
- dependency gating;
- worker health.

A process being alive is not necessarily ready to receive traffic.

---

## 9. Rollout Strategies

Supported:
- direct;
- rolling;
- blue/green;
- canary;
- feature-flagged.

Default:
`<STRATEGY>`

Use complexity proportional to deployment risk.

---

## 10. Rollback / Recovery

### Application Rollback

```bash
<COMMAND/PROCESS>
```

### Database Recovery

`<PROCESS>`

Do not assume schema rollback is always safe. Recovery may require roll-forward.

### Trigger Conditions

Rollback/recovery should be considered when:
- health/readiness fails;
- critical journey fails;
- error rate exceeds threshold;
- data integrity risk appears;
- security regression appears.

---

## 11. Deployment Verification

Verify:
- target version;
- health;
- critical dependencies;
- migration status;
- smoke tests;
- critical metrics;
- error rate;
- queue/worker state where relevant.

---

## 12. Secrets and Configuration

Production secrets are injected through `<MECHANISM>`.

Never bake environment secrets into artifacts.

Reference `CONFIGURATION.md`.

---

## 13. Observability During Release

Monitor:
- deployment events;
- application errors;
- latency;
- saturation;
- dependency errors;
- queue lag;
- critical business signals.

Define observation window based on risk.

---

## 14. Zero-Downtime Requirements

`<REQUIRED / TARGET / NOT REQUIRED>`

If required, document:
- connection draining;
- compatibility window;
- schema compatibility;
- session handling;
- worker deployment order.

---

## 15. Disaster Recovery

Reference NFR for RPO/RTO.

Document:
- backup location;
- restore process;
- service recovery priority;
- DNS/traffic changes if applicable.

---

## 16. Manual Actions

List unavoidable manual steps explicitly.

| Step | Why Manual | Owner | Risk |
|---|---|---|---|
| `<STEP>` | `<RATIONALE>` | `<OWNER>` | `<RISK>` |

Prefer eliminating repeated manual actions over documenting increasingly complex rituals.

---

## 17. Production Access

Define:
- who may deploy;
- who may access production;
- break-glass process;
- audit expectations.

---

## 18. Release Checklist

Use:

`../06_delivery/RELEASE_CHECKLIST.md`

The checklist should reference this document instead of duplicating deployment instructions.

---

## 19. Related Documents

- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- NFR: `../02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`
- Configuration: `./CONFIGURATION.md`
- Runbook: `./RUNBOOK.md`
- Release Checklist: `../06_delivery/RELEASE_CHECKLIST.md`
- CI/CD Standard: `../standards/13_CI_CD_RELEASE.md`

---

## 20. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
