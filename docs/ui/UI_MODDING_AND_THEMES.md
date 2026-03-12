Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# UI Modding And Themes

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


UI extensions are pack-driven and schema-validated.

## UI Pack Model

- UI packs provide IR fragments, layouts, and theme data.
- UI packs must declare provided command bindings explicitly.
- UI packs cannot define hidden commands or bypass dispatch.

## Theme Model

- Themes can set palette, typography, spacing, and icon references.
- Themes are presentation-only and cannot alter simulation behavior.
- Theme selection is deterministic and profile-driven.

## Validation Rules

- Pack data must satisfy `schema/ui/ui_pack.schema`.
- Theme data must satisfy `schema/ui/ui_theme.schema`.
- Invalid bindings refuse with deterministic refusal codes.
- Unknown extension maps are preserved where declared open.

## Safety Constraints

- Capability checks gate optional UI modules.
- Experimental packs must be marked and removable.
- Disabling packs must not change simulation hashes.
