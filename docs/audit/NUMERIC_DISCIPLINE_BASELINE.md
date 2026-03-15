Status: DERIVED
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Release-pinned engine numeric policy and compiler matrix documentation.

# Numeric Discipline Baseline

- result: `complete`
- release_status: `pass`
- tolerance_registry_hash: `c0d280ec42ce51888ca444a2c4b901ee0cbd67ebb892b70606dfde0194407c3b`
- numeric_scan_fingerprint: `6e00945230c147255b776e545fd34a1a45d57f0ed846511faa06327c006d82e1`
- deterministic_fingerprint: `b89abe42362fadbb0d163ae03d8a9407c9aabc57d738f91ab6c0aefa834388ab`

## Numeric Domains

### Truth-path numeric
- `src/meta/numeric.py`
- `src/time/time_mapping_engine.py`
- `src/physics/momentum_engine.py`
- `src/physics/energy/energy_ledger_engine.py`
- `src/mobility/micro/free_motion_solver.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/astro/ephemeris/kepler_proxy_engine.py`

### Reviewed numeric bridges
- `src/geo/kernel/geo_kernel.py`: projection/query bridge with deterministic quantization
- `src/geo/metric/metric_engine.py`: bounded geodesic approximation bridge
- `src/meta/instrumentation/instrumentation_engine.py`: measurement quantization bridge
- `src/mobility/geometry/geometry_engine.py`: grid snap bridge with integer output
- `src/mobility/micro/constrained_motion_solver.py`: heading derivation bridge with integer output
- `src/process/qc/qc_engine.py`: qc/reporting quantization bridge

### Render-only numeric
- `src/client/render/renderers/software_renderer.py`
- `src/platform/platform_input_routing.py`
- `src/platform/platform_window.py`

### Tooling-only numeric
- `tools/audit/`
- `tools/dist/`
- `tools/release/`

## Tolerances

- `tol.geo_projection`
- `tol.illumination_fixed`
- `tol.orbit_sampling`
- `tol.render_interp`

## Enforcement Coverage

- ARCH-AUDIT numeric checks: `float_in_truth_scan`, `noncanonical_serialization_scan`, `compiler_flag_scan`
- RepoX numeric rules: `INV-FLOAT-ONLY-IN-RENDER`, `INV-CANONICAL-NUMERIC-SERIALIZATION`, `INV-SAFE-FLOAT-COMPILER-FLAGS`
- AuditX numeric analyzers: `E525`, `E526`, `E527`
- TestX numeric coverage: fixed-point ops, trig lookup, hash stability, truth-namespace float scan

## Readiness

- CONCURRENCY-CONTRACT-0: `ready`
