# Security Engineering Standard

> **Purpose:** Define reusable implementation rules for secure software development.
>
> `THREAT_MODEL.md` identifies project threats and trust boundaries. This standard defines baseline engineering controls. Project-specific security requirements or regulations may strengthen these rules.

---

## 1. Core Principle

Security is enforced at trusted boundaries, not assumed from client behavior.

All external input is untrusted until validated.

Authorization MUST protect authoritative operations regardless of UI visibility.

Secrets MUST remain secret throughout source, logs, artifacts, CI, and runtime.

---

## 2. Secure Defaults

Security-sensitive defaults MUST fail closed where practical.

Examples:
- protected endpoint defaults to denied;
- unknown role does not gain access;
- invalid signature is rejected;
- missing secret does not silently disable verification.

Avoid "development convenience" defaults that can accidentally reach production.

---

## 3. Threat-Driven Security

Security controls SHOULD be proportional to:
- asset sensitivity;
- trust boundary;
- likelihood;
- impact.

Do not add ceremonial controls while leaving higher-risk flows unprotected.

Update the threat model when a change introduces a material new threat or boundary.

---

## 4. Authentication

Authentication MUST use established mechanisms/libraries/providers appropriate to the architecture.

Applications MUST NOT:
- implement custom password hashing;
- accept unsigned/unverified tokens;
- trust client-supplied identity/role fields;
- store plaintext passwords.

Token/session validation MUST verify relevant properties such as:
- signature;
- issuer;
- audience;
- expiration;
- not-before where applicable.

---

## 5. Passwords

If the application manages passwords directly:
- use an established adaptive password hashing algorithm;
- use framework/library defaults appropriate to current guidance;
- never encrypt passwords reversibly;
- never log passwords;
- rate-limit/defend login where risk requires.

Password reset tokens MUST be:
- unpredictable;
- time-limited;
- single-use or invalidated appropriately.

---

## 6. Sessions

Session design SHOULD define:
- expiration;
- renewal;
- logout invalidation;
- revocation where required;
- concurrent session policy;
- cookie/token storage.

Browser session cookies SHOULD use appropriate:
- `Secure`;
- `HttpOnly`;
- `SameSite`.

Do not expose session credentials to client-side JavaScript unless architecture intentionally requires a token model and risks are understood.

---

## 7. OAuth2 / OIDC

OAuth/OIDC integrations MUST validate:
- redirect URI rules;
- state/nonce where applicable;
- issuer;
- audience;
- token signature;
- PKCE where applicable to public clients.

Do not accept arbitrary redirect/callback URLs from user input.

---

## 8. MFA / Step-Up

High-risk operations MAY require step-up authentication.

Examples:
- changing credentials;
- high-value payment;
- admin/security action;
- exporting sensitive data.

Step-up requirement belongs in product/security design, not ad hoc UI behavior.

---

## 9. Authorization

Authorization MUST occur on the server/trusted service boundary for protected resources.

Checks SHOULD consider:
- identity;
- role;
- scope;
- ownership;
- tenant;
- resource state;
- business policy.

Avoid authorization scattered as repeated raw `if role == ...` checks when a policy abstraction would improve consistency.

---

## 10. Object-Level Authorization

Every operation using user-controlled resource identifiers MUST validate access to the referenced object.

Do not assume:
- random UUID makes an object private;
- hidden UI prevents access;
- parent resource authorization automatically covers child operations.

This protects against BOLA/IDOR-style failures.

---

## 11. Tenant Isolation

Multi-tenant systems MUST enforce tenant isolation at authoritative server/data boundaries.

Tenant context MUST come from trusted identity/request context, not arbitrary payload fields.

Cross-tenant admin capability MUST be explicit and auditable where appropriate.

---

## 12. Privileged Operations

Admin/privileged actions SHOULD:
- require explicit authorization;
- use least privilege;
- be auditable when impact warrants;
- avoid broad shared admin accounts.

Break-glass access SHOULD be exceptional and tracked for high-risk systems.

---

## 13. Input Validation

Inputs MUST be validated for:
- shape;
- length;
- format;
- allowed values;
- semantic constraints.

Validation SHOULD use allow-lists where feasible.

Do not rely on validation alone for injection prevention when parameterized APIs exist.

---

## 14. SQL / Query Injection

Database access MUST use parameterized queries/prepared mechanisms.

Do not concatenate untrusted input into:
- SQL;
- NoSQL query syntax;
- search expressions;
- stored procedure names.

Dynamic sort/filter fields MUST be allow-listed.

---

## 15. Command Injection

Avoid executing shell commands with user-controlled data.

If unavoidable:
- use safe process APIs with argument arrays;
- allow-list commands/options;
- avoid shell interpretation;
- run with least privilege.

Never build shell strings from untrusted input.

---

## 16. Cross-Site Scripting (XSS)

User-controlled content MUST be safely encoded/escaped for its output context.

Frontend frameworks' default escaping SHOULD NOT be bypassed without review.

Raw HTML rendering MUST use:
- trusted content;
- vetted sanitization;
- explicit rationale.

Sanitization libraries SHOULD be established and maintained.

---

## 17. CSRF

Cookie-authenticated browser applications that perform state changes MUST assess CSRF.

Use appropriate protections such as:
- same-site cookie strategy;
- CSRF tokens;
- origin checks;
- framework protections.

Bearer-token APIs may have a different CSRF profile but still require XSS/token theft analysis.

---

## 18. SSRF

Server-side URL fetching MUST treat destinations as untrusted when user influence exists.

Controls MAY include:
- scheme allow-list;
- hostname/domain allow-list;
- DNS/IP validation;
- block private/link-local/metadata ranges;
- redirect revalidation;
- network egress policy.

Do not trust a URL simply because it parses successfully.

---

## 19. Open Redirects

Redirect destinations derived from user input MUST be constrained to approved destinations.

Use:
- relative paths;
- allow-listed origins/routes.

Do not pass arbitrary external URLs through login/logout flows.

---

## 20. File Uploads

File uploads MUST define:
- maximum size;
- allowed type/content;
- filename handling;
- storage location;
- access control;
- malware/content scanning where risk requires.

Do not trust:
- extension;
- client MIME type;
- original filename.

Uploads SHOULD be stored outside executable application paths.

---

## 21. Path Traversal

User-controlled filenames/paths MUST NOT directly determine filesystem paths without safe normalization and boundary checks.

Prefer generated storage keys.

---

## 22. Deserialization

Untrusted data MUST NOT be deserialized into mechanisms that can instantiate arbitrary types or execute code.

Use explicit schemas/types.

Avoid unsafe native object serialization formats across trust boundaries.

---

## 23. Template / Expression Injection

Do not evaluate untrusted text as:
- template code;
- expression language;
- script;
- SQL;
- regex with uncontrolled complexity where DoS risk exists.

Dynamic rules engines require explicit sandbox/security design.

---

## 24. Secrets

Secrets include:
- passwords;
- API keys;
- signing keys;
- client secrets;
- database credentials;
- webhook secrets.

Secrets MUST NOT be:
- committed;
- embedded in images/build artifacts unintentionally;
- printed in logs;
- exposed to frontend bundles unless intended public values.

Use approved secret management.

---

## 25. Secret Rotation

High-value credentials SHOULD support rotation.

Rotation design SHOULD consider overlapping old/new validity where zero-downtime is required.

Compromised credentials MUST be revocable.

---

## 26. Cryptography

Use established cryptographic libraries and protocols.

MUST NOT:
- invent custom encryption;
- use obsolete hashes/ciphers for security;
- hard-code encryption keys;
- use deterministic encryption where semantic security is required without a specific design.

Randomness for security-sensitive tokens MUST use cryptographically secure RNG.

---

## 27. Transport Security

Sensitive/authenticated traffic MUST use TLS in production.

Do not disable certificate validation to fix connectivity issues.

Internal traffic security SHOULD follow threat model/network trust assumptions.

---

## 28. Data at Rest

Sensitive persistent data SHOULD use platform/storage encryption as appropriate.

Field-level encryption MAY be required for particularly sensitive data.

Encryption does not replace authorization and data minimization.

---

## 29. Personal Data

Collect only data needed for product/business requirements.

Sensitive/PII handling SHOULD define:
- purpose;
- access;
- retention;
- deletion/export;
- logging/analytics restrictions.

Do not copy production PII into development/test without an approved protected process.

---

## 30. Logging

Logs MUST NOT contain:
- passwords;
- access/refresh tokens;
- private keys;
- full card/payment credentials;
- raw session secrets;
- unnecessary sensitive payloads.

Identifiers MAY be logged when necessary for operations, subject to privacy policy.

Redaction SHOULD occur before data reaches log sinks.

---

## 31. Error Handling

Public errors MUST NOT expose:
- stack traces;
- SQL;
- internal filesystem paths;
- secrets;
- vendor credentials;
- sensitive debugging context.

Detailed error context MAY be recorded securely in internal telemetry with redaction.

---

## 32. Webhooks

Webhook endpoints MUST verify provider authenticity where the provider supports secure verification.

Consider:
- signature;
- timestamp;
- replay;
- raw-body requirements;
- idempotency.

Do not accept business-critical callbacks solely based on source IP unless provider contract explicitly relies on it and operational constraints are understood.

---

## 33. CORS

CORS MUST be configured to the minimum required origins/methods/headers.

Do not use:

```text
Access-Control-Allow-Origin: *
```

with credentials or protected browser APIs.

CORS is not authentication or authorization.

---

## 34. Security Headers

Web applications SHOULD use appropriate browser security headers, such as:
- Content-Security-Policy;
- frame restrictions;
- content type protections;
- referrer policy;
- HSTS where TLS deployment supports it.

Exact policy depends on frontend architecture.

---

## 35. Content Security Policy

CSP SHOULD be used for browser-facing applications where practical.

Avoid broad:
- `unsafe-inline`;
- `unsafe-eval`;
- wildcard sources;

without justified need.

Adopt incrementally if legacy constraints prevent immediate strict enforcement.

---

## 36. Rate Limiting and Abuse

Public/auth endpoints SHOULD assess abuse risk.

Candidates:
- login;
- password reset;
- registration;
- OTP;
- search;
- expensive generation;
- file upload;
- webhook endpoints.

Rate limiting SHOULD distinguish user/IP/client context where appropriate.

Do not use IP-only rules as a universal identity control.

---

## 37. Resource Limits

Inputs/operations SHOULD define safe bounds:
- payload size;
- file size;
- pagination max;
- query complexity;
- batch size;
- execution time.

Unbounded user-controlled resource use can become denial-of-service.

---

## 38. Dependencies

Dependencies SHOULD be maintained and scanned appropriately.

Known critical/high vulnerabilities MUST be assessed rather than ignored by default.

Do not update production dependencies blindly without compatibility testing.

Detailed supply-chain rules belong in `12_DEPENDENCY_SUPPLY_CHAIN.md`.

---

## 39. Frontend Security

Frontend code MUST assume the user can inspect/modify client state.

MUST NOT store authoritative secrets or trust:
- hidden fields;
- disabled controls;
- client role flags;
- route guards

as enforcement.

Sensitive tokens/session design MUST follow project security architecture.

---

## 40. Mobile / Desktop Clients

Installed clients SHOULD be treated as untrusted for server authorization.

Embedded secrets in shipped binaries MUST be considered recoverable by attackers.

Do not place long-lived server credentials in client applications.

---

## 41. Background Jobs

Jobs handling privileged/sensitive data SHOULD:
- run with least privilege;
- validate message/input;
- avoid logging sensitive payloads;
- handle duplicate/replay safely.

---

## 42. Security in CI/CD

CI MUST NOT expose secrets in:
- logs;
- pull requests from untrusted contexts;
- artifact metadata.

Secret access SHOULD be scoped by environment/job.

Production deploy credentials SHOULD be more restricted than test credentials.

---

## 43. Security Scanning

Projects SHOULD use risk-appropriate automation:
- secret scanning;
- dependency scanning;
- static analysis;
- container/image scanning;
- IaC scanning.

Scanners do not replace secure design/review.

False positives MAY be suppressed only with explicit rationale where the tool supports it.

---

## 44. Vulnerability Handling

Security findings SHOULD be triaged by:
- exploitability;
- affected asset;
- exposure;
- impact;
- available mitigation.

Critical exploitable issues SHOULD block release where risk is unacceptable.

Do not prioritize solely by scanner severity without context.

---

## 45. Security Testing

Tests SHOULD cover high-risk controls such as:
- authorization matrix;
- object ownership;
- tenant isolation;
- webhook signatures;
- input injection boundaries;
- session expiration;
- file validation.

Detailed test implementation belongs in `09_TESTING_STANDARD.md`.

---

## 46. Security Review Triggers

Explicit security review SHOULD occur when adding/changing:
- authentication;
- authorization;
- admin functionality;
- payment;
- file upload;
- sensitive data;
- public webhook;
- external URL fetch;
- cryptography;
- multi-tenancy;
- new internet-exposed service.

---

## 47. Incident Readiness

Projects handling important user/business data SHOULD have a way to:
- revoke credentials;
- identify affected versions/users;
- inspect audit/log evidence;
- disable risky capabilities where practical;
- recover safely.

Operations procedure belongs in the runbook.

---

## 48. Security Exceptions

Security exceptions MUST be:
- explicit;
- risk-assessed;
- owned;
- time-bound/reviewed when temporary.

Do not silently weaken controls to make development/test easier.

Material accepted security risk SHOULD appear in the threat model/risk register.

---

## 49. Security Review Checklist

Review:
- trusted boundary;
- authentication;
- object/tenant authorization;
- input/output handling;
- secrets;
- sensitive data;
- injection;
- SSRF/file/webhook risk;
- rate/resource limits;
- logs;
- dependency risk;
- tests;
- threat model update.

