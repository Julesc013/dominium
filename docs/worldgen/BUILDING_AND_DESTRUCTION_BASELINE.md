# Building & Destruction Baseline (STRUCTURES7)

Status: binding for T7 baseline.  
Scope: structural assemblies that interact with terrain and fields via processes.

## What structures are
- Buildings, bridges, tunnels, and megastructures are assemblies that interact with terrain via fields.
- Stability emerges from support_capacity and stress fields; no hardcoded "building vs terrain" rules.
- Geometry references are view-only; meshes never become authoritative truth.

## Data model (authoritative)
- Structure specs:
  - `structure_id`, `geometry_ref`
  - `material_traits` (stiffness, density, brittleness)
  - `load_capacity`, `connection_points`, `gravity_interaction`
  - `maturity`
- Structure instances:
  - `structure_id`, `placement_transform`, `anchor_refs`
  - `integrity`, `stress_state`, `provenance`
- All numeric fields are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Processes (event-driven only)
- Placement, removal, repair, reinforcement, and collapse are Processes.
- Stress resolution is coarse and scheduled; no per-tick solvers.
- Determinism uses named RNG streams:
  - `noise.stream.<domain>.structure.<purpose>`
- Collapse emits terrain overlays (rubble/fill) via process outputs; no implicit mesh edits.

## Terrain integration
- Placement and stability read:
  - `terrain.phi` (solid/void)
  - `terrain.support_capacity`
  - `terrain.roughness` and slope (as needed)
- Underground structures and tunnels are supported via SDF overlays and anchors.

## What is NOT included yet
- No crafting, production, or economy.
- No ownership or zoning systems.
- No per-tick physics or global solvers.

## Collapse/expand compatibility
- Macro capsules store:
  - total structure count
  - total mass (coarse)
  - integrity and stress histograms
  - RNG cursor continuity for structure streams
- Expansion is deterministic and preserves invariants.

## Maturity labels
- structure.placement: **BOUNDED**
- structure.stress_model: **BOUNDED**
- structure.collapse: **BOUNDED**
- structure.material_traits: **STRUCTURAL**

## See also
- `docs/architecture/STRUCTURAL_STABILITY_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
