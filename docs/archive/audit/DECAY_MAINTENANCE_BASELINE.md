Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Decay Maintenance Baseline

## Scope
MAT-6 baseline introduces deterministic macro-first decay/failure/maintenance substrate integrated with commitments, provenance, conservation accounting, and inspection overlays.

## Failure Modes
- Registry: `failure_mode_registry`
- Baseline mode IDs:
  - `failure.corrosion.basic`
  - `failure.fatigue.basic`
  - `failure.thermal_cycling.basic`
  - `failure.wear.general`
- Trigger default: deterministic threshold crossing over accumulated wear.

## Maintenance Policies
- Registry: `maintenance_policy_registry`
- Baseline policies:
  - `maint.policy.default_realistic`
  - `maint.policy.rank_strict`
  - `maint.policy.none`
- Backlog growth rules:
  - `backlog.linear_stub`
  - `backlog.stepwise_stub`

## Runtime Behavior
- New deterministic process family:
  - `process.decay_tick`
  - `process.maintenance_schedule`
  - `process.inspection_perform`
  - `process.maintenance_perform`
- Health state is tracked in canonical asset records with wear, hazard, and backlog.
- Failure events are explicit artifacts; no silent failures.

## Time Warp Behavior
- Decay supports large `dt_ticks` using deterministic bounded sub-step integration.
- Replay hash remains stable for equivalent inputs and policy context.

## Ledger Integration
- Failure/maintenance effects are accounted through process-level conservation deltas.
- Preferred closed-universe transformation:
  - usable mass decrement with corresponding `material.scrap.generic` increment
  - entropy metric increment (`quantity.entropy_metric`).
- Refusal on unaccounted mutation: `refusal.conservation_unaccounted`.

## Inspection UX
- Snapshot payload includes:
  - quantized wear channels
  - quantized failure risk summary
  - maintenance backlog
  - next maintenance commitments
- Overlay behavior:
  - failed nodes highlighted
  - wear color coding
  - maintenance glyph metadata
- Epistemic precision is policy-gated.

## Extension Points
- MAT-7: micro-part materialization can bind asset health to explicit micro instances.
- Future fracture/thermo solvers can plug into failure mode `hazard_inputs` and `maintenance_effect_model_id`.
- Multiplayer proof bundles can include maintenance/failure trace attestations.

## Gate Summary
- RepoX: PASS (MAT-6 invariants wired)
- AuditX: run (MAT-6 analyzers wired)
- TestX: PASS (MAT-6 deterministic tests and guard presence)
- strict build: PASS
- ui_bind --check: PASS
