# SPEC_COMPONENT_SCHEMA (ECSX0)

Schema ID: ECS_COMPONENT_SCHEMA  
Schema Version: 1.0.0  
Status: binding.  
Scope: logical component definitions and ownership.

## Purpose
Define a stable, versioned schema layer for ECS components so that:
- component meaning is fixed by schema,
- physical storage is a backend choice,
- serialization and deltas are schema-driven and deterministic,
- game components can evolve without rewriting engine storage.

## Core Definitions
### Component
A component is a logical bundle of fields with stable semantics.

Required fields:
- `component_id` (stable, unique, numeric or stable hash)
- `name` (human-readable)
- `owner` (ENGINE or GAME)
- `version` (semver)
- `fields[]` (ordered by field_id)

### Field
A field is an atomic, typed element within a component.

Required fields:
- `field_id` (stable numeric or stable hash)
- `name` (human-readable)
- `type` (portable, fixed-width; see `docs/specs/SPEC_NUMERIC.md`)
- `determinism_class` (AUTHORITATIVE, DERIVED, PRESENTATION)

Optional fields:
- `packing_hints` (e.g., bit width, alignment class)
- `delta_hints` (e.g., baseline group, quantization hint)
- `bounds` (min/max or domain constraints)

## Ownership and Scope
### ENGINE-owned components
- Provide primitives required by engine mechanisms (e.g., identity, spatial anchor).
- Must remain stable and portable.
- Must NOT be extended or modified by mods.

### GAME-owned components
- Define gameplay state and rules.
- May be extended only through schema changes, with version bumps and migration notes.
- Must remain deterministic if sim-affecting.

Ownership is explicit and enforced by schema validators.

## Field Order and Serialization
Field order is **by field_id only**. Do not encode layout assumptions.
Serialization rules are defined in `SPEC_PACKING_AND_DELTAS.md`.

## Versioning Rules
Semver applies to each component:
- MAJOR: meaning or determinism changes; migration required or refusal policy.
- MINOR: additive fields; must include default/migration rules.
- PATCH: non-semantic or documentation changes only.

Field changes:
- Rename is allowed if `field_id` does not change.
- Removal is deprecation only; field_id is never reused.

## Migration Rules
Any sim-affecting change requires:
- explicit migration or refusal policy,
- deterministic defaulting rules (no silent fallbacks),
- version bump per `schema/SCHEMA_VERSIONING.md`.

## Field ID Assignment Policy
Field IDs are stable and never reused. See `SPEC_FIELD_IDS.md`.

## Examples
### Engine-Owned Example (Identity)
```
component_id: 1001
name: "Identity"
owner: ENGINE
version: 1.0.0
fields:
  - field_id: 1
    name: "entity_id"
    type: U64
    determinism_class: AUTHORITATIVE
  - field_id: 2
    name: "spawn_tick"
    type: I64
    determinism_class: AUTHORITATIVE
```

### Game-Owned Example (Population)
```
component_id: 2001
name: "PopulationCohort"
owner: GAME
version: 1.2.0
fields:
  - field_id: 1
    name: "cohort_id"
    type: U64
    determinism_class: AUTHORITATIVE
  - field_id: 2
    name: "count"
    type: U32
    determinism_class: AUTHORITATIVE
  - field_id: 3
    name: "morale_q16"
    type: I32
    determinism_class: AUTHORITATIVE
    bounds: { min: -65536, max: 65536 }
  - field_id: 4
    name: "ui_color_tag"
    type: U32
    determinism_class: PRESENTATION
```

## Prohibitions
- Adding fields without stable `field_id`.
- Reusing `field_id` for different meaning.
- Using float fields in authoritative components.
- Encoding physical layout in the logical schema.
