Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: INT-1 InteriorVolumeGraph baseline completion report.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Interior Volume Baseline

## Model Summary
- Interior topology is data-defined by `interior_graph` with:
  - `interior_volume` nodes
  - `portal` edges
- Runtime substrate is `src/interior/interior_engine.py` with deterministic APIs:
  - `reachable_volumes`
  - `path_exists`
  - `resolve_volume_world_transform`
  - `apply_portal_transition`
- Interior schemas and registry payloads are integrated via CompatX:
  - `schema/interior/interior_volume.schema`
  - `schema/interior/portal.schema`
  - `schema/interior/interior_graph.schema`
  - `data/registries/interior_volume_type_registry.json`
  - `data/registries/portal_type_registry.json`

## Portal Integration
- Portals are state-machine-gated connectivity edges.
- Portal connectivity uses portal state (`open|closed|locked|damaged`) and deterministic permeability tags.
- Portal transitions are process-triggered through `apply_transition` only; no direct flag mutation.

## Epistemic Gating
- Observation pipeline applies deterministic interior occlusion:
  - viewer volume derived from camera/authority scope/entity location mapping
  - if target entity is in same interior graph but unreachable via open portals, it is excluded from `PerceivedModel`.
- Freecam bypass is policy-gated:
  - `lens.nondiegetic.freecam` bypasses occlusion
  - law profile can additionally allow bypass via `epistemic_limits.allow_freecam_occlusion_bypass`.
- Inspection exposes interior sections without truth mutation:
  - `section.interior.layout`
  - `section.interior.portal_states`

## Render/Inspection Overlays
- Inspection overlay integration adds `interior_overlay` mode:
  - volume boundary markers
  - portal state glyphs
  - deterministic ordering/material hashing
- Overlay data is derived from inspection snapshots and remains truth-read-only.

## Guardrails
- RepoX invariants added:
  - `INV-NO-ADHOC-OCCLUSION`
  - `INV-PORTAL-USES-STATE-MACHINE`
- AuditX analyzers added:
  - `InteriorOcclusionLeakSmell` (`E96_INTERIOR_OCCLUSION_LEAK_SMELL`)
  - `DuplicateInteriorGraphSmell` (`E97_DUPLICATE_INTERIOR_GRAPH_SMELL`)
- TestX coverage added:
  - `test_volume_connectivity_deterministic`
  - `test_portal_state_changes_connectivity`
  - `test_occlusion_in_perceived_model`
  - `test_spatial_transform_composition_deterministic`

## Extension Points (INT-2)
- Portal `sealing_coefficient` is in place for HVAC/fluid coupling.
- Interior graph can connect to FlowSystem channels without schema refactor.
- State-machine + constraint hooks are ready for airlocks, pressure doors, and compartment sealing logic.
