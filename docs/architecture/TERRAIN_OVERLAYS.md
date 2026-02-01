Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Terrain Overlays (TERRAIN0)

Status: binding.
Scope: process-only overlay semantics for terrain edits.

## Overlay types (authoritative)
- `delta_phi` (CSG cut/fill)
- `delta_material`
- `delta_field` (generic)

All overlays:
- are created only via Processes.
- are sparse and chunked.
- are auditable with provenance.
- are collapsible into macro capsules.
- never modify meshes directly.

## Deterministic CSG for `delta_phi`
Let `phi_base` be the current SDF and `phi_edit` be the edit SDF.

Cut (subtraction):
- `phi_out = max(phi_base, -phi_edit)`

Fill (union):
- `phi_out = min(phi_base, phi_edit)`

smooth (bounded filter process):
- A Process applies a deterministic, fixed-point kernel over a bounded radius.
- The kernel radius and weights are explicit data, not implicit behavior.
- The process MUST be replayable and budgeted.

## Ordering
Overlay application order is deterministic:
- primary: commit tick
- secondary: process_id
- tertiary: overlay_id

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`