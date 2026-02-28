# ACTION_SURFACE Baseline

Status: ACT-1 baseline complete
Version: 1.0.0

## Scope
This baseline introduces a universal ActionSurface metadata layer for interaction discovery and affordance generation. It is data-driven, deterministic, law/authority gated, and process-only for mutation.

## Schema Summary
- `schema/interaction/action_surface.schema`
- `schema/interaction/surface_type.schema`
- `schema/interaction/tool_tag.schema`
- `schema/interaction/surface_visibility_policy.schema`

Compiled schema outputs:
- `schemas/action_surface.schema.json`
- `schemas/surface_type.schema.json`
- `schemas/tool_tag.schema.json`
- `schemas/surface_visibility_policy.schema.json`
- `schemas/surface_type_registry.schema.json`
- `schemas/tool_tag_registry.schema.json`
- `schemas/surface_visibility_policy_registry.schema.json`

## Registry Baseline
Source registries:
- `data/registries/surface_type_registry.json`
- `data/registries/tool_tag_registry.json`
- `data/registries/surface_visibility_policy_registry.json`

Baseline surface types:
- `surface.fastener`
- `surface.handle`
- `surface.seam`
- `surface.port`
- `surface.panel`
- `surface.grip`

Baseline tool tags:
- `tool_tag.cutting`
- `tool_tag.fastening`
- `tool_tag.welding`
- `tool_tag.lifting`
- `tool_tag.operating`

Baseline visibility policies:
- `visibility.default`
- `visibility.lab_only`
- `visibility.diegetic_only`

## Affordance Integration
- `src/interaction/action_surface_engine.py` resolves surfaces from perceived assembly/AG/blueprint metadata.
- `src/client/interaction/affordance_generator.py` now generates affordances from resolved surfaces first.
- Surface-driven affordances include:
  - `surface_id`
  - `surface_type_id`
  - `surface_visibility_policy_id`
  - `parameter_schema_id` (if present)
- Deterministic ordering:
  - surfaces sorted by `surface_id`
  - affordances sorted by `(surface_id, process_id, affordance_id)`
- Tool incompatibility produces disabled affordance reason:
  - `refusal.tool.incompatible`

## Render Behavior
- `src/client/interaction/interaction_panel.py` selection overlays include deterministic ActionSurface markers.
- Markers are procedural glyphs and materials only (no texture/assets required).
- Marker color derives from `surface_type_id` hash.
- Markers are overlay-layer only and bound to selection payloads.

## Runtime/Compile Integration
- Registry compile now includes:
  - `surface_type_registry`
  - `tool_tag_registry`
  - `surface_visibility_policy_registry`
- Lockfile contract updated with:
  - `surface_type_registry_hash`
  - `tool_tag_registry_hash`
  - `surface_visibility_policy_registry_hash`
- Session runtime registry loading and null-boot maps include the new ActionSurface registries.

## Guardrails
RepoX invariants enforced:
- `INV-ACTION-SURFACE-DATA-DRIVEN`
- `INV-NO-HARDCODED-SURFACE-LOGIC`
- `INV-ACTION-PROCESS-ONLY`

AuditX analyzers added:
- `HardcodedInteractionSmell`
- `SurfaceLeakSmell`

TestX coverage added:
- `test_surface_resolution_deterministic`
- `test_affordance_generation_from_surfaces`
- `test_tool_incompatibility_refusal`
- `test_surface_visibility_policy`
- `test_render_surface_marker_stable`

## Extension Points
Prepared for:
- ACT-2 ToolEffect: process parameterization by tool state and contact semantics.
- ACT-3 Task: multi-step interaction plans built on ActionSurface + process intents.
