Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Energy Baseline (ENERGY0)

Status: binding for T11 baseline.  
Scope: deterministic, event-driven energy accounting.

## What energy is in T11
- Energy is a **conserved scalar** stored in explicit stores.
- Transfers occur via explicit flows resolved by processes.
- Losses are explicit dissipation (default destination: heat).

All energy values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What exists
**Stores**
- Capacity-bounded, typed reservoirs.
- Optional leakage (ratio per ACT tick).

**Flows**
- Directed, rate-limited transfers.
- Efficiency and latency are data-defined.
- Failure modes are explicit (overload, brownout, blackout, cascade, leakage).

**Resolution**
- Event-driven and interest-bounded.
- Deterministic (stable ordering, no floats).
- No per-tick global scans.

## What is NOT included yet
- No heat/thermal dynamics (T12).
- No continuous circuit equations or solvers.
- No fuel chemistry or detailed electromechanics.
- No economy, pricing, or logistics.

## Collapse/expand compatibility
Energy collapse stores:
- total stored energy per domain (invariant)
- coarse generation/consumption/loss distributions
- RNG cursor continuity for failure streams

Expand reconstructs consistent microstate deterministically.

## Inspection & tooling
Inspection exposes:
- store amounts/capacities
- flow rates and efficiencies
- loss totals
- failure history flags

Visualization is symbolic (arrows, gauges) and never authoritative.

## Maturity labels
- Stores: **BOUNDED** (explicit, capacity-limited).
- Flows: **BOUNDED** (event-driven, deterministic).
- Networks: **BOUNDED** (symbolic resolution only).

## See also
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/SCALING_MODEL.md`