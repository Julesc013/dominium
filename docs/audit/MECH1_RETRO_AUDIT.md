Status: ACTIVE
Version: 1.0.0
Owner: Core Engineering
Last Updated: 2026-03-01
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MECH1 Retro Audit

## Scope
- Prompt: `MECH-1 — Mechanics Substrate (Structural Graph, Load Propagation, Deformation, Fracture)`
- Audit target: ad hoc structural mechanics logic that should migrate to deterministic `StructuralGraph` + hazard/process pathways.
- Relevant invariants:
- `INV-PROCESS-ONLY-MUTATION`
- `INV-NO-ADHOC-LOAD-CHECK`
- `INV-STRUCTURAL-FAILURE-THROUGH-MECH`
- `INV-NO-ADHOC-TEMP-MODIFIERS`
- `INV-NO-WALLCLOCK-IN-PERFORMANCE`

## Findings

### 1) No canonical structural mechanics substrate exists in runtime
- Evidence:
  - No `src/mechanics/` module in current source tree.
  - No structural graph row families in process runtime state normalization.
- Impact:
  - Load path, deformation, and fracture behavior are not represented as deterministic first-class state.
- Migration:
  - Introduce `structural_graph`, `structural_edge`, `structural_node`, and deterministic evaluation engine with budgeted degradation.

### 2) Existing load/spec checks are compliance stubs, not mechanics propagation
- Evidence:
  - `src/specs/spec_engine.py` currently evaluates `check.structure.load_rating_stub` via summarized inputs, without graph propagation/deformation state.
- Impact:
  - Spec compliance can reason about declared ratings, but does not expose deterministic edge/node stress from live load paths.
- Migration:
  - Feed mechanics summaries (`stress_ratio`, deformation/failure states) into compliance input catalogs and checks.

### 3) Temporary degradation already uses Effect system, but not structural max-load hooks
- Evidence:
  - `tools/xstack/sessionx/process_runtime.py` maintenance tick emits `effect.machine_degraded` with `machine_output_permille`.
- Impact:
  - Temporary machine degradation is deterministic and process-driven, but it does not currently reduce structural connection/node load capacity.
- Migration:
  - Integrate effect modifiers into mechanics effective `max_load` calculations.

### 4) Connection semantics are currently tag-level only
- Evidence:
  - `schema/materials/connection_type.schema` models declarative tags.
  - `data/registries/connection_type_registry.json` currently stores tag-like connection entries.
- Impact:
  - No canonical stiffness/max-load/rotation/translation support contract for deterministic structural evaluation.
- Migration:
  - Add mechanics connection schema/registry fields for stiffness, load caps, motion support flags, fatigue state.

### 5) No unified fracture process family present
- Evidence:
  - No `process.mechanics_fracture` handler in process runtime.
  - No deterministic structural failure provenance stream.
- Impact:
  - Structural failure cannot be reenacted through a dedicated mechanics process boundary.
- Migration:
  - Add `process.mechanics_fracture` as consequence process with deterministic provenance and graph detach semantics.

## Migration Plan

### Phase A: Contracts and schemas
- Add mechanics schemas (`structural_graph`, `structural_edge`, `structural_node`, `connection_type`).
- Upgrade connection registry with mechanics-capable defaults.

### Phase B: Deterministic engine + process mutation
- Implement graph-based load propagation/deformation updates.
- Add fracture process and state persistence hooks.

### Phase C: Integrations and enforcement
- Integrate ACT tool tasks (`weld/cut/drill`) with structural mutations.
- Integrate effects/spec hooks and ROI deformation overlays.
- Add RepoX/AuditX rules for mechanics bypass and inline strength checks.

## Deprecation Entries Required
- Existing tag-only connection semantics should remain supported as compatibility aliases, but mechanics-aware fields become the canonical path for structural behavior.
- Any future inline `if load > X then break` logic outside mechanics runtime must be rejected by enforcement rules.

## Acceptance Criteria for Audit Closure
- Structural load propagation order is deterministic (`graph_id`, then `edge_id`).
- Fracture/failure mutation routes through mechanics process handlers only.
- No wall-clock or nondeterministic branching introduced.
- Spec/effect integrations consume mechanics state without bypassing process-only mutation.
