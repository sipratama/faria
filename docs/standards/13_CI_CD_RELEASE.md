# CI/CD and Release Standard

> **Purpose:** Define reusable rules for automated verification, artifact creation, environment promotion, deployment safety, and release evidence.
>
> Concrete deployment topology/procedure belongs in `DEPLOYMENT.md`. Release-specific go/no-go checks belong in `RELEASE_CHECKLIST.md`.

---

## 1. Core Principle

CI/CD should make safe changes repeatable.

A release SHOULD be traceable from:

```text
source commit
   ↓
verified build
   ↓
immutable artifact
   ↓
environment promotion
   ↓
deployment
   ↓
post-deploy verification
```

Avoid manual steps that cannot be reproduced or audited when automation is practical.

---

## 2. CI Goals

CI SHOULD provide:
- fast feedback;
- repeatability;
- required quality gates;
- security checks;
- artifact generation;
- useful failure evidence.

CI MUST NOT be designed merely to "turn green."

---

## 3. Pipeline Stages

A typical pipeline MAY include:

```text
validate
  ↓
build
  ↓
unit/component
  ↓
integration/contract
  ↓
security
  ↓
package
  ↓
publish
  ↓
deploy
  ↓
smoke
```

The project MAY combine/reorder stages based on architecture and speed.

---

## 4. Fast Feedback

Fast checks SHOULD run early:

- formatting/lint;
- type/compile;
- unit tests;
- static analysis.

Expensive checks MAY run later or conditionally.

Do not delay obvious failures behind long integration suites.

---

## 5. Required Checks

Protected branches SHOULD require project-appropriate checks.

Examples:
- build;
- test;
- contract;
- migration;
- security scan.

Do not require meaningless gates merely for process appearance.

---

## 6. Deterministic Environment

CI SHOULD pin important runtime/tool versions.

Builds MUST NOT depend on undeclared developer-machine state.

CI configuration SHOULD be version controlled.

---

## 7. Secrets

CI secrets MUST:
- come from protected secret storage;
- be scoped to job/environment;
- not be printed;
- not be exposed to untrusted fork/PR contexts.

Production secrets SHOULD be inaccessible to routine test jobs.

---

## 8. Untrusted Contributions

CI MUST treat external/untrusted code as potentially malicious.

Do not automatically expose:
- deployment credentials;
- package publish tokens;
- cloud credentials

to arbitrary pull request code.

---

## 9. Build Once

Where practical, build the application artifact once and promote the same immutable artifact through environments.

Prefer:

```text
commit SHA → image digest
```

over rebuilding different binaries for staging/production.

---

## 10. Artifact Versioning

Artifacts SHOULD include traceable version identity.

Examples:
- semantic version;
- git SHA;
- build number;
- image digest.

Avoid mutable production tags as the only identity.

---

## 11. Artifact Integrity

Higher-risk projects MAY use:
- checksums;
- signatures;
- attestations;
- provenance.

Artifact integrity controls SHOULD align with supply-chain risk.

---

## 12. Caching in CI

CI caches MAY improve speed.

Caches MUST NOT:
- make builds non-reproducible;
- leak secrets;
- mix incompatible tool versions.

Cache invalidation SHOULD include relevant lock/config changes.

---

## 13. Test Parallelism

Parallel tests MAY reduce pipeline time.

Shared external resources MUST be isolated to prevent race/flakiness.

Do not trade determinism for speed.

---

## 14. Flaky CI

Flaky pipelines are defects.

Do not normalize:
- rerun until green;
- random integration failures;
- hidden retry of failed tests.

Temporary retry MAY exist during incident mitigation but SHOULD NOT hide persistent instability.

---

## 15. Security Scans

CI SHOULD run risk-appropriate:
- secret scan;
- dependency scan;
- SAST;
- container scan;
- IaC scan.

Blocking policy SHOULD distinguish real critical risk from noisy findings.

---

## 16. Contract Verification

Contract changes SHOULD be verified in CI when tooling permits.

Examples:
- OpenAPI lint/validation;
- generated client consistency;
- AsyncAPI/schema validation;
- backward compatibility check.

---

## 17. Migration Verification

Database changes SHOULD have CI validation.

At minimum:
- migrations apply;
- schema starts clean.

Higher-risk projects SHOULD also test upgrade from prior schema/data.

---

## 18. Environment Promotion

Promotion SHOULD be explicit.

Typical:

```text
main build
  ↓
staging
  ↓
verification
  ↓
production
```

Projects MAY use direct production deploy for low-risk systems when appropriate.

---

## 19. Environment Configuration

Environment-specific behavior SHOULD come from controlled configuration/secrets, not different source branches.

Avoid:
- `production` code branch diverging from `main`;
- manually edited server files;
- undocumented environment patches.

---

## 20. Deployment Approval

Approval policy SHOULD reflect risk.

Examples:
- automated for low-risk staging;
- manual approval for production;
- multi-party approval for regulated systems.

Do not add approval steps with no real risk-control value.

---

## 21. Migration Ordering

Deployment pipeline MUST define migration/application ordering.

Phased deployments SHOULD preserve compatibility across old/new versions where required.

Do not deploy code requiring a schema that is not yet available.

---

## 22. Rollout Strategies

Supported strategies MAY include:
- rolling;
- blue/green;
- canary;
- direct replace;
- feature flag.

Choose based on:
- risk;
- platform;
- rollback needs;
- cost.

Do not use complex rollout infrastructure solely for sophistication.

---

## 23. Feature Flags

Feature flags MAY decouple deployment from release.

Flags SHOULD define:
- default;
- owner;
- rollout plan;
- removal condition.

Do not leave permanent stale flags.

---

## 24. Rollback

Deployment SHOULD have an understood recovery path.

Application rollback may not imply DB rollback.

When schema is not backward compatible, prefer roll-forward or phased migration.

Do not advertise "one-click rollback" if data changes make it unsafe.

---

## 25. Post-Deploy Verification

Deployments SHOULD verify:
- target version;
- health/readiness;
- smoke tests;
- critical metrics;
- queue/worker status;
- migration completion;
- critical business flow where appropriate.

---

## 26. Deployment Markers

Observability SHOULD record deployments/config changes to correlate incidents.

---

## 27. Release Gates

Production release SHOULD consider:
- required tests;
- security findings;
- migration risk;
- unresolved critical defects;
- known limitations;
- rollback/recovery;
- operations readiness.

Use `RELEASE_CHECKLIST.md`.

---

## 28. Release Notes / Changelog

Projects SHOULD maintain release communication appropriate to audience.

Public libraries/products MAY need semantic changelog.

Internal services MAY rely on deployment records/issues.

Do not maintain duplicate release notes nobody uses.

---

## 29. Semantic Versioning

Libraries/public contracts SHOULD consider semantic versioning where consumer expectations benefit.

Applications MAY use product version/tag schemes better suited to deployment.

Versioning policy SHOULD be explicit.

---

## 30. Hotfixes

Hotfixes MAY use shortened workflow.

However:
- change must be traceable;
- tests should be as strong as time permits;
- production branch divergence should be reconciled immediately;
- missing documentation/test debt should be repaired.

---

## 31. Failed Deployment

Failed deployment SHOULD stop promotion automatically where possible.

Recovery process SHOULD define:
- rollback/roll-forward;
- migration state;
- traffic state;
- alerting.

Do not continue promotion after critical verification failure.

---

## 32. Pipeline Permissions

CI/CD identities SHOULD use least privilege.

Separate:
- read/build;
- package publish;
- staging deploy;
- production deploy

when risk warrants.

---

## 33. Infrastructure as Code

Infrastructure SHOULD be version controlled where practical.

Manual infrastructure changes SHOULD be minimized and reconciled.

IaC changes SHOULD be reviewed/tested proportionally to risk.

---

## 34. Ephemeral Environments

Ephemeral preview/test environments MAY improve verification.

They SHOULD:
- use non-production secrets/data;
- have lifecycle cleanup;
- avoid uncontrolled cost.

---

## 35. Production Data in CI

CI MUST NOT use production data unless an explicitly approved protected process exists.

Prefer synthetic/anonymized data.

---

## 36. Release Evidence

A release SHOULD be able to answer:

```text
What commit?
What artifact?
What tests?
What migrations?
What environment?
Who/what approved?
What version is running?
```

---

## 37. Pipeline Review Checklist

Review:
- runtime pinning;
- secret scope;
- untrusted PR handling;
- fast feedback;
- required gates;
- artifact identity;
- migration check;
- security scans;
- deployment recovery;
- post-deploy evidence.

---

## 38. Exceptions

Early-stage projects MAY use simpler CI/CD.

However, production releases SHOULD remain traceable and reproducible enough to diagnose what was deployed.
