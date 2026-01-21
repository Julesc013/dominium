--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Building machine rules, ownership checks, and maintenance policy.
SCHEMA:
- Building/machine record formats and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No per-frame building ticks.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_BUILDINGS_MACHINES — Buildings as Machines (CIV1)

Status: draft  
Version: 1

NOTE: Legacy CIV1 spec. Superseded by CIV0+ canonical documents in
`schema/civ/README.md` and `schema/economy/README.md`. Retained for reference
and non-authoritative if conflicts exist.

## Purpose
Define deterministic building machines that drive production via scheduled
events, not per-frame ticks.

## BuildingMachine schema
Required fields:
- building_id
- type_id (schema-defined)
- owner_ref (person/org/estate)
- input_stores (refs)
- output_stores (refs)
- production_recipe_ref
- maintenance_state
- next_due_tick
- provenance_ref

Rules:
- input/output stores are explicit; no hidden inventories.
- production_recipe_ref MUST reference a production recipe spec.
- maintenance_state is deterministic and scheduled.

## Determinism requirements
- Machine scheduling is ACT-based and batch-vs-step equivalent.
- Start/complete events are deterministic and ordered.
- No random breakdowns or OS time usage.

## Integration points
- Production chains: `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- Logistics flows: `schema/civ/SPEC_LOGISTICS_FLOWS.md`
- Provenance law: `docs/SPEC_PROVENANCE.md`

## Prohibitions
- No fabricated outputs without inputs.
- No global tick loops over machines.
