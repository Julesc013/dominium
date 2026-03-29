Status: DERIVED
Last Reviewed: 2026-03-30
Stability: provisional
Future Series: XI-5
Replacement Target: Xi-6 freeze inputs after residual convergence

# XI-5X2 Content Source Policy Report

## Result

- retained content-source rows: `13`
- retained root: `packs/source`

## Rationale

- `docs/architecture/deterministic_packaging.md` excludes `packs/source/*` from default dist output unless a bundle explicitly selects it.
- `docs/worldgen/REAL_DATA_IMPORT_PIPELINE.md` states that runtime reads derived packs only while source packs are upstream import inputs.
- import tools and determinism tests still consume `packs/source` directly for reproducible raw-data ingestion.
