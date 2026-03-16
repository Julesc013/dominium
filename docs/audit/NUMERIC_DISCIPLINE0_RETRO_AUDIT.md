Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Numeric discipline baseline and release-pinned engine policy docs.

# NUMERIC-DISCIPLINE-0 Retro Audit

## Scope

- Audit existing float and fixed-point usage before freezing numeric policy.
- Classify reviewed approximation bridges separately from canonical truth numeric.
- Confirm SOL-1 and SOL-2 already avoid floating-point trig in their canonical outputs.

## Current Numeric Surfaces

### Truth-path numeric

- `src/meta/numeric.py`
- `src/time/time_mapping_engine.py`
- `src/physics/momentum_engine.py`
- `src/physics/energy/energy_ledger_engine.py`
- `src/mobility/micro/free_motion_solver.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/astro/ephemeris/kepler_proxy_engine.py`

### Reviewed deterministic float bridges

- `src/geo/kernel/geo_kernel.py`
  Reason: projection/query bridge with deterministic quantization.
- `src/geo/metric/metric_engine.py`
  Reason: spherical/geodesic approximation bridge with bounded deterministic rounding.
- `src/process/qc/qc_engine.py`
  Reason: QC/reporting rate derivation quantizes back to integer values.
- `src/mobility/micro/constrained_motion_solver.py`
  Reason: heading derivation bridge emits integer milli-degree results only.
- `src/mobility/geometry/geometry_engine.py`
  Reason: grid snapping bridge quantizes back to integer coordinates.
- `src/meta/instrumentation/instrumentation_engine.py`
  Reason: measurement quantization bridge snaps back to deterministic integer quanta.

### Render-only numeric

- `src/client/render/renderers/software_renderer.py`
- `src/platform/platform_window.py`
- `src/platform/platform_input_routing.py`

### Tooling-only numeric

- Audit/report helpers and deterministic bundle/report generators under `tools/`
- UI/help/report formatting surfaces that do not feed canonical hashes

## Findings

- SOL-1 illumination geometry already uses fixed-point lookup tables and integer reduction; no float trig path was found in `illumination_geometry_engine.py`.
- SOL-2 ephemeris/orbit sampling already reuses SOL-1 fixed-point trig and integer arithmetic; no float orbit solver path was found in `kepler_proxy_engine.py`.
- Existing float usage concentrates in reviewed approximation bridges and canonicalizer helpers rather than persisted canonical state payloads.
- No unsafe float compiler flags were found in the scanned build configuration surfaces.

## Freeze Implications

- Numeric governance should formalize the reviewed bridge list rather than silently allowing ad hoc float use.
- Canonical serialization needs an explicit scan/report surface even when current findings are zero.
- Engine-level tolerances should be versioned separately from quantity tolerances so cross-domain approximation bounds are visible and testable.
