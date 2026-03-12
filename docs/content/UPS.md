Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Universal Pack System (UPS)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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
