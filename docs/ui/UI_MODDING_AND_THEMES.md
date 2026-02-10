Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# UI Modding And Themes

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

