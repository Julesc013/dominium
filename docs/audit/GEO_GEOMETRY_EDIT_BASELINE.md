Status: BASELINE
Last Updated: 2026-03-09
Version: 1.0.0
Scope: GEO-7 deterministic geometry state, process-only edit application, MAT provenance, coupling outputs, ROI micro hooks, proof/replay, and enforcement.

# GEO Geometry Edit Baseline

## 1) Scope

GEO-7 freezes the deterministic geometry edit contract on top of:

- GEO-0 topology, metric, partition, and projection constitutions
- GEO-1 stable GEO cell identity
- GEO-2 frame and precision discipline
- GEO-3 metric and neighborhood query routing
- GEO-4 GEO-bound field sampling and partition storage
- GEO-5 projection and lens gating
- GEO-6 deterministic pathing and shard-stage traversal

The authoritative doctrine is:

- `docs/geo/GEOMETRY_EDIT_CONTRACT.md`

Relevant invariants and contracts upheld:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A6 Provenance is mandatory
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C3 CompatX obligations
- `INV-GEOMETRY-MUTATION-PROCESS-ONLY`
- `INV-GEOMETRY-EDIT-RECORDED`
- `INV-NO-DIRECT-TERRAIN-WRITES`

## 2) Retro Audit Summary

Retro-consistency findings are recorded in `docs/audit/GEO7_RETRO_AUDIT.md`.

The audit confirmed:

- the repo had no canonical GEO-bound solid-occupancy substrate before GEO-7
- prior geometry-related mobility guide-geometry work did not provide terrain/earthwork mutation semantics
- excavation and construction provenance needed to route through MAT batch surfaces rather than ad hoc counters
- any future terrain mutation had to be blocked from direct state writes outside process runtime commit paths

GEO-7 therefore stayed targeted:

- no voxel renderer
- no FEM or PDE terrain solve
- no hidden geometry mutation from tools or UI paths
- no wall-clock or nondeterministic refinement behavior

## 3) Geometry State Baseline

New schemas:

- `schema/geo/geometry_cell_state.schema`
- `schema/geo/geometry_chunk_state.schema`
- `schema/geo/geometry_edit_event.schema`

New registry:

- `data/registries/geometry_edit_policy_registry.json`

Frozen edit policies:

- `geo.edit.default`
- `geo.edit.rank_strict`
- `geo.edit.lab_aggressive`

Canonical GEO-7 state is keyed by `geo_cell_key`:

- macro state stores `material_id`, `occupancy_fraction`, `height_proxy`, `permeability_proxy`, and `conductance_proxy`
- optional ROI micro state stores chunk payload references under `geometry_chunk_state`
- authoritative state hashes derive from geometry cell rows, chunk rows, and canonical geometry edit events

Core runtime lives in:

- `src/geo/edit/geometry_state_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

## 4) Edit Operations

Frozen authoritative process paths:

- `process.geometry_remove`
- `process.geometry_add`
- `process.geometry_replace`
- `process.geometry_cut`

Frozen helper surfaces:

- `geometry_remove_volume(...)`
- `geometry_add_volume(...)`
- `geometry_replace_material(...)`
- `geometry_cut_volume(...)`
- `geometry_state_hash_surface(...)`

Key runtime rules:

- all target cells are sorted by canonical `geo_cell_key` ordering
- `volume_amount` is bounded in deterministic GEO occupancy units
- add/remove/replace/cut never mutate truth outside process runtime commit paths
- policy refusals are explicit and explainable
- ROI micro edits are opt-in and remain bounded by declared policy budgets

## 5) Provenance Rules

GEO-7 freezes excavation and fill provenance through MAT batches and canonical edit events.

Removed material:

- emits `geometry_edit_event`
- produces deterministic `artifact.material_batch.geometry_edit` batches
- preserves `geo_edit_id` and source process provenance

Added material:

- consumes declared MAT batches deterministically
- records consumed batch ids in the authoritative process result
- refuses when required mass is unavailable

Canonical edit logging now includes:

- `geometry_edit_events`
- `artifact.geometry_edit_event.*`
- `geometry_edit_event_hash_chain`
- `geometry_state_hash_chain`

## 6) Coupling Effects

GEO-7 does not write directly into FLUID, THERM, or MECH truth state. Instead it emits deterministic model and adjustment surfaces.

Frozen coupling outputs:

- MECH instability hazard rows through `hazard.geo.instability`
- FLUID permeability adjustments through `channel.fluid.permeability.geo`
- THERM conductance adjustments through `channel.therm.conductance.geo`

New quantity registry anchors:

- `quantity.geo.permeability_proxy`
- `quantity.geo.conductance_proxy`

Coupling contract ids emitted by GEO-7:

- `coupling.geo_to_mech.instability_stub`
- `coupling.geo_to_fluid.permeability_stub`
- `coupling.geo_to_therm.conductance_stub`

## 7) ROI Micro And Compaction

ROI micro support remains optional and bounded.

Frozen hooks:

- `build_micro_geometry_chunk_from_cell_state(...)`
- `geometry_apply_micro_chunk_edit(...)`
- `aggregate_geometry_chunk_to_cell(...)`

Behavior:

- micro chunks are created only when `roi_micro` is explicitly requested and policy allows it
- compacted macro state remains authoritative
- compaction markers remain derived and replay-verifiable
- expand must reconstruct from deterministic state plus retained chunk payloads or refuse

## 8) Lens And Explain Integration

GEO-7 exposes lawful derived surfaces for observation without truth leaks.

New lens layer:

- `layer.geometry_occupancy`

New explain contracts:

- `explain.geometry_edit_refused`
- `explain.collapse_due_to_instability`

Projection/lens adapters can now show:

- excavated cells
- solid occupancy proxies
- tunnel-like occupancy gaps as derived stubs

All presentation remains derived from lawful lens/view surfaces rather than direct truth reads in UI code.

## 9) Proof And Replay Baseline

Proof and replay surfaces added:

- `tools/geo/tool_replay_geometry_window.py`

Control/server/shard proof surfaces now carry:

- `geometry_edit_policy_registry_hash`
- `geometry_state_hash_chain`
- `geometry_cell_state_hash_chain`
- `geometry_chunk_state_hash_chain`
- `geometry_edit_event_hash_chain`

Replay verification re-runs deterministic edit fixtures and checks:

- recorded versus observed geometry hash chains
- repeated-run stability
- compaction marker hash stability

## 10) Enforcement Baseline

RepoX scaffolding added:

- `INV-GEOMETRY-MUTATION-PROCESS-ONLY`
- `INV-GEOMETRY-EDIT-RECORDED`
- `INV-NO-DIRECT-TERRAIN-WRITES`

AuditX analyzers added:

- `E346_DIRECT_GEOMETRY_WRITE_SMELL`
- `E347_UNLOGGED_TERRAIN_EDIT_SMELL`

These checks enforce:

- process-owned geometry state persistence
- canonical edit-event recording and proof surfaces
- replay verifier presence
- prevention of direct authoritative terrain writes outside process runtime

## 11) Contract And Schema Impact

Changed:

- new GEO-7 schemas and edit policy registry
- new GEO geometry state and edit helpers
- new authoritative process runtime handlers for add/remove/replace/cut
- new MAT provenance surfaces for geometry debris and fill consumption
- new derived coupling outputs for MECH/FLUID/THERM
- new replay/proof hash anchors for geometry edit state
- new RepoX/AuditX/TestX GEO-7 enforcement and validation scaffolding

Unchanged:

- process-only mutation invariant
- truth tick ordering
- projection/lens truth isolation
- worldgen ownership of authored terrain content
- PDE/FEM non-goals

## 12) Validation Snapshot

Executed during GEO-7 baseline:

- targeted GEO-7 TestX subset
- geometry replay verifier
- strict RepoX/AuditX gate runs on the finished baseline
- deterministic many-edits stress fixture
- strict build and topology regeneration

## 13) Readiness

GEO-7 is ready for:

- GEO-8 worldgen interface binding

because the repository now has:

- deterministic solid occupancy and material state keyed by GEO cells
- process-only excavation, fill, replace, and cut operations
- MAT provenance for removed and added material
- derived coupling surfaces for downstream mechanical, fluid, and thermal systems
- replay-stable geometry edit hashes and proof anchors
