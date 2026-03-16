Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MECH-1 Mechanics Substrate Baseline

Status: CANONICAL  
Last Updated: 2026-03-01  
Scope: Structural graph mechanics, deterministic load propagation, fracture/failure, and integration hooks.

## 1) Structural Graph Model

MECH-1 introduces deterministic structural mechanics over a graph overlay:

- `structural_graph`: graph identity (`structural_graph_id`), assembly anchor (`assembly_id`), sorted node/edge refs.
- `structural_node`: applied force/torque, elastic/plastic strain, failure state.
- `structural_edge`: connection type, stiffness, max load, fatigue state, failure state, stress ratio, evaluated load.
- `connection_type_registry`: canonical defaults for `conn.weld`, `conn.bolt`, `conn.glue`, `conn.hinge`, `conn.rope`, `conn.cable`, `conn.rigid_joint`.

Deterministic ordering:

- Graphs sorted by `structural_graph_id`.
- Edges sorted by `edge_id`.
- Nodes sorted by `node_id`.

## 2) Load Propagation Algorithm

Meso-tier deterministic evaluator: `evaluate_structural_graphs(...)`

- Per-edge load is derived from connected node force/torque, degree-normalized.
- `stress_ratio_permille = applied_load / effective_max_load` (fixed-point integer permille).
- Effect hook:
  - `effect.machine_degraded` (`machine_output_permille`) reduces effective edge max load.
  - Edge target first, then graph target, then assembly target (deterministic fallback).
- Budgeting:
  - Cost units consumed per evaluated graph.
  - If budget is insufficient, evaluation degrades deterministically with `degrade.mechanics.budget` and stable skipped-graph ordering.

MOB hooks:

- `track_alignment_error_permille` raises effective load.
- `derailment_risk_permille` is derived from stress + alignment and persisted on edge extensions.
- Stress summaries expose `recommended_speed_cap_permille` for downstream speed capping via Effects.

## 3) Fracture Behavior

Processes:

- `process.mechanics_tick`
  - Runs graph evaluation.
  - Produces deterministic fracture candidates (`fracture_edge_ids`).
  - Emits pending deterministic fracture intents (`process.mechanics_fracture`) and provenance.
- `process.mechanics_fracture`
  - Marks edge failed/detached.
  - Updates assembly detach tracking.
  - Optionally updates interior portal sealing/leak hazards when linked.
  - Emits mechanics provenance event.

Tool-integrated structural mutation:

- `process.weld_joint` increases edge strength (`max_load`) deterministically.
- `process.cut_joint` reduces edge strength or fractures deterministically.
- `process.drill_hole` reduces node integrity and increases plastic strain deterministically.

Task integration:

- New task types:
  - `task.weld_joint` -> `process.weld_joint`
  - `task.cut_joint` -> `process.cut_joint`
  - `task.drill_hole` -> `process.drill_hole`

## 4) Integration: MAT / SPEC / MOB / CTRL

MAT integration:

- Mechanics state is persisted in authoritative process runtime state:
  - `structural_graphs`, `structural_nodes`, `structural_edges`, `mechanics_provenance_events`.

SPEC integration:

- `check.structure.load_rating_stub` now consumes both load rating and stress ratio inputs.
- `process.spec_check_compliance` injects mechanics-derived load summary when available.
- `spec.track` hook applies/removes automatic `effect.speed_cap` based on stress-derived recommended cap.

MOB integration hooks:

- `derived.mob.track_stress_summary` contains stress/alignment/derailment fields for mobility control/risk logic.

Inspection/ROI visualization:

- Mechanics summaries are attached to inspection target payload extensions.
- ROI overlay mode `mechanics_overlay` renders:
  - Stress bucket coloring
  - Near-fracture crack glyphs
  - Deterministic risk labels
- Visual only; no mesh truth mutation.

## 5) Enforcement and Audit

RepoX hard invariants added:

- `INV-NO-ADHOC-LOAD-CHECK`
- `INV-STRUCTURAL-FAILURE-THROUGH-MECH`

AuditX analyzers added:

- `E137_STRUCTURAL_BYPASS_SMELL`
- `E138_INLINE_STRENGTH_CHECK_SMELL`

## 6) Extension Points (Future Advanced Physics)

MECH-1 leaves deterministic extension points for future depth without FEM/PDE:

- Richer connection constitutive laws per connection type.
- Fatigue evolution models and material-cycle effects.
- Localized micro deformation rendering tied to ROI policy.
- Deeper MOB coupling (track geometry, wheel/axle models, derailment consequence simulation).

## 7) Validation Snapshot (MECH-1 Finalization)

Executed on 2026-03-01:

- RepoX (`STRICT`): PASS (warning-only on existing AuditX finding volume threshold).
- AuditX scan: completed; artifacts refreshed under `docs/audit/auditx/`.
- TestX (MECH-1 suite):
  - `testx.mechanics.load_distribution_deterministic` PASS
  - `testx.mechanics.stress_ratio_calculation` PASS
  - `testx.mechanics.fracture_trigger` PASS
  - `testx.mechanics.weld_increases_strength` PASS
  - `testx.mechanics.plastic_strain_accumulates` PASS
  - `testx.mechanics.meso_budget_degradation` PASS
- Registry compile deterministic check: PASS after connection-type schema projection alignment.
- Strict build:
  - `cmake --preset msvc-verify` refused in this environment (Visual Studio 18 2026 not installed).
  - `cmake --preset linux-verify` configure failed due missing expected tool targets on this host profile.
