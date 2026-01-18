--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Production recipes, scheduling, and enforcement rules.
SCHEMA:
- Recipe format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No stochastic production.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_PRODUCTION_CHAINS — Production Recipes (CIV1)

Status: draft  
Version: 1

## Purpose
Define deterministic production recipes and their scheduling requirements.

## ProductionRecipe schema
Required fields:
- recipe_id
- inputs (asset_id + qty; bounded list)
- outputs (asset_id + qty; bounded list)
- duration_act (ACT ticks)

Optional fields:
- byproducts (asset_id + qty; bounded list)

Rules:
- inputs/outputs lists are deterministically ordered (by asset_id).
- duration_act uses ACT time only.

## Determinism requirements
- Recipe application must be deterministic and replay-safe.
- Batch vs step equivalence MUST hold for production completion.

## Integration points
- Building machines: `schema/civ/SPEC_BUILDINGS_MACHINES.md`
- Logistics flows: `schema/civ/SPEC_LOGISTICS_FLOWS.md`

## Prohibitions
- No hidden inputs or implicit outputs.
- No floating point quantities.
