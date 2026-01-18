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
- No fleet physics or global combat simulation.
- No per-tick travel combat loops.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_INTERPLANETARY_WAR - Multi-Scale and Interplanetary Conflict (CIV5-WAR0)

Status: draft
Version: 1

## Purpose
Define conflict behavior across scales and interplanetary domains without
physics-based global simulation.

## Multi-scale domain rules
LOCAL (meters-km):
- Tactical resolution only if interest + fidelity justify.
- Otherwise collapsed to analytical outcome.

PLANETARY:
- Control of regions/cities.
- Logistics and population effects dominate.

ORBITAL:
- Control of orbits/stations.
- Blockade effects via logistics.

INTERSTELLAR:
- Route interdiction.
- Arrival denial.
- No fleet physics.

GALACTIC:
- Strategic only; no micro resolution.

## InterplanetaryConflictLink schema
Required fields:
- link_id
- origin_domain_id
- destination_domain_id
- route_id
- departure_act
- arrival_act
- interdiction_window (act range)
- blockading_force_ids
- blockade_policy_id
- next_due_tick (ACT)
- provenance_ref

Rules:
- Travel and arrival are scheduled events; no continuous simulation.
- Interdiction and arrival denial are resolved at scheduled acts only.
- Blockade effects are applied via logistics events, not per-tick drains.

## Time warp compatibility
- Conflict schedules use ACT and must remain deterministic under time warp.
- Warp limits are enforced by scale domain rules; no local overrides.
- Cross-scale arrivals use fixed scheduling and deterministic ordering.

## Epistemic constraints
- Route interdiction and blockade visibility is sensor- and report-driven.
- UI must not expose authoritative arrivals or hidden deployments.

## Integration points
- Scale domains and time warp: `schema/scale/SPEC_SCALE_DOMAINS.md`,
  `schema/scale/SPEC_SCALE_TIME_WARP.md`
- Interplanetary logistics: `schema/scale/SPEC_INTERPLANETARY_LOGISTICS.md`,
  `schema/scale/SPEC_INTERSTELLAR_LOGISTICS.md`
- Logistics/production: `schema/civ/SPEC_LOGISTICS_FLOWS.md`,
  `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- Epistemic gating: `docs/SPEC_EPISTEMIC_INTERFACE.md`

## Prohibitions
- No real-time physics combat globally.
- No per-entity combat ticks.
- No random outcomes.
- No UI-driven resolution.
- No instant war state changes.

## Test plan (spec-level)
Required scenarios:
- Deterministic engagement resolution.
- Batch vs step equivalence.
- Logistics starvation effects.
- Occupation legitimacy decay.
- Epistemic uncertainty correctness.
- No global iteration with many conflicts.
