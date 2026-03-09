Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# Sol Minimal Pin Pack

This document freezes the SOL-0 minimal official Sol overlay pack for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/STAR_SYSTEM_SEED_MODEL.md`
- `docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`

## 1. Purpose

`pack.sol.pin_minimal` is the official MVP Sol overlay pack.

Its purpose is limited to:

- pinning the Sol system identity lineage onto the procedural MW base
- supplying essential physical constants and coarse orbital elements
- making Sol, the eight major planets, Earth, and Luna feel recognizably correct

It is not a catalog pack, terrain pack, or Earth geography pack.

## 2. What The Pack Pins

The pack pins only the minimum hierarchy required for MVP recognition.

Pinned objects:

- the anchored `kind.star_system` representing Sol
- the primary `kind.star` representing Sol
- eight `kind.planet` bodies:
  - Mercury
  - Venus
  - Earth
  - Mars
  - Jupiter
  - Saturn
  - Uranus
  - Neptune
- one `kind.moon` body for Luna as an overlay-safe moon stub if procedural MW-2 did not materialize that moon

Pinned facts are limited to:

- stable display names
- stable hierarchy relationships
- coarse physical constants
- coarse orbital elements
- stable semantic tags needed for later Sol/Earth routing

## 3. What The Pack Does Not Pin

The pack must not include:

- DEM or terrain height data
- real Earth geography
- climate simulation outputs
- biomes or landcover datasets
- political borders
- cities, roads, or infrastructure
- authored surface tiles
- star catalogs beyond the Sol lineage

## 4. Sol Targeting Rule

The pack targets Sol by deterministic anchor, not by name lookup.

Required rule:

- the active realism profile declares one `sol_anchor_cell_key`
- the MW generator guarantees that the anchor cell yields at least one star-system seed
- the Sol star-system is the anchored system at local index `0`

Identity law remains unchanged:

- star-system ID derives from GEO-1 identity inputs
- star ID derives from the anchored Sol system ID and local subkey `star:0`
- planet IDs derive from the anchored Sol system ID and local subkeys `planet:0` through `planet:7`
- Luna derives from the anchored Sol system ID and moon slot `moon:2:0`

This keeps official Sol pinning compatible with later overlays and save patches.

## 5. Overlay Rules

The pack is a GEO-9 property-patch overlay only.

Allowed behavior:

- `set`/`replace` of properties on stable target object IDs
- addition of Luna as a lawful overlay moon stub if the procedural base lacks that object
- tagging Earth as `planet.earth` for later surface-generator routing

Forbidden behavior:

- deleting procedural objects
- replacing object identity
- patching immutable identity paths such as `object_id`
- changing the MW generator's general star or planet priors

The procedural base remains canonical.
The Sol pack only refines it.

## 6. Pinned Property Classes

The pack may pin only these coarse property classes:

- `display_name`
- `tags`
- `hierarchy.parent_object_id`
- `hierarchy.body_slot_id`
- `physical.mass_kg`
- `physical.radius_km`
- `spin.rotation_period_hours_milli`
- `spin.axial_tilt_mdeg`
- `orbit.semi_major_axis_milli_au`
- `orbit.eccentricity_permille`
- `orbit.inclination_mdeg`

Additional fine-detail surface, atmosphere, or geopolitical properties are outside SOL-0.

## 7. Trust And Official Status

`pack.sol.pin_minimal` is an official trusted overlay surface.

Required trust markers:

- pack manifest `signature_status` must be `signed` or stronger
- the overlay layer must be emitted as `layer_kind = official`
- GEO-9 trust validation must accept the layer under the existing official-pack trust path

This is the SOL-0 SecureX hook.
No online verification or live service dependency is introduced.

## 8. Precision Policy

All numeric values are intentionally coarse and fixed-point friendly.

Rules:

- masses are pinned as integer kilograms
- radii are pinned as integer kilometers
- rotation periods are pinned as integer `hours_milli`
- axial tilts and inclinations are pinned as integer `mdeg`
- semi-major axes are pinned as integer `milli_au`
- eccentricity is pinned as integer `permille`

SOL-0 must not introduce float-dependent runtime behavior.

## 9. Forward Compatibility

The minimal Sol pack is a stable base for later overlays.

Future layers may add:

- refined Sol ephemerides
- Earth and Moon macro detail
- named small bodies
- catalog-calibrated metadata

Those layers must still map onto the same GEO-owned identity lineage unless an explicit migration is declared.

## 10. Readiness Outcome

SOL-0 is complete when an official pack can:

- deterministically identify the anchored Sol lineage
- apply minimal physical/orbital overrides
- preserve procedural object IDs under overlay merge
- revert cleanly to procedural values when the official layer is absent

This yields a tiny official Sol surface suitable for MVP without introducing large datasets or catalog dependence.
