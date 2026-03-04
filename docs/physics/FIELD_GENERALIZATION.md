# Field Generalization Constitution

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-2 deterministic field catalog and coupling doctrine.

## 1) Purpose

Define a uniform FieldLayer contract for gravity, radiation, magnetic stub, irradiance, and future fields without introducing solver-level nondeterminism.

## 2) Canonical Field Types

Normative initial set:

- `field.temperature`
- `field.gravity_vector`
- `field.radiation_intensity`
- `field.magnetic_flux_stub`
- `field.irradiance`

Compatibility aliases may exist, but canonical references in new contracts must use the IDs above.

## 3) Field Properties Contract

Each field type must declare:

- dimensional vector (`dimension_vector`)
- deterministic default value (`default_value`)
- update policy binding (`update_policy_id`)
- deterministic fingerprint

Sampling contract:

- deterministic by input tuple `(field_id, spatial_node_id, tick)`
- sample artifacts are replay/proof hashable
- no wall-clock dependence

## 4) Update Sources (Only Legal Paths)

Field values may change only through:

- scheduled update policy execution (`process.field_tick`)
- explicit boundary/process update (`process.field_update`)
- constitutive model output routed through process pathways

Direct domain mutation of field state is forbidden.

## 5) Tiering

- `F0`: static/profile-defined coarse fields (default)
- `F1`: scheduled meso updates (deterministic, no PDE requirement)
- `F2`: ROI refinement reserved for future phases

Tier transitions remain budget-governed and deterministic.

## 6) Coupling Discipline

Cross-domain coupling contract:

`Field sample -> ConstitutiveModel -> {Effects | Hazards | Flow adjustments | Derived quantities}`

Rules:

- model inputs read fields via declared `input_signature` references
- models do not directly mutate field state
- any field mutation emitted by model outputs must route through `process.field_update`

## 7) Deterministic Ordering Requirements

- field type iteration sorted by `field_id`
- spatial update/sample iteration sorted by `spatial_node_id`
- deterministic cache key for samples:
  - `(field_id, spatial_node_id, tick)`

## 8) Boundary and Shard Contract

- cross-shard field continuity is mediated by boundary artifacts only
- no direct cross-shard state reads/writes from field evaluation logic
- deterministic merge policy required at shard boundaries

See `docs/physics/FIELD_SHARD_RULES.md`.

## 9) Non-Goals

- no PDE solvers in PHYS-2
- no wall-clock-coupled update loops
- no mandatory default-pack dependency for null boot

