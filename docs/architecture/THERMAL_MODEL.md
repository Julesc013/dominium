# Thermal Model (THERMAL0)

Status: binding.  
Scope: event-driven heat accounting and failure.

## Core invariant
**Heat is energy that is no longer available for useful work.
It accumulates, diffuses slowly, and degrades systems unless
explicitly removed by processes.**

Heat is not:
- animation
- instant dissipation
- cosmetic only
- a hidden variable

## Relationship to energy
- Every energy loss declared in ENERGY0 produces heat unless explicitly redirected.
- Energy loss to heat accumulation is an explicit process step (no implicit dissipation).
- Heat stores are separate from energy stores and are not interchangeable.

## Primitives (authoritative)
Heat is represented via three data primitives:
- **Stores** (schema/heat.store.schema)  
  Capacity-bounded reservoirs of accumulated heat.
- **Flows** (schema/heat.flow.schema)  
  Directed transfers between heat stores with rate and efficiency constraints.
- **Thermal stress** (schema/thermal.stress.schema)  
  Safe ranges, efficiency modifiers, and damage rates for temperature exposure.

All numeric values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Heat state changes are **only** allowed via Process execution:
- `process.heat.accumulate`
- `process.heat.dissipate`
- `process.heat.transfer`

No per-tick global scans, continuous diffusion solvers, or implicit drains are permitted.

## Temperature and stress
- Operating temperature is derived from heat amount and capacity using a data-defined scale.
- Safe ranges define efficiency loss and damage thresholds.
- Stress evaluation is deterministic and event-driven.

## Cooling and dissipation
Cooling is modeled via assemblies and processes:
- radiators
- heat sinks
- coolant loops (symbolic; no fluid dynamics yet)
- insulation

Cooling effectiveness is environment- and damage-aware but never implicit.

## Failure semantics
Failure modes are explicit and explainable:
- overheat
- efficiency loss
- shutdown
- damage

If probabilistic failure is configured, RNG must use named streams:
`noise.stream.heat.flow.failure`.

## Collapse/expand compatibility
Collapse stores macro capsule stats:
- total heat per domain (invariant)
- temperature distributions (sufficient statistics)
- dissipation and transfer rates
- RNG cursor continuity for failure streams

Expand reconstructs a deterministic microstate consistent with capsule stats.

## Non-goals (THERMAL0)
- No continuous PDE solvers or per-tick diffusion
- No implicit dissipation or hidden heat sinks
- No fluid dynamics or combustion modeling yet

## See also
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
