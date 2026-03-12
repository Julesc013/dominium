Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Safe Mod Patterns

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: canonical.
Scope: explicitly supported mod patterns.
Authority: canonical. Mods SHOULD follow these patterns.

## Supported patterns
- Add new model families via `schema/worldgen_model.schema`.
- Add new refinement layers with explicit precedence tags.
- Add new epistemic datasets (knowledge and measurement artifacts).
- Add new reality domains (magic, alt-physics) as optional packs.
- Add incorrect or fictional knowledge as epistemic overlays.

## Required behaviors
- All additions MUST be capability-resolved.
- All additions MUST include provenance records.
- All additions MUST preserve unknown fields and tags.
