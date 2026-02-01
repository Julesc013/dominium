Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Heat and Failure Baseline (HEAT0)

Status: binding for T12 baseline.  
Scope: event-driven heat accumulation and failure constraints.

## What heat is in T12
- Heat is the conserved consequence of energy losses.
- Heat is stored in explicit stores and moved by explicit flows.
- Thermal stress links temperature exposure to efficiency loss and damage.

All heat values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What exists
**Stores**
- Capacity-bounded heat reservoirs with ambient exchange rates.

**Flows**
- Directed, rate-limited transfers between heat stores.
- Efficiency and latency are data-defined.

**Stress and failure**
- Safe ranges define efficiency loss and damage rates.
- Overheating and undercooling are explicit flags, not implicit effects.

**Resolution**
- Event-driven and interest-bounded.
- Deterministic (stable ordering, fixed-point math).
- No per-tick global scans.

## What is NOT included yet
- No continuous diffusion or PDE solvers.
- No fluid dynamics, combustion, or fire propagation.
- No implicit heat sinks or background cooling.

## Collapse/expand compatibility
Heat collapse stores:
- total heat per domain (invariant)
- temperature distributions (sufficient statistics)
- dissipation/transfer rates

Expand reconstructs consistent microstate deterministically.

## Inspection and tooling
Inspection exposes:
- temperature at cursor
- heat sources and sinks
- efficiency loss and failure risk
- provider provenance

Visualization is symbolic and never authoritative.

## Maturity labels
- Stores: **BOUNDED** (explicit, capacity-limited).
- Flows: **BOUNDED** (event-driven, deterministic).
- Stress: **BOUNDED** (threshold-based, auditable).

## See also
- `docs/architecture/THERMAL_MODEL.md`
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`