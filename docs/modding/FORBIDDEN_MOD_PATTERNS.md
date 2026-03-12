Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Forbidden Mod Patterns

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: canonical.
Scope: prohibited mod behaviors.
Authority: canonical. Mods MUST NOT violate these rules.

## Prohibitions
- Mods MUST NOT delete parent refinement layers.
- Mods MUST NOT redefine engine or game semantics.
- Mods MUST NOT assume absolute truth or privileged physics.
- Mods MUST NOT depend on load order hacks.
- Mods MUST NOT hardcode file paths or assets.

## Enforcement
- Violations MUST be rejected or forced into explicit degraded modes.
