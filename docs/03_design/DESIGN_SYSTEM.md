# Design System — <PROJECT_NAME>

> **Peran dokumen:** Source of truth untuk **prinsip visual, design tokens, reusable UI patterns, interaction behavior, accessibility, responsive rules, dan motion**.
>
> Dokumen ini tidak menentukan business rules. Feature-specific behavior berada di feature specification dan UX flow.

---

## Metadata Dokumen

| Field | Value |
|---|---|
| Product | `<PROJECT_NAME>` |
| Status | Draft / Review / Locked |
| Owner | `<OWNER>` |
| Last Updated | `<YYYY-MM-DD>` |

---

## 1. Design Direction

### Product Personality

`<MODERN / TRUSTED / TECHNICAL / PLAYFUL / EDITORIAL / ETC.>`

### Design Intent

<Deskripsikan rasa dan kualitas pengalaman yang ingin dibangun.>

### Principles

1. **<PRINCIPLE>** — <WHY>
2. **<PRINCIPLE>** — <WHY>
3. **<PRINCIPLE>** — <WHY>

### Anti-Patterns

Hindari:
- `<ANTI_PATTERN>`;
- `<ANTI_PATTERN>`;
- inconsistent one-off styling tanpa alasan.

---

## 2. Design Token Ownership

Design token harus menjadi reusable source, bukan copy-paste value di setiap component.

Recommended categories:

```text
color
typography
spacing
size
radius
shadow
border
motion
breakpoint
z-index
```

Jika project menggunakan token file/code-generated system, executable token definitions adalah implementation source. Dokumen ini menjelaskan intent dan semantic meaning.

---

## 3. Color

### Semantic Colors

| Token | Purpose | Example |
|---|---|---|
| `color.background.default` | Main surface | `<VALUE>` |
| `color.text.primary` | Primary text | `<VALUE>` |
| `color.action.primary` | Primary action | `<VALUE>` |
| `color.status.success` | Success feedback | `<VALUE>` |
| `color.status.warning` | Warning | `<VALUE>` |
| `color.status.danger` | Destructive/error | `<VALUE>` |

Jangan gunakan warna sebagai satu-satunya pembeda status.

### Brand Palette

`<PALETTE / LINK>`

---

## 4. Typography

| Role | Token / Style | Usage |
|---|---|---|
| Display | `<STYLE>` | Hero / major marketing |
| Heading 1 | `<STYLE>` | Page title |
| Heading 2 | `<STYLE>` | Major section |
| Body | `<STYLE>` | Primary reading |
| Label | `<STYLE>` | Controls |
| Code / Mono | `<STYLE>` | Technical content |

Rules:
- maintain readable line length;
- avoid font-size-only hierarchy;
- preserve minimum readable size;
- avoid excessive font families/weights.

---

## 5. Spacing and Layout

### Spacing Scale

`<4 / 8-based / custom>`

| Token | Value | Typical Use |
|---|---:|---|
| `space.1` | `<VALUE>` | Tight |
| `space.2` | `<VALUE>` | Small |
| `space.3` | `<VALUE>` | Component |
| `space.4` | `<VALUE>` | Section |

### Grid

`<GRID RULES>`

### Content Width

`<MAX WIDTH / CONTAINER RULES>`

---

## 6. Breakpoints

| Name | Range | Intent |
|---|---|---|
| Mobile | `<RANGE>` | Compact single-column |
| Tablet | `<RANGE>` | Intermediate |
| Desktop | `<RANGE>` | Full layout |
| Wide | `<RANGE>` | Optional |

Breakpoints harus mengikuti content behavior, bukan device brand tertentu.

---

## 7. Core Components

Setiap reusable component harus mempunyai:
- purpose;
- variants;
- states;
- sizing;
- accessibility behavior;
- responsive behavior jika relevan.

### Button

**Variants**
- Primary
- Secondary
- Tertiary / Ghost
- Destructive

**States**
- Default
- Hover
- Focus
- Active
- Disabled
- Loading

**Rules**
- satu primary action dominan per context bila memungkinkan;
- disabled state tidak menggantikan explanation;
- loading button harus mencegah accidental duplicate submission bila action tidak repeatable.

### Input

States:
- Default
- Focus
- Filled
- Invalid
- Disabled
- Read-only

Error message harus associated dengan field secara semantic.

### Other Components

Document when used:
- Select / Combobox
- Checkbox / Radio
- Tabs
- Dialog
- Drawer
- Toast
- Tooltip
- Table
- Pagination
- Card
- Badge
- Breadcrumb
- Navigation
- Stepper / Progress
- Empty State
- Skeleton

---

## 8. Form Pattern

### Label

- visible label preferred;
- placeholder bukan pengganti label;
- optional/required convention harus konsisten.

### Validation

- client validation untuk immediate feedback;
- server response tetap authoritative;
- preserve user input after validation failure;
- group summary dapat digunakan untuk form panjang.

### Destructive Action

Gunakan confirmation ketika consequence sulit dipulihkan.

---

## 9. Feedback and Status

### Success
Jelaskan outcome yang berhasil, bukan hanya “Success”.

### Warning
Gunakan untuk consequence/attention yang belum menjadi failure.

### Error
Error harus:
- understandable;
- actionable bila memungkinkan;
- tidak mengekspos internal details;
- mempertahankan context user.

### Toast
Gunakan untuk transient feedback yang tidak memerlukan permanent context.

Critical failure tidak boleh hanya disampaikan melalui toast yang cepat hilang.

---

## 10. Loading

Pilih pattern berdasarkan konteks:

| Pattern | Use When |
|---|---|
| Skeleton | Structure predictable |
| Spinner | Short indeterminate wait |
| Progress | Meaningful progress known |
| Background status | User can leave flow |

Hindari skeleton yang sangat berbeda dari final layout.

---

## 11. Empty States

Empty state harus mengandung kombinasi yang relevan:

- title;
- explanation;
- illustration/icon bila membantu;
- primary next action;
- secondary education/help.

Bedakan:
- first-use empty;
- no search result;
- filtered empty;
- permission-limited empty;
- error disguised as empty (avoid).

---

## 12. Tables and Data-Dense UI

Rules:
- prioritize readable alignment;
- numeric values align consistently;
- support horizontal overflow intentionally on small screens;
- row actions predictable;
- loading/empty/error states defined;
- sorting/filtering state visible;
- pagination behavior consistent.

---

## 13. Navigation Patterns

Define:
- primary navigation;
- secondary navigation;
- breadcrumbs;
- contextual actions;
- mobile navigation behavior.

Navigation labels should use user language, not internal module names where those differ.

---

## 14. Motion

### Motion Principles

Motion harus:
- clarify relationship;
- acknowledge interaction;
- guide attention;
- communicate progress/state;
- never delay task completion unnecessarily.

### Timing

| Category | Duration |
|---|---:|
| Micro interaction | `<VALUE>` |
| Component transition | `<VALUE>` |
| Page/section transition | `<VALUE>` |

### Reduced Motion

Respect `prefers-reduced-motion` or platform equivalent for non-essential movement.

---

## 15. Icons and Illustration

### Icons
- use one coherent icon family when possible;
- decorative icons should not receive unnecessary accessible labels;
- action icons without visible text need accessible names;
- avoid ambiguous icon-only critical actions.

### Illustration
`<STYLE / USAGE RULES>`

---

## 16. Content and Microcopy

### Tone

`<TONE>`

### Rules
- action labels should describe action;
- avoid unnecessary jargon in user-facing copy;
- destructive confirmation names the consequence;
- errors explain what user can do next;
- technical identifiers may be shown only when useful for support/debugging.

---

## 17. Accessibility

Target: `<e.g. WCAG 2.2 AA where applicable>`

Required patterns:
- keyboard operability;
- visible focus;
- semantic structure;
- label/control association;
- sufficient contrast;
- accessible names;
- status announcements;
- touch target sizing;
- reduced motion;
- no color-only meaning.

---

## 18. Responsive Adaptation

Responsive design bukan sekadar mengecilkan desktop.

For each major component, define:
- what reflows;
- what stacks;
- what becomes drawer/menu;
- what remains always visible;
- what can collapse;
- what must never disappear.

---

## 19. Design QA Checklist

Before considering a new UI pattern complete:

- [ ] uses existing tokens where applicable;
- [ ] variants/states are defined;
- [ ] loading/empty/error behavior exists;
- [ ] keyboard behavior is verified;
- [ ] responsive behavior is verified;
- [ ] contrast and semantics are reviewed;
- [ ] reduced motion is considered;
- [ ] pattern does not duplicate an existing component without reason.

---

## 20. Exceptions

Document intentional deviations.

| Component / Area | Exception | Reason | Review |
|---|---|---|---|
| `<AREA>` | `<EXCEPTION>` | `<RATIONALE>` | `<DATE/MILESTONE>` |

---

## 21. Related Documents

- UX Flows: `./UX_FLOWS.md`
- PRD: `../00_product/PRD.md`
- Feature Specs: `../01_features/`
- Frontend Standard: `../standards/05_FRONTEND_STANDARD.md`
- Accessibility NFR: `../02_architecture/NON_FUNCTIONAL_REQUIREMENTS.md`

---

## 22. Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | `<YYYY-MM-DD>` | Initial draft | `<AUTHOR>` |
