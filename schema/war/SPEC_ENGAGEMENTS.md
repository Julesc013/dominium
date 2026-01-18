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
- No per-tick combat loops.
- No stochastic engagement outcomes.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_ENGAGEMENTS - Engagement Events (CIV5-WAR0)

Status: draft
Version: 1

## Purpose
Define deterministic, event-driven engagement resolution between opposing
security forces across conflict domains.

## Engagement schema
Required fields:
- engagement_id
- conflict_id
- domain_id
- participant_force_ids
- start_act
- resolution_act
- resolution_policy_id (game-defined)
- order_key (deterministic)
- logistics_inputs (equipment, supplies, transport refs)
- legitimacy_scope_id
- epistemic_scope_id
- provenance_ref

Rules:
- Engagements are scheduled events; no per-tick updates.
- Resolution uses shared authoritative state and deterministic rules.
- Batch vs step equivalence must hold.

## EngagementOutcome schema
Required fields:
- outcome_id
- engagement_id
- casualty_refs (LIFE2 outcomes)
- resource_deltas (CIV1 inventories and flows)
- legitimacy_deltas (CIV2 legitimacy updates)
- control_deltas (jurisdiction or domain control changes)
- epistemic_reports (sensor/report outputs)
- provenance_ref

Rules:
- Casualties must be emitted via LIFE2 pipelines only.
- Resource changes must be applied via CIV1 logistics/production systems.
- Outcomes must be deterministic and stable under replays.

## Scheduling and ordering
- order_key provides deterministic ordering under simultaneous resolutions.
- Engagements are processed only when resolution_act is due.
- No global iteration; scheduler processes due engagements only.

## Epistemic constraints
- Outcome visibility is filtered by epistemic scopes and sensors.
- UI receives delayed or partial reports, not authoritative outcomes.

## Integration points
- LIFE pipelines: `schema/life/SPEC_DEATH_AND_ESTATE.md`
- CIV1 logistics/production: `schema/civ/SPEC_LOGISTICS_FLOWS.md`,
  `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- CIV2 legitimacy: `schema/governance/SPEC_LEGITIMACY.md`
- Knowledge gating: `schema/knowledge/SPEC_SECRECY.md`,
  `docs/SPEC_EPISTEMIC_INTERFACE.md`
- Event scheduling: `docs/SPEC_EVENT_DRIVEN_STEPPING.md`

## Prohibitions
- No real-time physics combat globally.
- No per-entity combat ticks.
- No random outcomes.
- No UI-driven resolution.

## Test plan (spec-level)
Required scenarios:
- Deterministic engagement resolution.
- Batch vs step equivalence.
- Logistics starvation effects.
- Occupation legitimacy decay.
- Epistemic uncertainty correctness.
- No global iteration with many conflicts.
