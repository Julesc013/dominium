# PHYS-2 Retro Consistency Audit

Status: AUDIT
Last Updated: 2026-03-04
Scope: PHYS-2 field generalization preflight audit.

## 1) Existing Field Types

Observed in `data/registries/field_type_registry.json`:

- canonical baseline: `field.temperature`, `field.moisture`, `field.friction`, `field.visibility`, `field.wind`
- physics additions present: `field.gravity_vector`, `field.radiation_intensity`, `field.magnetic_flux_stub`, `field.irradiance`
- legacy aliases still present for compatibility:
  - `field.gravity.vector` -> alias of `field.gravity_vector`
  - `field.radiation` -> alias of `field.radiation_intensity`

Migration note:

- retain alias rows for deterministic replay compatibility, but canonical references in new PHYS-2 bindings should use underscore IDs.

## 2) Direct Field Mutation Audit

Authoritative field write pathways found:

- `tools/xstack/sessionx/process_runtime.py`
  - `process.field_update` branch
  - model-output pathway for `process.field_update`
- `src/fields/field_engine.py`
  - deterministic normalization/query/update helpers

Risk:

- static analysis rules were missing dedicated blockers for direct field-state writes outside process paths.

Action:

- PHYS-2 adds RepoX rules:
  - `INV-FIELD-TYPE-REGISTERED`
  - `INV-FIELD-MUTATION-THROUGH-PROCESS`
- PHYS-2 adds AuditX analyzers:
  - `DirectFieldWriteSmell`
  - `UnregisteredFieldSmell`

## 3) Gravity Stub from PHYS-1

Observed:

- legacy model id `model.phys.gravity_stub` remained active.
- runtime auto-binding already checked canonical-first candidate (`model.phys_gravity_force`) with fallback to legacy id.

Migration:

- PHYS-2 promotes canonical model id `model.phys_gravity_force`.
- legacy id remains as deprecated alias for replay compatibility.

## 4) Hardcoded Environmental Modifiers

Observed:

- existing field modifier synthesis remains process-driven via `process.field_tick`.
- no new hardcoded field mutation path introduced in PHYS-2 changes.

Residual risk:

- ad-hoc field references in future code can bypass registry if not governed.

Mitigation:

- enforce field-token registration via RepoX/AuditX checks added in PHYS-2.

## 5) Unified Field Catalog Migration Plan

1. Canonical IDs:
- adopt canonical names in all new bindings:
  - `field.gravity_vector`
  - `field.radiation_intensity`
  - `field.magnetic_flux_stub`
  - `field.irradiance`

2. Backward compatibility:
- keep legacy aliases and mark deprecated in registry extensions.

3. Process-only mutation:
- all authoritative field writes route through `process.field_update` + `_apply_field_updates`.

4. Deterministic sampling:
- retain `(field_id, spatial_node_id, tick)` sample identity with deterministic fingerprints.

