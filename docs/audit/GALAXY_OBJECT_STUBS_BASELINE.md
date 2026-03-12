# GAL-1 Galaxy Object Stubs Baseline

Status: Provisional
Series: GAL-1

## Object Kinds

- `kind.black_hole_stub`
  - Single central supermassive black-hole proxy anchored at the Milky Way galactic root origin.
- `kind.nebula_stub`
  - Sparse procedural nebula point-of-interest stub for future ASTRO-domain packs.
- `kind.supernova_remnant_stub`
  - Sparse procedural remnant stub for future hazard and lore packs.

## Placement Rules

- The central black-hole proxy is emitted exactly once from the galaxy-origin cell.
- Sparse non-central stubs are derived from:
  - GAL-0 stellar density proxy
  - GAL-0 metallicity proxy
  - galactocentric radius and height thresholds
  - named RNG stream `rng.worldgen.galaxy_objects`
- Generation is bounded:
  - `max_objects_per_cell = 1`
  - central black hole remains separate and origin-only
- Current deterministic sample window:
  - `cell.0.0.0` -> `kind.black_hole_stub`
  - `cell.400.0.0` -> `kind.supernova_remnant_stub`
  - `cell.800.0.0` -> no GAL-1 object rows
  - `cell.4200.0.0` -> no GAL-1 object rows

## Hazard Hooks

- GAL-1 keeps hazards object-local and static in MVP:
  - `hazard_strength_proxy`
  - `radiation_bump_permille`
  - `gravity_well_bump_permille`
- No dynamic gas clouds, supernova events, or runtime gravity solver are introduced.
- The current default layer/view path exposes object-local hazard hints only.

## Stability And Replacement

- All GAL-1 object-kind rows are tagged `provisional`.
- `future_series = ASTRO-DOMAIN`
- `replacement_target = dynamic lifecycle + gas dynamics`
- Replacement readiness:
  - future lifecycle simulation can replace sparse stubs without changing GAL-1 object identity or replay surfaces
  - future hazard systems can consume the existing object-local proxy hooks

## Locked Deterministic Outputs

- Combined replay hash:
  - `dd533adb0870f9cad9c9d87a303ab775d617be34f406c577b31a4421a25c0046`
- Artifact hash chain:
  - `0e091e122f4c3bff6df710b1a01613a38452534028e734c09abb8a759765b8e0`
- Layer payload hash:
  - `52d1b8c1f70bf4d48909d642995ce43fb5d269f9dfdb98fbc6abbee27b021a80`
- Hazard hook hash:
  - `0633bf2ccab4c680958a05a9340a8fbfc11ffce90f5e431139a59e02cec5a837`

## Readiness

GAL-1 is ready for:

- `META-STABILITY-1` tagging sweeps
- release-block gating that needs stable galaxy object replay fingerprints
- later ASTRO-domain lifecycle, hazard, and gas-dynamics overlays
