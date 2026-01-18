--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Needs thresholds, consumption policy, and survival rules.
SCHEMA:
- Needs state record format and versioning metadata.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No floating-point consumption values.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_NEEDS_MINIMAL — Needs State Canon (CIV0a)

Status: draft  
Version: 1

## Purpose
Define the minimal deterministic needs state used by the CIV0a survival loop.

## NeedsState schema (minimal)
Required fields:
- food_store (units)
- water_store (units)
- shelter_level (proxy level)
- hunger_level (bounded)
- thirst_level (bounded)
- last_consumption_tick (ACT)
- next_consumption_tick (ACT)

Optional fields:
- last_production_provenance (provenance ref)

## Determinism requirements
- All values are integer and deterministic.
- Consumption is event-driven at next_consumption_tick.
- Batch vs step equivalence MUST hold.

## Prohibitions
- No global per-tick consumption scans.
- No implicit food or water generation.
