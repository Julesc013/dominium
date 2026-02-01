Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Energy Model (ENERGY0)

Status: binding.  
Scope: universal energy accounting across all authoritative processes.

## Core invariant
**Energy is a conserved scalar quantity that is stored in fields, transferred by
processes, dissipated as heat, and never appears or disappears without an explicit
process.**

Energy is not:
- electrons or voltage
- animation or VFX
- a magic resource

## Primitives (authoritative)
Energy is represented via three data primitives:
- **Stores** (`schema/energy.store.schema`)  
  Capacity-bounded reservoirs with optional leakage.
- **Flows** (`schema/energy.flow.schema`)  
  Directed transfers between stores with rate and efficiency constraints.
- **Loss profiles** (`schema/energy.loss.schema`)  
  Explicit dissipation (defaults to heat).

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Energy state changes are **only** allowed via Process execution:
- `process.energy.generate`
- `process.energy.transfer`
- `process.energy.consume`
- `process.energy.store`
- `process.energy.release`

No background ticks, global solvers, or implicit drains are permitted. All
energy effects must be auditable, deterministic, and replayable.

## Declaring energy usage
Processes may declare energy needs and outputs in their extension bags. The
canonical shape is:

- `extensions.energy.inputs[]` (store_id, amount, unit)
- `extensions.energy.outputs[]` (store_id, amount, unit)
- `extensions.energy.losses[]` (loss_id, fraction)

This is a declaration only; execution is still process-ordered and subject to
law/meta-law and budget admission.

## Networks & resolution
Energy networks are assemblies (wires, pipes, shafts, grids). Resolution is:
- event-driven (topology or load changes)
- interest/budget bounded
- deterministic (stable ordering, fixed-point math)

No continuous circuit equations or per-tick global solvers are allowed.

### Failure semantics
Failure modes are explicit and explainable:
- overload
- brownout
- blackout
- cascading failure
- leakage

If probabilistic failure is configured, RNG must use **named streams** of the form:  
`noise.stream.energy.flow.failure`

RNG derivation follows `docs/architecture/RNG_MODEL.md` with domain/process/tick
mixing; no wall-clock inputs are permitted.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- total stored energy per domain (invariant)
- generation/consumption/loss distributions (sufficient statistics)
- RNG cursor continuity for failure streams

Expand reconstructs a deterministic microstate consistent with capsule stats.

## Law & refusal semantics
Energy processes must obey law/meta-law. Refusals must clearly state:
- insufficient energy
- forbidden connection
- safety/code violations

Refusal semantics are governed by `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (ENERGY0)
- No thermal simulation (comes in T12).
- No fluid dynamics or per-tick solvers.
- No economy, pricing, or resource abstraction.

## See also
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`