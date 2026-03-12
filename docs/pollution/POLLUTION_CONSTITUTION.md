Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Pollution Constitution

Status: CANONICAL
Last Updated: 2026-03-05
Scope: POLL-0 constitutional contract for pollutant quantities, concentration fields, deterministic transport policy, and exposure accounting without CFD.

## 1) Purpose

POLL defines a deterministic externality substrate that bridges chemistry, environment, health stubs, and governance.

POLL models pollutants as conserved mass and/or concentration fields with explicit transform models for decay/deposition.

## 2) Pollutant Quantities

### Required Quantity

- `quantity.pollutant_mass`
  - canonical unit policy: `kg`
  - conservation applies unless explicit transform model executes

### Pollutant Type IDs (POLL-0 baseline)

- `pollutant.smoke_particulate`
- `pollutant.co2_stub`
- `pollutant.toxic_gas_stub`
- `pollutant.oil_spill_stub`

### Medium Semantics

Pollutants declare medium eligibility:
- airborne
- waterborne
- soilborne
- multi-medium where explicitly declared

## 3) Spatial Representation

Pollutant concentration proxies are represented as field layers:
- `field.pollution.<type>_concentration`

Transport channels:
- field update policies (P1 meso proxy)
- FLUID contaminant carrying pathways (stub in POLL-0, operationalized later)

No direct renderer/UI writes are allowed to pollutant field layers.

## 4) Dispersion, Decay, and Deposition

### Dispersion (P1)

- Deterministic meso proxy only (no atmospheric CFD).
- Policy-driven diffusion/advection stubs.
- FIELD wind modifiers may influence policy outputs.

### Decay and Deposition

- Decay/deposition are constitutive model transforms.
- Transforms must explicitly map pollutant mass to modeled sinks such as `deposited_mass` and `neutralized_mass`.
- Every transform execution must be logged as deterministic process output.

No silent pollutant creation or disappearance is permitted.

## 5) Exposure Contract

- Subjects and/or zones accumulate deterministic exposure from local concentration samples.
- Exposure state is per-subject/per-pollutant with tick-stamped updates.
- POLL-0 hazard output is limited to `hazard.health_risk_stub` hooks (no full medical subsystem coupling yet).

## 6) Tier Contract

- `P0` bookkeeping only:
  - canonical source totals by pollutant and region
  - no concentration field simulation required
- `P1` coarse dispersion + exposure:
  - deterministic field update policies
  - deterministic exposure accumulation
- `P2` reserved:
  - optional ROI micro detail in future work

POLL-0 runtime support target: `P0` operational, `P1` policy declarations prepared.

## 7) Coupling Discipline

Pollution source creation must originate through process-layer couplings only:
- `CHEM -> POLL` via reaction/process emission events
- `THERM -> POLL` via fire/combustion emission events
- `FLUID -> POLL` via contaminant carry/leak events (stub in POLL-0)
- `FIELD -> POLL` modifiers (e.g., wind) through declared policy/model bindings only

Visibility coupling rule:
- `POLL -> FIELD.visibility` is permitted only through constitutive model outputs and process-managed effect application.
- Direct ad-hoc visibility writes derived from non-POLL smoke shortcuts are non-canonical and must migrate.

## 8) Proof and Explainability

Every material pollution change must be explainable with deterministic provenance:
- source chain (`pollution_source_event` lineage)
- transport/field policy ID applied
- decay/deposition policy/model ID applied
- exposure threshold derivation inputs

Required explain surfaces:
- `explain.pollution_spike`
- `explain.exposure_threshold`

## 9) Determinism and Budgeting

- Named deterministic ordering and reduction rules are mandatory for aggregation.
- Authoritative outcomes must be replay-equivalent under thread-count variation.
- Policy/model execution must obey budget/degrade discipline and emit explicit degradation markers when capped.

## 10) Optionality and Null-Boot

- POLL is pack-driven and optional.
- Runtime must boot deterministically with no pollutant packs.
- `poll.policy.none` must remain valid as explicit refusal/degradation path.

## 11) Non-Goals (POLL-0)

- No atmospheric CFD.
- No full meteorology solver.
- No wall-clock dependent behavior.
- No direct state mutation outside deterministic process execution.
