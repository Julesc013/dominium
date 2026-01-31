# Fluids and Containment Baseline (FLUIDS0)

Status: binding for T13 baseline.  
Scope: event-driven fluids and gases stored in containment or terrain voids.

## What fluids are in T13
- Conserved volumes stored in explicit containers or voids.
- Movement resolved by scheduled processes (no per-tick solvers).
- Pressure limits and rupture thresholds are explicit and inspectable.

All values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What exists
**Stores**
- Volume, capacity, temperature, and contamination tracked per containment.

**Flows**
- Directed, rate-limited transfers with efficiency and latency.
- Failure modes are explicit and deterministic.

**Pressure & rupture**
- Pressure derived from fill ratio and explicit limits.
- Rupture causes deterministic leakage events.

**Resolution**
- Event-driven and interest-bounded.
- Deterministic ordering and math.
- No per-tick global scans.

## What is NOT included yet
- No turbulence, surface waves, or vortex effects.
- No erosion, sediment transport, or fluid-driven terrain change.
- No continuous diffusion or gas mixing solvers.
- No combustion or hazard propagation (later layer).

## Collapse/expand compatibility
Fluid collapse stores:
- total fluid volume per domain (invariant)
- pressure distributions
- contamination distributions

Expand reconstructs consistent microstate deterministically.

## Inspection and tooling
Inspection exposes:
- fluid volume and capacity
- pressure and rupture risk
- containment integrity and leak points
- provider provenance

Visualization is symbolic and never authoritative.

## Maturity labels
- Stores: **BOUNDED** (capacity-limited, auditable).
- Flows: **BOUNDED** (event-driven, deterministic).
- Pressure: **BOUNDED** (threshold-based, explicit).

## See also
- `docs/architecture/FLUIDS_MODEL.md`
- `docs/architecture/THERMAL_MODEL.md`
- `docs/architecture/ENERGY_MODEL.md`
