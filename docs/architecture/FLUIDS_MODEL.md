# Fluids Model (FLUIDS0)

Status: binding.  
Scope: containment, flow, and pressure for fluids and gases.

## Core invariant
**Fluids and gases are conserved volumes stored in containment or terrain voids,
whose movement resolves in response to gradients via explicit processes.**

Fluids and gases are not:
- particles
- per-tick flows
- cosmetic effects
- free-floating without containment

## Primitives (authoritative)
Fluid and gas state is represented via four data primitives:
- **Stores** (`schema/fluid.store.schema`)  
  Capacity-bounded containment for volumes, temperature, and contamination.
- **Flows** (`schema/fluid.flow.schema`)  
  Directed transfers between stores with rate/efficiency constraints.
- **Pressure** (`schema/fluid.pressure.schema`)  
  Limits and rupture thresholds tied to containment.
- **Properties** (`schema/fluid.properties.schema`)  
  Static tags and scalars for density/viscosity/compressibility.

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Fluid state changes are **only** allowed via Process execution:
- `process.fluid.resolve_flow`
- `process.fluid.transfer`
- `process.fluid.equalize_pressure`
- `process.fluid.leak`

No background ticks, per-cell solvers, or implicit redistribution are permitted.
All effects must be auditable, deterministic, and replayable.

## Containment interfaces
Containment is modeled as assemblies and voids:
- tanks, pipes, valves, seals, walls
- terrain voids (caves, tunnels, cavities)

No fluid may exist without a containment context.

## Resolution & determinism
Resolution is:
- event-driven (topology/pressure changes or breaches)
- interest/budget bounded
- deterministic (stable ordering, fixed-point math)

If probabilistic failure is configured, RNG must use named streams of the form:  
`noise.stream.fluid.flow.failure`

RNG derivation follows `docs/architecture/RNG_MODEL.md`.

## Pressure & rupture
Pressure is derived from containment fill ratios and explicit limits.
Rupture thresholds trigger deterministic release and leakage events; no hidden
physics or solvers are implied.

## Flooding & drainage
Flooding and drainage are resolved locally via processes:
- flooding fills terrain voids (phi-defined)
- drainage follows pressure/gradient rules, not per-tick solvers
- travel cost and hazards may be modified by overlays

## Heat & energy interaction
- Fluid temperature is derived from T12 heat stores when connected.
- Pumping and pressurizing may declare energy usage (symbolic in FLUIDS0).
- Heat transfer occurs through explicit processes only.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- total fluid volume per domain (invariant)
- pressure distributions and contamination distributions (sufficient statistics)
- RNG cursor continuity for configured failure streams

Expand reconstructs a deterministic microstate consistent with capsule stats.

## Law & refusal semantics
Fluid processes must obey law/meta-law. Refusals must clearly state:
- insufficient capacity
- forbidden connection
- safety/pressure violations

Refusal semantics are governed by `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (FLUIDS0)
- No Navier–Stokes or PDE solvers.
- No particle simulation or global voxel grids.
- No erosion or sediment transport.
- No implicit heat dissipation.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
