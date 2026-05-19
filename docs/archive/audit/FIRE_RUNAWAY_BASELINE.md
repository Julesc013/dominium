Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# THERM-4 Fire/Runaway Baseline

## Scope
- Phase: `THERM-4` (fire ignition, combustion stubs, spread bounds, runaway cascade hooks).
- Tier target: deterministic THERM T1 integration with bounded spread and replay/proof surfaces.
- Non-goals kept:
  - no full chemistry kinetics
  - no mandatory FLUID/POLL dependency
  - no wall-clock dependence

## Ignition Model
- `model.therm_ignite_stub` is registered and dispatched in model engine.
- Ignition trigger is deterministic from:
  - temperature
  - ignition threshold
  - combustible/oxygen proxy flags
  - active-fire guard

## Combustion Stub
- `model.therm_combust_stub` is registered and dispatched in model engine.
- Outputs:
  - heat emission (`quantity.thermal.heat_loss_stub`)
  - pollutant emission stub (`derived.pollutant.emission_stub`)
  - deterministic fuel consumption (`derived.therm.fuel_consumed`)
  - hazard increment (`hazard.fire.basic`)

## Fire Lifecycle Processes
- Added deterministic runtime handlers:
  - `process.start_fire`
  - `process.fire_tick`
  - `process.end_fire`
- Added canonical state normalizers:
  - `thermal_fire_states` / `fire_state_rows`
  - `thermal_fire_events` / `fire_event_rows`

## Spread Bounds and Cascades
- Thermal T1 solve evaluates spread through graph adjacency in deterministic ordering.
- Spread bounds:
  - fixed spread cap per tick (`max_fire_spread_per_tick`)
  - fixed iteration cap (`fire_iteration_limit`)
- Cap-reached condition emits deterministic degrade decision log row.

## Safety Integration
- Fire tick path emits fail-safe safety hook (`safety.fail_safe_stop`) for active combustion.
- Thermal runaway remains safety-emittable and now has dedicated proof hash chain surface.

## Inspection / UX Surfaces
- Added inspection sections:
  - `section.thermal.fire_states`
  - `section.thermal.runaway_events`
- Section payloads are policy-gated and deterministic.

## Proof Bundle Integration
- Control proof bundle now includes:
  - `fire_state_hash_chain`
  - `ignition_event_hash_chain`
  - `fire_spread_hash_chain`
  - `runaway_event_hash_chain`

## Enforcement
- RepoX invariants:
  - `INV-FIRE-MODEL-ONLY`
  - `INV-NO-ADHOC-BURN-LOGIC`
- AuditX analyzers:
  - `InlineFireLogicSmell` (`E201_INLINE_FIRE_LOGIC_SMELL`)
  - `UnboundedSpreadSmell` (`E202_UNBOUNDED_SPREAD_SMELL`)

## Readiness
- THERM-4 baseline is ready for CHEM/POLL future integration by replacing combustion stubs with full constitutive models while preserving process-only mutation and deterministic proof surfaces.
