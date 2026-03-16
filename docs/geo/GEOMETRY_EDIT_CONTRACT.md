Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## GEO-7 Geometry Edit Contract

### Purpose

GEO-7 freezes the deterministic geometry edit substrate for excavation, fill, replacement, cutting, and compaction over GEO-partitioned space.

This substrate is for world solid occupancy and material truth.

It is distinct from the existing mobility guide geometry workflow:

- `process.geometry_create`
- `process.geometry_edit`
- `process.geometry_finalize`

Those process ids continue to describe authored guide geometry and formalization. GEO-7 introduces world-solid edit processes instead of reusing that meaning.

### A. Geometry Representation Levels

Authoritative geometry truth is partition-bound and GEO-keyed.

Macro geometry:

- keyed by `geo_cell_key`
- each cell carries:
  - `material_id`
  - `occupancy_fraction`
  - optional `height_proxy`
  - `permeability_proxy`
  - `conductance_proxy`

Macro geometry is the canonical minimum truth required outside ROI.

ROI micro geometry:

- optional finer subdivision under a macro parent cell
- represented by versioned chunk payloads or deterministic subcell descriptors
- used only when explicit ROI detail is required

Micro geometry must aggregate deterministically back into macro descriptors.

### B. Edit Operations

Canonical GEO-7 edit operations are:

- `process.geometry_remove`
  - excavation, mining, demolition removal
- `process.geometry_add`
  - fill, embankment, construction material deposition
- `process.geometry_replace`
  - remove then add with deterministic ordering
- `process.geometry_cut`
  - bounded multi-cell removal along an explicit path

All geometry edit operations:

- are deterministic
- are process-only mutations
- require explicit authority
- sort target cells by canonical `geo_cell_key` ordering
- use bounded volume application rules
- emit canonical edit records

No renderer, tool, lens, or ad hoc helper may mutate authoritative geometry state directly.

### C. Conservation And Provenance

Geometry edits are material events, not silent occupancy changes.

Removal:

- removed solid volume produces `material_out`
- `material_out` is represented as deterministic MAT batch rows
- generated batch identity must derive from:
  - process id
  - tick
  - target cell key set
  - material id
  - removed quantity

Addition:

- fill or construction consumes `material_in`
- consumed batches are decremented deterministically
- refusal is required when supplied material is missing or insufficient

Replacement:

- deterministic remove first
- deterministic add second
- both sides are recorded in one canonical edit event or a deterministic pair of linked records

Energy and entropy consequences remain process-mediated:

- tool/work transforms may emit heat or ledger hooks
- GEO-7 does not bypass PHYS conservation or accounting surfaces

### D. Coupling Updates

Geometry edits modify couplings through declared coupling contracts and deterministic model outputs.

Required GEO-7 coupling surfaces:

- FLUID-facing `permeability_proxy`
- THERM-facing `conductance_proxy`
- MECH-facing `stability_hazard`
- POLL-facing contamination tags or future placeholders

Rules:

- geometry code may update geometry-owned proxy values
- geometry code must not directly mutate FLUID, THERM, MECH, or POLL truth stores
- cross-domain consequences must be surfaced as:
  - coupling evaluation records
  - derived outputs
  - hazards
  - effects
  - future domain processes

### E. Compaction And Expansion

Micro edits may compact into macro descriptors when ROI detail is no longer required.

Compaction rules:

- `geometry_edit_event` is canonical and never compacted away
- `geometry_chunk_state` is derived and compactable
- macro compaction descriptors summarize:
  - net occupancy
  - dominant material
  - proxy values
  - micro provenance reference

Expansion rules:

- expansion may restore micro detail only when deterministic source data is available
- deterministic source data may include:
  - persisted chunk payload
  - edit log replay
  - state vector anchor plus edit log
- if deterministic restoration is not possible, the system must remain at macro state or refuse expansion explicitly

### F. Ordering And Bounds

Canonical cell ordering is:

1. `chart_id`
2. `index_tuple`
3. `refinement_level`

Canonical edit ordering is:

1. tick
2. process id
3. target cell ordering
4. edit kind

All edit application loops must be bounded by:

- explicit target cell lists
- explicit `volume_amount`
- optional policy caps
- ROI chunk limits

Unbounded flood-fill or mesh-wide terrain mutation is forbidden in GEO-7.

### G. ROI And Macro Aggregation

Inside ROI:

- edits may resolve at micro chunk granularity
- chunk outputs aggregate into macro cell state deterministically

Outside ROI:

- edits remain macro
- the authoritative truth is still cell-keyed
- no hidden micro simulation is required

This keeps excavation and construction scalable without losing provenance.

### H. Lens And Explain Integration

Geometry edit consequences may be observed only through lawful lens layers and explain contracts.

Baseline GEO-7 observation surfaces:

- `layer.geometry_occupancy`
- excavation area markers
- tunnel markers stub
- diegetic survey or ground-scanner readouts when instrument policy allows

Baseline explain contracts:

- `explain.geometry_edit_refused`
- `explain.collapse_due_to_instability`

### I. Non-Goals

GEO-7 does not implement:

- voxel rendering
- full FEM terrain solving
- PDE erosion or granular flow
- hidden wall-clock throttling
- direct UI or tool mutation of geometry truth
