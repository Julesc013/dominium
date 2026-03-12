Status: AUDIT
Last Updated: 2026-03-09
Scope: GEO-7 geometry edit contract retro-consistency audit
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO7 Retro Audit

## 1) Scope

This audit reviews the current repository for terrain and geometry mutation assumptions before GEO-7 introduces a canonical geometry edit substrate.

Relevant constraints:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A6 Provenance is mandatory
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` C1 Version semantics

## 2) Existing Geometry And Terrain Assumptions

Observed canonical contracts already present:

- `schema/terrain.overlay.schema`
  - defines auditable terrain overlay records
  - documents process-only edit intent at the schema level
- `schema/terrain.macro_capsule.schema`
  - defines macro terrain capsule summaries for collapse and expand
- `schema/terrain.field.schema`
  - treats terrain truth as field stack identifiers such as `terrain.phi`
- `docs/worldgen/TERRAIN_GEOMETRY_BASELINE.md`
  - describes terrain truth in terms of SDF-style field layers
  - explicitly defers construction and destruction behavior
- `docs/worldgen/MINING_AND_EXTRACTION_BASELINE.md`
  - describes mining as terrain overlays and process outputs, not direct mesh mutation
- `docs/worldgen/BUILDING_AND_DESTRUCTION_BASELINE.md`
  - routes building and destruction through fields, support, and process outcomes

These documents establish intent, but there was no first-class GEO runtime for occupancy/material edits over `geo_cell_key`.

## 3) Existing Runtime Mutation Surfaces

Current runtime surfaces found:

- `tools/xstack/sessionx/process_runtime.py`
  - already contains `process.geometry_create`
  - already contains `process.geometry_edit`
  - already contains `process.geometry_finalize`
  - these handlers operate on guide geometry for mobility and formalization workflows
  - they do not mutate world solid occupancy or terrain material state
- `src/mobility/geometry/geometry_engine.py`
  - owns mobility guide geometry identities and derived metrics
  - not suitable as terrain or excavation truth
- `src/fields/field_engine.py`
  - field truth is GEO-keyed after GEO-4
  - field storage can host terrain-adjacent values, but does not currently store canonical excavatable solid occupancy/material state

Conclusion:

- existing `process.geometry_*` handlers are not a terrain edit substrate
- no canonical world solid edit runtime existed before GEO-7

## 4) Direct Terrain Or Geometry Mutation Findings

Searches across `src/`, `tools/`, `docs/`, `schema/`, and `data/` found:

- many terrain and mining references in docs and schemas
- no canonical `process.geometry_remove`, `process.geometry_add`, `process.geometry_replace`, or `process.geometry_cut`
- no dedicated `geometry_cell_state` runtime store
- no dedicated `geometry_edit_event` canonical record type

Risk areas identified:

- field-based terrain truth alone does not preserve material batch provenance for excavation/fill
- worldgen docs reference overlays and SDF concepts that would otherwise encourage parallel one-off implementations
- the name `process.geometry_edit` is already used for mobility guide geometry and must not be reused semantically for terrain excavation

## 5) Direct Mutation Risk Assessment

No existing authoritative direct terrain write path was found that already mutates a world solid occupancy store.

This is good from a constitutional perspective:

- GEO-7 can introduce a new process-only path without breaking an existing direct-write runtime
- migration pressure is mostly from documentation intent and future feature prompts, not from entrenched runtime code

Potential smell points to guard against after GEO-7:

- ad hoc writes to `geometry_cell_states`
- ad hoc writes to `geometry_chunk_states`
- unlogged modifications to terrain-like occupancy or fill fraction values

## 6) Required GEO-7 Migration Points

Future geometry-affecting systems should route through GEO-7 instead of inventing bespoke mutation paths:

- mining and excavation processes
- demolition and rubble generation
- fill, grading, and terraforming
- tunnel or boolean-cut authoring
- collapse/expand compaction surfaces for edited cells
- future fluid permeability and thermal conductance updates tied to excavated or filled cells

Likely integration points:

- MAT batch creation and consumption
- MECH instability hazard generation
- FLUID permeability proxy lookup
- THERM conductance proxy lookup
- GEO-5 lens layers for excavation/occupancy visibility
- SYS collapse and expand metadata

## 7) GEO-7 Implementation Notes

Recommended implementation posture:

- introduce new `src/geo/edit` runtime rather than extending mobility geometry runtime
- keep authoritative mutation inside `tools/xstack/sessionx/process_runtime.py`
- keep geometry state normalization and edit arithmetic pure and deterministic
- record every authoritative edit as a canonical `geometry_edit_event`
- maintain macro cell state keyed by `geo_cell_key`
- treat ROI micro chunks as optional derived detail over a macro parent cell

## 8) Audit Outcome

The repository is ready for GEO-7.

No blocking canonical conflict was found, provided that:

- world solid edits remain process-only
- geometry edit provenance is always recorded
- new world geometry state is kept separate from existing mobility guide geometry state
