--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Domain rules, transitions, and interest binding.
SCHEMA:
- Scale domain record formats and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No physics simulation in scale domains.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_SCALE_DOMAINS - Scale Domains (CIV4)

Status: draft  
Version: 1

## Purpose
Define explicit scale domains and their deterministic constraints.

## ScaleDomain schema
Required fields:
- domain_id
- domain_type (local/planetary/orbital/system/interstellar/galactic/universal)
- min_warp
- max_warp
- default_step_act
- fidelity_limit (macro/meso/micro)

Rules:
- Domain definitions are explicit and immutable at runtime.
- Warp limits are integers and deterministic.
- Fidelity limits are enforced by interest binding.

## Determinism requirements
- Domain IDs are stable and ordered.
- No global scans across domains each tick.

## Integration points
- Time warp: `schema/scale/SPEC_SCALE_TIME_WARP.md`
- Logistics flows: `schema/scale/SPEC_INTERPLANETARY_LOGISTICS.md`
- Interest sets: `docs/SPEC_INTEREST_SETS.md`

## Prohibitions
- No physical orbital simulation for CIV4.
- No omniscient global domain state in UI.
