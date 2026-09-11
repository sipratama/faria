# Operations Runbook — <PROJECT_NAME>

> **Document role:** Action-oriented procedures for diagnosing and recovering from known production operational conditions.
>
> This is not architecture documentation and not an incident diary. Procedures should be executable, safe, and kept current.

---

## 1. Service Overview

| Service / Component | Purpose | Owner | Criticality |
|---|---|---|---|
| `<SERVICE>` | `<PURPOSE>` | `<OWNER>` | Low/Med/High |

---

## 2. Operational Links

| Resource | Location |
|---|---|
| Dashboard | `<LINK>` |
| Logs | `<LINK>` |
| Traces | `<LINK>` |
| Alerts | `<LINK>` |
| Deployment | `<LINK>` |
| Status page | `<LINK/N/A>` |

Do not place credentials here.

---

## 3. First Response Checklist

When an incident is suspected:

1. identify affected capability/users;
2. confirm whether issue is ongoing;
3. check recent deployments/config changes;
4. inspect high-level health/metrics;
5. identify failing component/dependency;
6. mitigate user impact before deep root-cause work when appropriate;
7. preserve relevant evidence;
8. communicate according to project incident process.

---

## 4. Service Health

### Expected Healthy State

- `<SIGNAL>`;
- `<SIGNAL>`.

### Health Commands

```bash
<COMMAND>
```

### Key Metrics

| Metric | Normal | Concern |
|---|---|---|
| `<METRIC>` | `<RANGE>` | `<THRESHOLD>` |

---

## 5. Common Incident Procedures

### RB-001 — Elevated Error Rate

**Symptoms**
- `<SYMPTOM>`

**Check**
1. `<STEP>`
2. `<STEP>`

**Likely Causes**
- `<CAUSE>`

**Mitigation**
1. `<SAFE ACTION>`

**Escalate When**
- `<CONDITION>`

**Recovery Verification**
- `<CHECK>`

---

### RB-002 — Database Connectivity

**Symptoms**
- `<SYMPTOM>`

**Check**
```bash
<COMMAND>
```

**Mitigation**
- `<ACTION>`

Do not restart/delete data stores as a default troubleshooting step without understanding impact.

---

### RB-003 — Queue / Worker Backlog

**Symptoms**
- queue lag;
- delayed processing;
- rising retry/dead-letter volume.

**Check**
- broker health;
- consumer health;
- processing latency;
- poison message pattern;
- downstream dependency.

**Mitigation**
`<ACTION>`

---

## 6. External Dependency Failure

| Dependency | User Impact | Degraded Behavior | Escalation |
|---|---|---|---|
| `<SERVICE>` | `<IMPACT>` | `<BEHAVIOR>` | `<WHEN>` |

---

## 7. Deployment Failure

Check:
- target artifact;
- rollout state;
- readiness;
- migration state;
- configuration;
- secrets;
- recent logs.

Recovery:
`<ROLLBACK/ROLL-FORWARD PROCEDURE>`

Reference `DEPLOYMENT.md`.

---

## 8. Migration Failure

Before any action:
- determine whether migration is partially applied;
- do not rerun destructive steps blindly;
- check migration tool state;
- preserve evidence;
- assess data integrity.

Recovery:
`<PROJECT-SPECIFIC PROCEDURE>`

---

## 9. High Latency

Check:
- request breakdown/traces;
- database queries;
- connection pools;
- dependency latency;
- saturation;
- cache behavior;
- queue delay.

Mitigation:
`<ACTION>`

---

## 10. Resource Saturation

### CPU
`<CHECK/ACTION>`

### Memory
`<CHECK/ACTION>`

### Disk
`<CHECK/ACTION>`

### Connection Pool
`<CHECK/ACTION>`

Avoid scaling blindly if the underlying failure is a leak or runaway workload.

---

## 11. Security Incident First Actions

If credential/token exposure or unauthorized access is suspected:
- restrict further exposure;
- rotate/revoke affected credentials when safe;
- preserve audit evidence;
- identify affected accounts/data;
- follow security incident escalation;
- avoid deleting evidence during cleanup.

Project-specific security incident procedure may live separately for regulated/high-risk projects.

---

## 12. Data Recovery

### Backup Location
`<REFERENCE>`

### Restore Procedure
`<PROCEDURE/LINK>`

### Verification
- integrity check;
- expected latest data according to RPO;
- application compatibility;
- user-critical flow.

---

## 13. Feature Disable / Kill Switch

| Capability | Mechanism | Impact |
|---|---|---|
| `<FEATURE>` | `<FLAG/CONFIG>` | `<IMPACT>` |

Only document mechanisms that actually exist.

---

## 14. Cache Recovery

`<SAFE CLEAR/INVALIDATION PROCEDURE>`

Warn when cache clearing may create load spikes or user-visible effects.

---

## 15. Dead-Letter / Failed Jobs

Procedure:
1. inspect cause;
2. determine whether retry is safe;
3. correct underlying issue;
4. replay with idempotency awareness;
5. verify downstream state.

Never bulk replay unknown failed operations solely to clear a queue.

---

## 16. Escalation

| Severity | Condition | Escalation |
|---|---|---|
| SEV-1 | `<CONDITION>` | `<PATH>` |
| SEV-2 | `<CONDITION>` | `<PATH>` |
| SEV-3 | `<CONDITION>` | `<PATH>` |

---

## 17. After Recovery

- verify critical user flow;
- verify metrics return to expected range;
- verify queues/backlogs recover;
- document remaining risk;
- create follow-up work for root cause;
- update runbook if procedure was incomplete or incorrect.

---

## 18. Safety Rules

Do not:
- run destructive commands without understanding scope;
- bypass authorization/security to restore service unless an approved emergency process exists;
- expose secrets in screenshots/logs;
- delete evidence prematurely;
- claim recovery until user-impacting behavior is verified.

---

## 19. Related Documents

- Deployment: `./DEPLOYMENT.md`
- Configuration: `./CONFIGURATION.md`
- System Architecture: `../02_architecture/SYSTEM_ARCHITECTURE.md`
- NFR: `../02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`
- Risks: `../06_delivery/RISKS.md`

---

## 20. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
