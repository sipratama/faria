# Threat Model — FARIA

> **Status:** Not activated for V1.
>
> FARIA V1 uses the `prototype` base profile with the `ai-enabled` modifier (see `docs/PROJECT_INITIALIZATION.md`). A formal STRIDE-style threat model was intentionally left out of the lean V1 documentation baseline established during initialization. The concrete V1 security baseline (Telegram allowlist, no raw DB access for the LLM, human confirmation for financial state changes, secret handling) is documented directly in `docs/02_architecture/SYSTEM_ARCHITECTURE.md` (Security and Trust Boundaries) since FARIA V1 is a single-household private system with a small, well-understood trust boundary.
>
> Activate this formal document if FARIA gains additional trust boundaries (e.g., multiple households, public exposure, payment execution) that outgrow the summary in System Architecture.

## Related Documents

- `AGENTS.md`
- `docs/PROJECT_INITIALIZATION.md`
- `docs/02_architecture/SYSTEM_ARCHITECTURE.md`
- `docs/standards/08_SECURITY_STANDARD.md`
