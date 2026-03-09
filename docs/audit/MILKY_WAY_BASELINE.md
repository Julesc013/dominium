Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/worldgen/MILKY_WAY_CONSTITUTION.md`, `schema/worldgen/galaxy_priors.schema`, and `src/geo/worldgen/worldgen_engine.py`.

# Milky Way Baseline

## Priors Summary

- Canonical realism profile: `realism.realistic_default_milkyway_stub`
- Canonical galaxy priors: `priors.milkyway_stub_default`
- Canonical generator version lock: `gen.v0_stub`
- Analytic macro prior surface:
  - disk radius `60000 pc`
  - bulge radius `6000 pc`
  - disk thickness `1200 pc`
  - spiral arm prior `4`
  - pitch angle prior `12.000 deg`
- Metallicity prior:
  - solar radius anchor `8000 pc`
  - solar metallicity anchor `1000 permille`
  - radial drop `40 permille / kpc`
  - bounded floor/ceiling `300..1400 permille`
- Star-formation prior:
  - age weights `young 140`, `mature 620`, `old 240`
  - IMF weights `M 620`, `K 220`, `G 110`, `F/A 50`
  - habitability bias anchored to `8000 pc +/- 4000 pc` and `|z| <= 600 pc`
- Cell policy:
  - GEO partition remains grid-addressed in galaxy frame
  - canonical MW cell size `10 pc`
  - canonical cap `24 systems per cell`

## Cell Generation Behavior

Milky Way cell generation remains on-demand only. The procedural base is derived from:

- `universe_seed`
- `realism_profile_id`
- `generator_version_id`
- `geo_cell_key`

For each requested cell, MW-0 now:

- derives galactocentric position from the GEO cell key
- evaluates analytic density, spiral-arm, bulge, metallicity, and habitability priors
- computes an expected system count and resolves it deterministically into a bounded `system_count`
- emits a deterministically ordered `generated_system_seed_rows` list keyed by `local_index`
- preserves stable star-system identity via `universe_id + cell_key + local_index`

Canonical fixture snapshots:

- Solar-band fixture `[800, 0, 0]`, `refinement_level=1`
  - `system_count = 7`
  - `metallicity_permille = 1000`
  - `habitable_filter_bias_permille = 1000`
  - `worldgen_result.deterministic_fingerprint = 60f30e610b9dc117985d356a4f96181682576b094d29b003b0ddc874290904b0`
- Dense-core fixture `[0, 0, 0]`, `refinement_level=0`
  - `uncapped_system_count = 27`
  - `system_count = 24`
  - `count_resolution = capped`
  - `metallicity_permille = 1320`

No star catalog, lore anchor, or real-data pack is required. Later named-star or catalog packs must overlay these stable base identities instead of replacing them.

## Refinement Ladder

- `L0`: cell summary plus deterministic `system_seed` rows only
- `L1`: `kind.star_system` objects materialize from those seeds
- `L2`: star and major-body placeholder expansion materializes from each system seed
- `L3`: surface-tile refinement remains available for downstream planet/earth work

This keeps Milky Way generation compatible with the existing GEO refinement contract while avoiding eager galaxy instantiation.

## Validation Snapshot

- TestX targeted MW subset: PASS on 2026-03-09
  - `test_mw_cell_generation_deterministic`
  - `test_system_count_bounded`
  - `test_system_ids_stable`
  - `test_cross_platform_mw_hash_match`
- RepoX targeted MW invariants: PASS on 2026-03-09
  - `INV-NO-CATALOG-REQUIRED`
  - `INV-MW-CELL-ON-DEMAND-ONLY`
  - `INV-NAMED-RNG-WORLDGEN-ONLY`
- AuditX targeted MW analyzers: PASS on 2026-03-09
  - `CatalogDependencySmell`
  - `EagerGalaxyInstantiationSmell`
- AuditX full scan: completed on 2026-03-09
  - output root `build/mw0/auditx/`
  - `findings_count = 2265`
  - `promotion_candidates = 69`
  - promoted strict blockers `= 0`
- RepoX STRICT full-repo run: failed on 2026-03-09 due pre-existing repository-wide governance drift
  - output root `build/mw0/repox/`
  - MW task-local groups remained clean:
    - `repox.runtime.worldgen violation_count = 0`
    - `repox.runtime.bundle violation_count = 0`
  - dominant blocking classes remained `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-REPOX-STRUCTURE`, `INV-NO-RAW-PATHS`, and `INV-TOOL-VERSION-MISMATCH`
- Strict build lane: blocked on 2026-03-09
  - `cmake --build --preset msvc-verify`
  - environment lacks `Visual Studio 18 2026`

## Topology Map

- `docs/audit/TOPOLOGY_MAP.json` regenerated on 2026-03-09
- deterministic fingerprint `4c00ee007bf34e54ff9630358f02a2371272031817fd62f170a1b2d2475b752e`
- node count `4324`
- edge count `9112`

## MW-1 Readiness

MW-0 leaves the repository ready for MW-1 system-seed artifact and query integration:

- the procedural Milky Way base is deterministic
- per-cell generation is bounded and on-demand
- stable system IDs are overlay-safe
- realism tuning is registry-driven rather than hardcoded catalog data
