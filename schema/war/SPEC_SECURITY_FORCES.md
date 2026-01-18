--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- primitives only (IDs, scheduling, ledger hooks)
GAME:
- conflict rules, policies, resolution
SCHEMA:
- formats, versions, migrations
TOOLS:
- future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No autonomous AI or hidden behavior in force records.
- No fabrication of force capacity or equipment.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_SECURITY_FORCES - Security Forces (CIV5-WAR0)

Status: draft
Version: 1

## Purpose
Define deterministic security force records used by conflict scheduling and
engagement resolution without implying autonomous AI.

## SecurityForce schema
Required fields:
- force_id
- authority_id
- force_type (cohort, machine, mixed)
- capacity (integer, deterministic)
- equipment_refs (machine ids from CIV1 production)
- readiness (fixed-point, 0..1)
- morale (fixed-point, 0..1)
- logistics_dependency_id
- home_domain_id
- next_due_tick (ACT)
- provenance_ref (mobilization or production source)

Rules:
- Readiness and morale are bounded and deterministic.
- Updates are scheduled events only; no per-tick drift.
- Capacity and equipment must be backed by CIV1 production and inventory.
- Force creation and dissolution require explicit game rules and provenance.

## Readiness and morale constraints
- No supply or transport capacity causes readiness decay via scheduled events.
- Illegitimate or unsupported force assignments increase morale decay rates.
- Recovery requires explicit resupply and rest events.

## Epistemic constraints
- Other actors do not see exact capacity or readiness.
- Observations are emitted via sensors/reports and may be delayed or partial.
- UI must reflect uncertainty; no authoritative force details in UI.

## Integration points
- CIV1 logistics/production: `schema/civ/SPEC_LOGISTICS_FLOWS.md`,
  `schema/civ/SPEC_BUILDINGS_MACHINES.md`, `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- CIV2 enforcement/legitimacy: `schema/governance/SPEC_ENFORCEMENT.md`,
  `schema/governance/SPEC_LEGITIMACY.md`
- LIFE pipelines for casualties: `schema/life/SPEC_DEATH_AND_ESTATE.md`
- Knowledge gating: `schema/knowledge/SPEC_SECRECY.md`,
  `docs/SPEC_EPISTEMIC_INTERFACE.md`

## Implementation notes (CIV5-WAR1)
- Canonical game implementation lives under `game/rules/war/` with public headers
  in `game/include/dominium/rules/war/`.
- Mobilization/demobilization pipelines enforce population, equipment, legitimacy,
  and authority checks and produce provenance-backed records.
- Readiness and morale updates are scheduled through due-event schedulers only.
- Refusal codes are defined in `dominium/rules/war/security_force.h`.
- WAR1 projections map `authority_id` to owning org/jurisdiction and
  `home_domain_id` to the current domain scope reference.

## Prohibitions
- No autonomous AI implied by force definitions.
- No random capacity or morale adjustments.
- No spawning equipment without production.

## Test plan (spec-level)
Required scenarios:
- Deterministic engagement resolution.
- Batch vs step equivalence.
- Logistics starvation effects.
- Occupation legitimacy decay.
- Epistemic uncertainty correctness.
- No global iteration with many conflicts.
