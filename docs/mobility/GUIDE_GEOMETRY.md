# GuideGeometry Doctrine

Status: CANONICAL
Last Updated: 2026-03-02
Scope: MOB-1 geometric substrate for deterministic movement constraints.

## 1) Purpose

GuideGeometry is the authoritative geometric substrate for mobility constraints. It provides deterministic, inspectable geometry artifacts that movement systems consume without hardcoded mode branches.

## 2) Geometry Types

GuideGeometry supports these type identifiers:

- `geo.spline1D`
  - Parametric centerline with deterministic arc-length parameter `s`.
  - Used for constrained 1D movement.
- `geo.corridor2D`
  - Surface/corridor envelope around a guide centerline.
  - Used for constrained 2D movement and lane-like envelopes.
- `geo.volume3D`
  - Bounded 3D navigation volume.
  - Used for constrained 3D movement.
- `geo.orbital_path`
  - Analytic orbital parameterization (no numeric integration required here).
- `geo.field_following`
  - Guidance path bound to declared field lanes or vector-follow references.

All geometry parameters are data-declared in typed parameter maps and resolved through registry schema refs.

## 3) Coordinate Frames and Spatial Scope

Every geometry row binds to `parent_spatial_id`.

- `parent_spatial_id` anchors coordinates to a `SpatialNode` frame.
- Geometry points and derived metrics are interpreted in this frame.
- Cross-frame usage requires explicit spatial transforms outside GuideGeometry core.

GuideGeometry never assumes global world-space as an implicit default in authoritative mutation.

## 4) Deterministic Parameterization

For `geo.spline1D`, parameter `s` is canonicalized as deterministic fixed-point millimeter arc-length.

- `s=0` maps to the first control endpoint.
- `s_max` equals deterministic total length.
- Sampling and snapping use deterministic ordering over point indices and endpoint ids.

No wall-clock stepping or random perturbation is allowed.

## 5) Junction Model

Junctions are explicit first-class rows:

- Junction types: `junc.endpoint`, `junc.switch`, `junc.merge`, `junc.split`, `junc.station`.
- Junction rows store:
  - connected geometry ids
  - parent spatial id
  - optional switch `state_machine_id` for switchable topology

Junction connection ordering is deterministic (`junction_id`, then `connected_geometry_ids` sorted).

## 6) Deterministic Snapping

Endpoint snapping is policy-driven and deterministic.

- Snap policies:
  - `snap.none`
  - `snap.endpoint`
  - `snap.grid`
  - `snap.spec_compliant`
- Snap selection order:
  1. Candidate endpoints sorted by distance metric and id tie-break
  2. Policy constraints applied in fixed order
  3. First valid candidate selected deterministically

## 7) SpecSheet Integration

Specs attach to geometry through standard SPEC processes.

- `process.spec_apply_to_target` may bind `spec_id` to `target_kind=geometry` and `target_id=geometry.*`.
- `process.spec_check_compliance` for geometry consumes derived metrics:
  - curvature radius summary
  - clearance summary (stub in MOB-1)
  - gauge width summary (stub in MOB-1)

Compliance is deterministic, inspectable, and returns explicit refusal/warn surfaces.

## 8) Formalization Integration

GuideGeometry integrates with FORM lifecycle:

- `RAW`
  - only physical assemblies and material traces exist
- `INFERRED`
  - candidate geometry remains derived-only
- `FORMAL`
  - accepting an inferred candidate creates canonical GuideGeometry artifact rows
- `NETWORKED`
  - deferred to MOB-2 network graph promotion

Inference itself remains non-mutating for truth until acceptance via control/process path.

## 9) UX and Planning Contract

Planning uses plan artifacts and ghost overlays.

- `PlanIntent` can carry guide previews in `plan_artifact.spatial_preview_data`.
- ExecutePlan emits process commitments/geometry create intents.
- Diegetic raw placement remains valid without immediate GuideGeometry creation.

GuideGeometry overlays are render-only projections and do not mutate truth.

## 10) Performance and Determinism

- Global micro geometry simulation is forbidden.
- Derived metric computation is budgeted and cacheable by geometry hash.
- Degradation is explicit and deterministic (reduced metric detail before refusal).
- All geometry/junction/candidate rows carry deterministic fingerprints.

## 11) Non-Goals (MOB-1)

- No vehicle micro-physics.
- No congestion solver.
- No signal control solver.
- No wall-clock dependence.
