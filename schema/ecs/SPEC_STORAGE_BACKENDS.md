# SPEC_STORAGE_BACKENDS (ECSX0)

Schema ID: ECS_STORAGE_BACKENDS  
Schema Version: 1.0.0  
Status: binding.  
Scope: allowable physical storage backends for component data.

## Purpose
Define storage backends that may represent component data without changing
component meaning or serialization rules.

## Allowed Backends
### 1) SoA Archetype Columns (Default)
- Structure-of-arrays per archetype.
- Deterministic iteration by stable entity order.
- Suitable for authoritative simulation.

### 2) AoSoA Blocks (SIMD-friendly)
- Array-of-structure-of-arrays in fixed-size blocks.
- Deterministic block ordering and stable entity order within block.
- Must expose canonical iteration order identical to SoA.

### 3) Packed Bitfield Mirrors (Network/Visibility)
- Compact derived views for transmission or visibility filtering.
- Derived unless explicitly declared authoritative.
- Must use deterministic packing rules (see `SPEC_PACKING_AND_DELTAS.md`).

### 4) GPU Mirrors (Presentation/Derived)
- GPU-resident copies for rendering/preview.
- Derived only; must not affect authoritative state.

## Determinism Guarantees
Each backend MUST declare:
- deterministic iteration order,
- stable commit ordering semantics,
- rules for mapping entity sets to storage ranges.

No backend may use:
- pointer-address ordering,
- platform-dependent layout assumptions,
- nondeterministic parallel writes.

## Access IR Integration
Backends must map AccessSets to explicit ranges:
- component_id + field_id
- entity set / archetype / chunk range

Access declarations must be independent of physical layout.

## Commit Semantics
Backends must commit authoritative writes in stable order:
- commit key is derived from TaskNode commit_key
- writes are applied deterministically

Derived backends must be discardable and must not influence authoritative hashes.

## Prohibitions
- Encoding layout assumptions in component schema.
- Allowing backend-specific field meaning.
