--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Conservation rules, sink/source policies, decay handling.
SCHEMA:
- Resource conservation record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit resource creation or deletion.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_RESOURCE_CONSERVATION — Conservation Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define resource conservation invariants: goods and value must be produced,
transformed, consumed, or dissipated via explicit effects.

## ResourceConservationClass (canonical)
- CONSERVED (mass/energy-like; cannot be created or destroyed)
- TRANSFORMED (changes form with explicit inputs/outputs)
- DISSIPATIVE (decays over time with explicit loss policy)

## Required fields
- resource_id (stable, schema-defined)
- conservation_class (one of the canonical classes)
- unit_ref (measurement unit)
- source_refs (production or extraction contracts)
- sink_refs (consumption, decay, destruction)
- provenance_refs (origin and causal chain)

Optional fields:
- storage_constraints (capacity and loss behavior)
- transport_constraints (logistics requirements)

## Rules (absolute)
- No goods without production or extraction contracts.
- No production without inputs and schedule policy.
- Destruction and decay must be explicit and auditable.
- Conservation rules apply across macro and micro representations.

## Integration points
- Production chains: `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- Logistics: `schema/economy/SPEC_LOGISTICS.md`
- Infrastructure: `schema/civ/SPEC_INFRASTRUCTURE.md`
- Life populations: `schema/life/SPEC_POPULATION_MODELS.md`

## See also
- `docs/architecture/WHY_ECONOMIES_DONT_FAKE.md`
