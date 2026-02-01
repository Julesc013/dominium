Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Conflict Baseline (WAR0)

Status: binding for T21 baseline.  
Scope: conflict records, engagements, and destruction as deterministic, event-driven processes.

## What exists in T21
- Conflict is represented as **scheduled events** tied to domains.
- Security forces are **records** with readiness and morale.
- Engagements resolve at **scheduled acts** with deterministic ordering.
- Occupation and resistance are **event-driven**, not per-tick.
- Weapons are **assemblies** that enable destructive processes.

## Destructive processes
Conflict uses the same process framework as other systems:
- sabotage, attack, siege, occupation, suppression, resistance
- consume energy (T11), generate heat (T12), and can create hazards (T15)
- modify terrain/structures via existing processes (T7/T9)

## Morale and legitimacy
Morale and legitimacy constrain outcomes:
- morale is a field with decay via scheduled processes
- low legitimacy reduces enforcement effectiveness
- resistance events trigger from legitimacy/logistics thresholds

All numeric values are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What is NOT included yet
- No combat minigame or hitpoint system.
- No per-tick battle simulation or particle physics.
- No scripted war outcomes or omniscient battle state.

## Collapse/expand compatibility
Collapsed domains store:
- conflict/side/force counts
- morale/readiness distributions
- resistance/occupation summaries

Expanded domains reconstruct conflict state deterministically and locally.

## Maturity labels
- Conflict records and events: **BOUNDED**
- Security forces and engagements: **BOUNDED**
- Occupation/resistance: **BOUNDED**
- Weapons as assemblies: **PARAMETRIC**

## See also
- `docs/architecture/CONFLICT_AND_WAR_MODEL.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`