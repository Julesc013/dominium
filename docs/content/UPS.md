# Universal Pack System (UPS)

Status: draft (implementation gaps noted).
Scope: capability-driven content resolution and pack handling.
Authority: canonical for required contract; blockers listed below.

## Required contract
- All non-code content MUST be supplied via packs.
- Content MUST be resolved by capability, never by file path.
- Packs MUST provide capabilities; they MUST NOT be mandatory requirements.
- Missing capabilities MUST trigger explicit fallback, disablement, or refusal.
- Engine and game MUST boot with zero packs installed.

## Current state (as-is)
- UPS concepts are documented in `docs/content/UPS_OVERVIEW.md`.
- Packs under `data/packs/` are optional and capability-providing.
- Capability resolution enforcement in engine/game is not yet fully audited.

## Blockers to resolve in Phase 3
- Replace any hardcoded path/content lookups with capability resolution APIs.
- Document and enforce explicit fallback/disable/refusal behavior.
- Verify zero-asset boot paths under TESTX.

## References
- `docs/content/UPS_OVERVIEW.md`
- `docs/content/FALLBACK_MATRIX.md`
