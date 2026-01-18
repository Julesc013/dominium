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
- No global physics combat or per-tick combat loops.
- No fabrication of forces, casualties, or outcomes.
- No UI access to authoritative conflict state.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_CONFLICT_CANON - Conflict Canon (CIV5-WAR0)

Status: draft
Version: 1

## Purpose
Define conflict as a deterministic, event-driven condition that integrates with
LIFE, CIV, governance, and scale systems without global simulation.

## Core definitions
CONFLICT:
- A state of opposing intents with coercive force.
- Exists when at least one side schedules hostile actions against another.
- Not a global flag; scoped to domains (city, region, orbit, route).

SECURITY FORCE:
- A cohort or machine-backed group capable of applying force.
- Defined by size/capacity, equipment, readiness, morale (bounded, deterministic),
  and logistics dependency.
- No autonomous AI implied.

ENGAGEMENT:
- A scheduled resolution event between opposing forces.
- Defined by participants, domain, start_act, and resolution_act.
- Resolution is deterministic and batch-safe.

CASUALTY:
- A LIFE2-compatible death or injury outcome.
- Casualties are outcomes of engagements or attrition events.
- No "HP ticks"; outcomes are event-based.

OCCUPATION:
- A condition where enforcement capacity of one authority applies within another's
  jurisdiction.
- Sustained by logistics and legitimacy.
- Degrades over time if unsupported.

RESISTANCE:
- Event-driven attrition against occupiers.
- Consumes legitimacy and logistics.
- Not random; threshold-driven.

## Conflict condition model
Conflict is a condition, not a mode. A conflict exists for a domain when hostile
actions are scheduled against another authority or force within that domain.
Conflict scope is bound to a domain and may exist at multiple scales concurrently.

## ConflictRecord schema
Required fields:
- conflict_id
- domain_id
- side_ids
- start_act
- status (active, suspended, resolved)
- next_due_tick (ACT)
- scheduled_event_ids (ordered by order_key)
- provenance_ref (command/action id)
- epistemic_scope_id (knowledge boundary)

Rules:
- Conflict existence is derived from scheduled hostile events; no global flag.
- next_due_tick is the earliest due among conflict events and participants.
- Conflicts are processed only when due; no global iteration.

## ConflictSide schema
Required fields:
- side_id
- authority_id
- force_ids
- objectives_ref (game-defined policy goals)
- logistics_dependency_id
- readiness_state (bounded, deterministic)
- next_due_tick (ACT)

Rules:
- Force membership and objectives are authoritative game rules.
- Side state changes must be event-driven.

## ConflictEvent envelope
Required fields:
- event_id
- conflict_id
- event_type (mobilization, deployment, engagement_resolution, attrition, demobilization)
- scheduled_act
- order_key (deterministic)
- participant_force_ids
- input_refs (logistics, forces, domains)
- output_refs (casualties, resource deltas, legitimacy deltas)
- provenance_ref
- epistemic_scope_id

Rules:
- Events are deterministic and batch-safe.
- Outputs must be applied through LIFE/CIV/governance pipelines only.

## Event-driven war model
Conflict is a set of scheduled events:
- Mobilization events
- Deployment/arrival events (logistics-driven)
- Engagement resolution events
- Attrition events (siege, blockade, occupation)
- Demobilization events

Rules:
- No per-tick combat updates.
- Each conflict participant exposes next_due_tick.
- Central macro scheduler processes only due conflict objects.

## Logistics and production integration
- Conflict consumes equipment (machines), supplies (food, fuel), and transport capacity.
- No supply causes readiness to degrade deterministically.
- Blockade/starvation are event-driven, not continuous per-tick drains.
- No teleportation of supplies; all deliveries are scheduled logistics arrivals.

## Governance and legitimacy integration
- Conflict affects legitimacy, enforcement capacity, and policy applicability.
- Illegitimate force degrades faster under sustained operations.
- Occupation without legitimacy produces resistance events.
- War exhaustion is modeled via scheduled legitimacy decay events.

## Epistemic constraints
- Actors may not know exact enemy strength, casualties, or hidden deployments.
- Knowledge propagates via sensors, reports, captured documents, and observation.
- UI must present uncertainty and delays; never authoritative conflict state.

## Non-fabrication and conservation
Explicitly forbidden:
- Spawning units without production.
- Killing people without the LIFE2 pipeline.
- Creating weapons without CIV1 machines.
- Resolving battles without consuming resources.

## Determinism and multiplayer parity
- Lockstep: war decisions and mobilizations are commands.
- Engagement outcomes are deterministic from shared state.
- Server-auth: server validates and schedules events; clients receive epistemic
  updates only.
- Batch vs step equivalence must hold for all conflict events.

## Refusal and failure modes
Required refusal codes:
- INSUFFICIENT_LOGISTICS
- INSUFFICIENT_AUTHORITY
- OUT_OF_DOMAIN
- CONFLICT_ALREADY_ACTIVE
- UNKNOWN_TARGET
- EPISTEMIC_INSUFFICIENT_INFO

Rules:
- Refusals are deterministic and logged with provenance.
- Refusals do not mutate state beyond audit records.

## Enforcement alignment (Phase 1)
Conflict systems must comply with ENF/DET/PERF/SCALE/DATA/REND/EPIS constraints
and their CI enforcement equivalents in `docs/CI_ENFORCEMENT_MATRIX.md`.

## Integration points
- LIFE pipelines: `schema/life/SPEC_LIFE_CONTINUITY.md`,
  `schema/life/SPEC_DEATH_AND_ESTATE.md`
- CIV1 logistics/production: `schema/civ/SPEC_LOGISTICS_FLOWS.md`,
  `schema/civ/SPEC_BUILDINGS_MACHINES.md`, `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- CIV2 legitimacy/enforcement: `schema/governance/SPEC_LEGITIMACY.md`,
  `schema/governance/SPEC_ENFORCEMENT.md`
- CIV3 knowledge/epistemics: `schema/knowledge/SPEC_SECRECY.md`,
  `schema/knowledge/SPEC_DIFFUSION.md`, `docs/SPEC_EPISTEMIC_INTERFACE.md`
- CIV4 scale/time warp: `schema/scale/SPEC_SCALE_DOMAINS.md`,
  `schema/scale/SPEC_SCALE_TIME_WARP.md`
- Scheduling: `docs/SPEC_EVENT_DRIVEN_STEPPING.md`, `docs/SPEC_SCHEDULING.md`

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
