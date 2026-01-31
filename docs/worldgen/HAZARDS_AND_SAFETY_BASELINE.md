# Hazards and Safety Baseline (HAZARD0)

Status: binding for T15 baseline.  
Scope: event-driven hazard emission, propagation, and exposure.

## What hazards are in T15
- Hazards are field-defined danger states with explicit intensity, exposure, and decay.
- Propagation is local, event-driven, and deterministic.
- Exposure is tracked explicitly and never implied by visuals.

All hazard values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What exists
**Hazard types**
- Data-defined classes (fire, toxic, radiation, pressure, thermal, biological, information).
- Default rates for intensity, exposure, and decay.

**Hazard fields**
- Active hazard emitters with provenance and uncertainty.
- Region-based falloff; no per-tick global diffusion.

**Exposure tracking**
- Accumulated exposure per hazard type.
- Explicit exposure limits and uncertainty.

**Resolution**
- Event-driven and interest-bounded.
- Deterministic ordering and fixed-point math.
- No global scans or hidden mutation.

**Safety systems**
- Alarms, sensors, containment upgrades, and emergency shutdowns are modeled
  as assemblies and processes.

## What is NOT included yet
- No scripted disasters or combat hazards.
- No continuous diffusion/PDE solvers.
- No biological injury or long-term health systems (later layers).

## Collapse/expand compatibility
Hazard collapse stores:
- total hazard energy per domain (invariant)
- hazard type distributions
- exposure histograms

Expand reconstructs consistent microstate deterministically.

## Inspection and tooling
Inspection exposes:
- hazard type and intensity
- exposure rate and decay
- uncertainty and provenance
- active containment failure sources

Visualization is symbolic and never authoritative.

## Maturity labels
- Hazard types: **BOUNDED** (data-defined, stable ids).
- Hazard fields: **BOUNDED** (process-driven, auditable).
- Exposure tracking: **BOUNDED** (explicit accumulation).

## See also
- `docs/architecture/HAZARDS_MODEL.md`
- `docs/architecture/FLUIDS_MODEL.md`
- `docs/architecture/THERMAL_MODEL.md`
- `docs/architecture/INFORMATION_MODEL.md`
