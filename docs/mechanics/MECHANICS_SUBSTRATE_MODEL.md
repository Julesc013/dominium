Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Version: 1.0.0
Owner: Core Engineering
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Mechanics Substrate Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## 1. Purpose
MECH-1 defines a deterministic, tiered mechanics substrate for structural load propagation, deformation, and fracture without introducing FEM/PDE solvers.

Mechanics is graph-based, process-driven, and budgeted under RS-5.

## 2. StructuralGraph
StructuralGraph is an overlay on AssemblyGraph.

- Nodes represent parts or subassemblies.
- Edges represent structural connections.
- Edge connection examples:
  - `conn.weld`
  - `conn.bolt`
  - `conn.glue`
  - `conn.hinge`
  - `conn.rope`
  - `conn.cable`
  - `conn.rigid_joint`

Edge attributes:
- `stiffness`
- `max_load`
- `connection_type_id`
- `fatigue_state`

## 3. Simplified Load Model
Per-node mechanics state tracks:
- `applied_force`
- `applied_torque`

Per-graph meso propagation:
- distribute node force contributions across connected edges proportionally by deterministic degree weighting.
- compute edge effective load and stress ratio.

Stress ratio:
- `stress_ratio = applied_load / max_load`
- represented as deterministic fixed-point/permille scalar in runtime state.

## 4. Deformation State
Per-node deformation fields:
- `elastic_strain` (recoverable scalar)
- `plastic_strain` (accumulated permanent scalar)
- `failure_state` (none|yielded|failed)

Update rules:
- elastic strain is derived from stress ratio each evaluation.
- plastic strain accumulates only above plastic threshold.
- failure is triggered when stress ratio exceeds fracture threshold.

## 5. Tiered Behavior
- Macro:
  - aggregate stress/failure summaries only.
- Meso:
  - deterministic graph load distribution and deformation updates.
- Micro (ROI):
  - overlay-only deformation visualization (color/glyph), no mesh mutation.

## 6. Integration Points
### 6.1 HazardModel
- Hazards consume stress/failure outputs from mechanics.
- `stress_ratio > 1` can trigger fracture consequence process.

### 6.2 Effect system
- Active effects can modify effective max-load or machine-mediated structural capacity.
- Effects remain temporary and process-governed.

### 6.3 SpecSheet
- Spec compliance may consume mechanics summaries (load/stress/deformation).
- `spec.bridge` and `spec.track` can evaluate load/stress constraints deterministically.

### 6.4 MOB hooks
- Mechanics publishes deterministic stress/misalignment risk signals.
- MOB can derive derailment risk and speed-cap suggestions from those signals.

## 7. Determinism and Budget Guarantees
- Ordering:
  - graphs sorted by `structural_graph_id`
  - edges sorted by `edge_id`
  - nodes sorted by `node_id`
- Tick-only evolution; no wall-clock.
- RS-5 budget degradation is deterministic and explicit.
- All authoritative mutation is process-only.

## 8. Non-Goals (MECH-1)
- No FEM or continuous PDE solver.
- No runtime mesh topology mutation in this phase.
- No bypass of control/process authority boundaries.
