# Dependency and Supply Chain Standard

> **Purpose:** Define reusable rules for third-party libraries, packages, containers, build tools, licenses, provenance, and software supply-chain risk.

---

## 1. Core Principle

Every dependency adds capability and responsibility.

A dependency SHOULD earn its maintenance, security, runtime, and supply-chain cost.

Prefer fewer well-understood dependencies over unnecessary package accumulation.

---

## 2. Before Adding a Dependency

Evaluate:

- what problem it solves;
- whether existing platform/project capability already solves it;
- maintenance activity;
- ecosystem adoption;
- security history;
- license;
- transitive dependency weight;
- runtime/bundle impact;
- lock-in;
- replacement difficulty.

Do not add a dependency solely to avoid writing a few lines of stable straightforward code.

---

## 3. Direct vs Transitive Dependencies

Projects SHOULD understand important transitive dependencies for:
- security;
- licensing;
- runtime conflicts;
- image/bundle size.

Critical transitive packages SHOULD be visible through tooling such as lockfiles/SBOM/dependency reports.

---

## 4. Lockfiles

Applications SHOULD commit ecosystem lockfiles when they provide reproducible dependency resolution.

Examples:
- `package-lock.json`;
- `pnpm-lock.yaml`;
- `yarn.lock`;
- `poetry.lock`;
- generated dependency lock equivalents.

Do not hand-edit lockfiles unless ecosystem workflow requires it.

---

## 5. Version Ranges

Use version ranges intentionally.

Production applications SHOULD favor predictable reproducible resolution.

Avoid broad unconstrained ranges for critical dependencies.

---

## 6. Dependency Updates

Dependencies SHOULD be updated regularly enough to avoid large unsafe jumps.

Updates SHOULD consider:
- release notes;
- breaking changes;
- migration;
- security;
- tests.

Automated update tools MAY be used.

Do not auto-merge high-risk dependency upgrades without adequate verification.

---

## 7. Vulnerabilities

Known vulnerabilities SHOULD be triaged based on:
- affected version;
- exploitability;
- reachable code path;
- exposure;
- asset impact;
- available fix/mitigation.

Scanner severity alone is not complete risk analysis.

Critical exploitable vulnerabilities SHOULD receive urgent action.

---

## 8. Vulnerability Suppression

Suppressions/exceptions MUST include:
- rationale;
- scope;
- owner;
- review/expiry where appropriate.

Do not permanently ignore scanner findings without context.

---

## 9. License Review

Dependencies MUST use licenses compatible with project distribution/business model.

Projects SHOULD track licenses for direct and material transitive dependencies.

Unknown/custom licenses SHOULD be reviewed.

Open-source project profiles MAY require stricter license policy.

---

## 10. Copyleft

Strong copyleft dependencies SHOULD be evaluated explicitly for distribution implications.

Do not assume "open source" automatically means safe for every proprietary distribution model.

Legal review MAY be required for material uncertainty.

---

## 11. Package Source

Dependencies SHOULD come from trusted official registries/repositories.

Avoid:
- random binary downloads;
- abandoned unofficial mirrors;
- unsigned artifacts when ecosystem provides verification.

Private registries SHOULD have controlled publishing permissions.

---

## 12. Typosquatting

Engineers SHOULD verify package identity before installation.

Check:
- exact name;
- publisher/organization;
- repository;
- documentation.

Do not install a package solely from an AI suggestion without verifying it exists and is legitimate.

---

## 13. Package Scripts

Package install/build scripts can execute code.

CI/build environments SHOULD treat third-party install scripts as supply-chain execution risk.

Disable or restrict scripts when ecosystem/workflow permits and risk warrants.

---

## 14. Container Base Images

Container images SHOULD use:
- maintained bases;
- explicit tags/digests where reproducibility matters;
- minimal required runtime;
- trusted registries.

Avoid `latest` for production deployment.

---

## 15. Image Scanning

Production container images SHOULD be scanned at risk-appropriate cadence.

Findings SHOULD be triaged like other dependency vulnerabilities.

---

## 16. Image Provenance

Projects with higher supply-chain risk SHOULD preserve:
- build source;
- commit SHA;
- image digest;
- builder identity;
- signing/attestation where appropriate.

---

## 17. SBOM

Projects MAY generate Software Bill of Materials.

SBOM is especially useful for:
- enterprise;
- regulated;
- distributed binaries;
- incident response.

An SBOM SHOULD derive from actual built artifacts/dependency resolution where possible.

---

## 18. Build Tools

Build plugins/tools are also dependencies.

They SHOULD be reviewed for:
- maintenance;
- arbitrary code execution;
- compatibility;
- source.

Do not trust build-time dependencies more than runtime dependencies.

---

## 19. Generated Code Tools

Code generators SHOULD be:
- versioned;
- reproducible;
- documented;
- pinned appropriately.

Generated output SHOULD be traceable to generator + source contract.

---

## 20. Vendor SDKs

Vendor SDKs SHOULD be isolated when:
- semantics are vendor-specific;
- replacement is plausible;
- testing needs a boundary;
- SDK creates wide coupling.

Do not wrap SDKs automatically when the abstraction adds no value.

---

## 21. Runtime Plugins

Plugin systems that load code dynamically require explicit trust policy.

Define:
- who can publish/install;
- signature/verification;
- permissions;
- isolation.

Do not load arbitrary remote code into trusted runtime by default.

---

## 22. Private Packages

Private package publishing SHOULD use:
- least privilege;
- protected publishing identity;
- provenance/versioning;
- clear ownership.

Avoid shared long-lived developer tokens for CI publishing.

---

## 23. Secrets in Package Managers

Registry credentials MUST:
- come from secret management;
- not be committed;
- use least scope;
- be rotated/revoked when exposed.

---

## 24. Reproducible Builds

Builds SHOULD be reproducible enough to map:

```text
source commit
+ dependency lock
+ build config
→ artifact
```

Environment-specific configuration SHOULD be injected at runtime where appropriate.

---

## 25. Dependency Removal

Unused dependencies SHOULD be removed.

Dead dependencies:
- increase attack surface;
- slow builds;
- confuse architecture;
- create license obligations.

---

## 26. Frontend Dependencies

Frontend dependency review SHOULD additionally consider:
- bundle size;
- browser compatibility;
- accessibility;
- SSR/hydration behavior;
- tree-shaking.

Do not add a large UI library for one trivial component without comparison.

---

## 27. Native / Binary Dependencies

Native/binary dependencies SHOULD consider:
- target platform support;
- security updates;
- build reproducibility;
- architecture compatibility.

Prefer ecosystem-standard maintained binaries.

---

## 28. Dependency Ownership

Critical dependencies SHOULD have a clear module/team owner.

Owner should understand:
- why it exists;
- upgrade path;
- operational impact.

---

## 29. End-of-Life Dependencies

EOL runtimes/frameworks MUST have an explicit migration or risk acceptance plan.

Do not silently run unsupported critical infrastructure indefinitely.

---

## 30. AI-Selected Dependencies

AI agents MUST NOT install new dependencies merely because they are familiar with them.

Before adding:
1. verify package existence/source;
2. inspect current project capabilities;
3. justify need;
4. assess maintenance/security/license;
5. keep scope minimal.

Prefer project-established dependencies.

---

## 31. Supply Chain Review Checklist

Review:
- package identity;
- need;
- license;
- maintenance;
- vulnerabilities;
- version/pinning;
- transitive impact;
- runtime/bundle cost;
- registry/provenance;
- secrets;
- test evidence.

---

## 32. Exceptions

Dependency risk exceptions SHOULD be explicit and reviewed.

High-risk proprietary/abandoned dependencies SHOULD have an exit/mitigation plan.
