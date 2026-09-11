# Frontend Engineering Standard

> **Purpose:** Define reusable implementation expectations for user-facing frontend applications.
>
> Product behavior comes from PRD/feature specs. UX flow and visual behavior come from design documentation. API shape comes from contracts.

---

## 1. Frontend Responsibilities

Frontend code SHOULD own:

- rendering;
- interaction;
- navigation;
- presentation state;
- form experience;
- client-side feedback;
- accessibility;
- responsive adaptation;
- consumption of server contracts.

Frontend MUST NOT be treated as the authoritative security boundary for protected business actions.

---

## 2. Structure

Frontend structure SHOULD organize code by meaningful feature/responsibility rather than only by technical file type.

Example:

```text
src/
├── app/
├── features/
│   ├── checkout/
│   └── learning/
├── components/
├── services/
├── hooks/
├── state/
└── utilities/
```

The exact structure is project-specific.

Avoid one global `components/`, `utils/`, or `services/` directory becoming an unowned dumping ground.

---

## 3. Component Responsibility

Components SHOULD have clear responsibilities.

Prefer separating:
- reusable presentation;
- feature orchestration;
- data fetching/mutation;
- complex business/policy decisions.

Do not split every small markup block into a component solely to reduce line count.

Extract components when reuse, readability, testability, or responsibility warrants it.

---

## 4. Server State vs UI State

Frontend SHOULD distinguish:

### Server State
Data whose authority lives on the server.

Examples:
- course list;
- order status;
- profile;
- permissions.

### Local UI State
Examples:
- dialog open;
- selected tab;
- temporary form field;
- local expansion state.

Do not duplicate server state into global client state without a concrete need.

Use the project's selected server-state/query mechanism consistently.

---

## 5. Data Fetching

Data fetching SHOULD:

- use centralized/adapted API clients where appropriate;
- respect contract types;
- handle loading/error/cancellation;
- avoid duplicate unnecessary requests;
- define refresh/staleness behavior.

Components SHOULD NOT invent API fields absent from the contract.

---

## 6. Mutations

Mutations SHOULD provide:

- progress state;
- prevention/handling of accidental duplicate action;
- clear success/failure result;
- cache/server-state reconciliation;
- rollback behavior if optimistic UI is used.

Do not show success before authoritative outcome when failure would create misleading user state, unless optimistic behavior is deliberately designed.

---

## 7. Forms

Forms SHOULD:

- use visible labels;
- preserve valid user input after validation failure;
- provide field-level feedback;
- distinguish client validation from server rejection;
- disable/prevent duplicate submission where required;
- handle server-side validation response.

Client validation improves UX but MUST NOT replace authoritative backend validation.

---

## 8. Validation

Validation rules shared with the backend MAY use shared schemas/generated contract types when architecture supports it.

Do not copy complex business rules independently into frontend code as the only implementation.

If frontend mirrors a business rule for UX, backend MUST remain authoritative.

---

## 9. Authorization UX

Frontend MAY hide or disable actions based on known permissions for UX.

However:
- protected routes/actions still require server enforcement;
- client role data MUST NOT be trusted as proof of authorization;
- forbidden responses MUST be handled safely;
- stale permissions SHOULD recover predictably.

---

## 10. Routing

Routes SHOULD:

- have clear ownership;
- support expected deep links;
- handle authentication transitions;
- preserve meaningful browser navigation behavior;
- avoid embedding secret/sensitive data in URLs.

Route guards improve UX but do not replace server authorization.

---

## 11. Loading States

Every async user-visible operation SHOULD define an appropriate loading state.

Use:
- skeleton for predictable content shape;
- spinner for short indeterminate wait;
- progress for meaningful measured progress;
- background status when user may continue elsewhere.

Avoid unnecessary layout shift.

---

## 12. Empty States

Differentiate:
- first use;
- no search result;
- filtered empty;
- no permission;
- loading failure.

Do not silently render `[]` as a generic empty state when data fetch actually failed.

---

## 13. Error States

Frontend errors SHOULD be:
- understandable;
- contextual;
- actionable when possible;
- safe.

Do not display:
- stack traces;
- raw backend exceptions;
- internal identifiers that provide no user value.

Technical correlation/reference IDs MAY be shown when useful for support.

---

## 14. Error Boundaries

Applications SHOULD use error boundaries or equivalent mechanisms where framework supports them to prevent one rendering failure from destroying unrelated UI.

Recovery behavior SHOULD be intentional.

Do not use global catch-all fallback as a substitute for feature-level error handling.

---

## 15. Optimistic UI

Optimistic updates MAY be used when:
- operation is likely to succeed;
- rollback is well-defined;
- temporary divergence is acceptable;
- duplicate/conflict behavior is understood.

Avoid optimistic UI for high-risk irreversible operations unless product behavior explicitly supports it.

---

## 16. Accessibility

User-facing frontend MUST consider accessibility.

At minimum where applicable:
- keyboard operation;
- visible focus;
- semantic HTML/native controls;
- accessible names;
- label association;
- error announcement;
- contrast;
- non-color-only meaning;
- reduced motion.

Prefer native semantic elements over recreating them with generic containers.

---

## 17. Keyboard and Focus

Interactive elements MUST be keyboard reachable where expected.

Modal/dialog flows SHOULD:
- move focus intentionally;
- contain focus when appropriate;
- restore focus after closing.

Async updates SHOULD not unexpectedly steal focus.

---

## 18. Responsive Design

Responsive behavior SHOULD be designed, not patched after desktop completion.

Components SHOULD define:
- stacking/reflow;
- overflow behavior;
- touch targets;
- navigation adaptation;
- content priority.

Critical capabilities MUST NOT disappear on small screens without explicit product scope.

---

## 19. Design System

Reusable UI SHOULD consume project design tokens/components where available.

Avoid one-off:
- colors;
- spacing;
- shadows;
- radii;
- typography;

when a semantic design token exists.

New reusable visual patterns SHOULD update the Design System when they become project conventions.

---

## 20. Styling

The project SHOULD use one primary styling approach consistently.

Avoid mixing multiple competing styling systems without architectural reason.

Styles SHOULD:
- remain scoped/predictable;
- avoid excessive specificity;
- preserve responsive/accessibility behavior.

---

## 21. Motion

Motion SHOULD communicate:
- causality;
- hierarchy;
- progress;
- state change.

Motion MUST NOT:
- block task completion unnecessarily;
- create inaccessible required behavior;
- ignore reduced-motion preferences when movement is non-essential.

---

## 22. Performance

Frontend SHOULD manage:
- bundle size;
- rendering cost;
- image/media weight;
- request waterfalls;
- unnecessary re-renders;
- large list rendering.

Performance optimization SHOULD be measured when non-trivial complexity is introduced.

Detailed targets belong in NFR and `11_PERFORMANCE_STANDARD.md`.

---

## 23. Large Lists

Large datasets SHOULD use appropriate:
- pagination;
- incremental loading;
- virtualization;

based on expected scale.

Do not render unbounded collections simply because current development data is small.

---

## 24. Images and Media

Use:
- appropriate dimensions;
- responsive sources where useful;
- lazy loading where appropriate;
- explicit size/aspect ratio to reduce layout shift.

Sensitive/private media MUST respect access control rather than relying on obscure URLs.

---

## 25. Client Storage

Browser/device storage SHOULD be treated deliberately.

Do not place sensitive credentials/data in:
- localStorage;
- sessionStorage;
- IndexedDB;

without understanding security implications.

Storage lifecycle, invalidation, and versioning SHOULD be defined for persistent client state.

---

## 26. Authentication Tokens

Token/session handling MUST follow the project's security architecture.

Frontend MUST NOT invent its own token persistence scheme merely for convenience.

Prefer secure provider/framework patterns.

Detailed security rules belong in `08_SECURITY_STANDARD.md`.

---

## 27. API Types

Where tooling supports it, frontend SHOULD derive API models/clients from authoritative contracts or maintain a clearly synchronized boundary.

Do not manually redefine large contract schemas in multiple locations if generation/shared schema solves the problem safely.

Generated code SHOULD not be manually patched.

---

## 28. Feature Flags

Frontend feature flags SHOULD:
- have clear defaults;
- be removed after rollout when no longer needed;
- not be the only enforcement mechanism for protected backend behavior.

---

## 29. Analytics

Analytics events SHOULD represent meaningful product behavior.

Do not:
- send secrets;
- send unnecessary PII;
- duplicate the same event from multiple components accidentally;
- bind analytics semantics tightly to unstable DOM structure.

Product events SHOULD align with PRD/UX analytics definitions where they exist.

---

## 30. Internationalization

If localization is required:
- user-facing strings SHOULD be externalized;
- date/time/currency SHOULD use locale-aware formatting;
- concatenated sentence fragments SHOULD be avoided where translation order may differ;
- layouts SHOULD tolerate text expansion.

---

## 31. Testing

Frontend tests SHOULD cover appropriate layers:

- component behavior;
- form validation;
- permission UX;
- important async states;
- accessibility behavior;
- critical end-to-end journeys.

Avoid snapshot-only testing as the main confidence mechanism for interactive behavior.

Detailed rules belong in `09_TESTING_STANDARD.md`.

---

## 32. Browser Compatibility

Supported browsers/platforms MUST follow project NFR.

Do not add compatibility hacks for unsupported platforms unless product scope changes.

Feature detection SHOULD be preferred over brittle user-agent assumptions where practical.

---

## 33. Dependency Use

Before adding a frontend dependency, consider:
- bundle cost;
- maintenance;
- tree-shaking;
- accessibility quality;
- SSR/client compatibility;
- existing design system capability.

Do not install a large library for trivial functionality without justification.

---

## 34. Frontend Review Checklist

Review:
- requirement alignment;
- server/client state ownership;
- loading/empty/error states;
- duplicate mutation behavior;
- contract usage;
- permission UX;
- accessibility;
- responsive behavior;
- performance;
- sensitive client storage;
- tests.

---

## 35. Exceptions

Project-specific framework constraints MAY adapt these rules.

Material deviations that affect architecture, security, compatibility, or product experience SHOULD be explicit in relevant project documentation.
