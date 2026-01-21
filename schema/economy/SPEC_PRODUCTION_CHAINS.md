--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic scheduling primitives.
GAME:
- Production rules, recipes, failure modes.
SCHEMA:
- Production chain record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No production without declared inputs.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_PRODUCTION_CHAINS — Production Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define deterministic production chains driven by explicit contracts with
inputs, outputs, capacity, and failure modes.

## ProductionContract (canonical)
Required fields:
- production_id (stable, unique within a timeline)
- actor_ref (producer)
- input_requirements (resources, labor, time)
- output_products (resources or services)
- capacity_limits (throughput, storage, energy)
- schedule_policy (ACT-based timing)
- failure_modes (refusal, defer, partial)
- provenance_refs (origin and causal chain)

Optional fields:
- maintenance_requirements (for infrastructure upkeep)
- logistics_requirements (required shipment links)
- market_output_refs (allowed market destinations)

## Rules (absolute)
- No production without inputs and schedule policy.
- Output is deterministic and bounded by capacity.
- Failure modes must be explicit (refuse or defer).
- Production never fabricates resources.

## Integration points
- Economic actors: `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- Resource conservation: `schema/economy/SPEC_RESOURCE_CONSERVATION.md`
- Infrastructure: `schema/civ/SPEC_INFRASTRUCTURE.md`
- Logistics: `schema/economy/SPEC_LOGISTICS.md`
- Time: `schema/time/README.md`

## See also
- `docs/arch/ECONOMY_AND_LOGISTICS.md`
