Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Conflict and War Model (WAR0)

Status: binding.  
Scope: conflict records, engagements, and destruction as deterministic, event-driven processes.

## Core invariant
Conflict is the deliberate application of **destructive processes** under contested authority.  
There is no combat minigame, no per-tick battle loop, and no special combat physics.

## Determinism and process-only mutation
- Conflict state changes occur only via **Processes**.
- No per-tick combat simulation or global scanning.
- Ordering is deterministic per `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`.
- Authoritative logic uses fixed-point only (see `docs/architecture/FLOAT_POLICY.md`).

## Conflict records and events
Conflict is a **condition**, not a mode:
- Conflicts exist when hostile events are scheduled in a domain.
- Events are scheduled by processes and resolved only when due.
- Outputs are applied via existing systems (LIFE, logistics, legitimacy).

Schemas:
- `schema/conflict.record.schema`
- `schema/conflict.side.schema`
- `schema/conflict.event.schema`

## Security forces and engagements
Forces are **records**, not autonomous AI:
- Readiness and morale are bounded, deterministic values.
- Engagements resolve at scheduled acts; batch vs step equivalence must hold.

Schemas:
- `schema/security_force.schema`
- `schema/engagement.schema`
- `schema/engagement.outcome.schema`

## Occupation, resistance, and morale
Occupation is sustained by legitimacy and logistics; resistance is event-driven:
- No per-tick occupation decay or resistance loops.
- Morale is field-based and decays only via processes.

Schemas:
- `schema/occupation.condition.schema`
- `schema/resistance.event.schema`
- `schema/morale.field.schema`

## Weapons as assemblies
Weapons are assemblies that enable destructive processes:
- No damage numbers; effectiveness emerges from materials and energy.

Schema:
- `schema/weapon.spec.schema`

## Collapse/expand compatibility
Macro capsules store coarse conflict statistics:
- conflict/side/force counts
- morale/readiness distributions
- resistance/occupation summaries
- RNG cursor continuity (if used)

Expanded domains reconstruct conflict state deterministically.

## Save/load/replay
- Conflicts are saved as records and events, not meshes or transient state.
- Replays reproduce scheduling and outcomes deterministically.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/UNIT_SYSTEM_POLICY.md`