# Hazards Model (HAZARD0)

Status: binding.  
Scope: hazard emission, propagation, exposure, and safety systems.

## Core invariant
**Hazards are field-based representations of danger caused by uncontrolled
energy, matter, or information, propagating through space and time via processes.**

Hazards are not:
- scripted events
- combat-only mechanics
- instantaneous global effects
- hidden debuffs

## Primitives (authoritative)
Hazard state is represented via three data primitives:
- **Hazard types** (`schema/hazard.type.schema`)  
  Declarative definitions of hazard classes and default rates.
- **Hazard fields** (`schema/hazard.field.schema`)  
  Active hazard emitters with intensity, exposure, and decay parameters.
- **Hazard exposures** (`schema/hazard.exposure.schema`)  
  Accumulated exposure records and limits for agents, structures, or regions.

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Hazard state changes are **only** allowed via Process execution:
- `process.hazard.emit`
- `process.hazard.spread`
- `process.hazard.decay`
- `process.hazard.neutralize`

No per-tick global solvers or implicit background propagation are permitted. All
effects must be deterministic, replayable, and auditable.

## Propagation & determinism
Propagation is:
- local and region-based
- interest/budget bounded
- deterministic (stable ordering, fixed-point math)

If probabilistic spread or failure is configured, RNG must use named streams of
the form:
`noise.stream.hazard.<hazard_type>.spread`

RNG derivation follows `docs/architecture/RNG_MODEL.md`.

## Containment failure integration
Hazards emerge from containment failures:
- seals, walls, tanks, pipes, reactors (fluids/energy)
- thermal overloads (heat)
- structural ruptures (structures/terrain)
- data vault breaches (information hazards)

Containment failure emits hazard fields via explicit processes only.

## Safety systems
Safety is first-class and process-driven:
- alarms and sensors
- containment upgrades
- emergency shutdowns
- evacuation routing (via travel fields)

Safety systems are assemblies and must obey law/meta-law.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- total hazard energy per domain (invariant)
- hazard type distributions and exposure histograms (sufficient statistics)
- RNG cursor continuity for configured spread streams

Expand reconstructs a deterministic microstate consistent with capsule stats.

## Law & refusal semantics
Hazard processes must obey law/meta-law. Refusals must clearly state:
- safety violations
- forbidden containment changes
- insufficient mitigation or budget

Refusal semantics are governed by `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (HAZARD0)
- No scripted disasters.
- No continuous diffusion or per-tick solvers.
- No combat mechanics or damage models beyond exposure accounting.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/FLOAT_POLICY.md`
