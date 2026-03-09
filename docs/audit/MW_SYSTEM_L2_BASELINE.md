Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, `docs/worldgen/MILKY_WAY_CONSTITUTION.md`, `docs/worldgen/STAR_SYSTEM_SEED_MODEL.md`, `docs/worldgen/STAR_SYSTEM_ORBITAL_PRIORS.md`, `schema/worldgen/system_priors.schema`, `schema/worldgen/planet_priors.schema`, `schema/worldgen/star_artifact.schema`, `schema/worldgen/planet_orbit_artifact.schema`, `schema/worldgen/planet_basic_artifact.schema`, and `src/worldgen/mw/mw_system_refiner_l2.py`.

# MW System L2 Baseline

## Star Priors

- Canonical realism profile: `realism.realistic_default_milkyway_stub`
- Canonical system priors: `priors.system_default_stub`
- Canonical planet priors: `priors.planet_default_stub`
- Canonical generator version lock: `gen.v0_stub`

Primary-star priors now refine each MW-1 `kind.star_system` artifact into one deterministic `kind.star`.

Default star prior ranges:

- IMF mass bands:
  - `m`: `80..600 milli_solar_mass`
  - `k`: `600..900 milli_solar_mass`
  - `g`: `900..1100 milli_solar_mass`
  - `f_a`: `1100..2200 milli_solar_mass`
- Age proxy buckets:
  - `young`: `300..2500 gyr_milli`
  - `mature`: `2500..7000 gyr_milli`
  - `old`: `7000..12000 gyr_milli`
- Luminosity remains a coarse deterministic mass-luminosity proxy.
- Metallicity is inherited directly from the parent MW-1 star-system artifact.

Canonical solar-band fixture (`geo_cell_key = [800, 0, 0]`, `refinement_level = 2`) yields:

- `star_artifact_count = 7`
- `star_artifact_hash_chain = bedb6c7caa0af2d75d96975869fa7f8eadd0f24b28a9f5fbabd18a85287faa3e`

## Planet Priors

MW-2 now derives bounded coarse major-body priors for deterministic `kind.planet` and `kind.moon` stub identities.

Default count and orbit priors:

- base planets by star band:
  - `m = 2`
  - `k = 3`
  - `g = 4`
  - `f_a = 5`
- deterministic count jitter: `+/- 1`
- metallicity bonus threshold: `950 permille`
- habitability bonus threshold: `780 permille`
- hot-star penalty threshold: `1500 milli_solar_mass`
- `max_planets = 8`
- `max_moons_per_planet = 1`

Default orbital ladder priors:

- inner edge `220 milli_au`
- outer edge `24000 milli_au`
- nominal spacing ratio `1680 permille`
- band jitter `140 permille`
- minimum spacing ratio `1350 permille`
- push-out ratio `1450 permille`
- periapsis gap ratio `1050 permille`

Default planet-body priors:

- classes: `rocky`, `terrestrial`, `oceanic`, `icy`, `gas_dwarf`
- radius ranges:
  - rocky `2400..6800 km`
  - terrestrial `4500..8200 km`
  - oceanic `5000..9000 km`
  - icy `2600..7200 km`
  - gas dwarf `14000..32000 km`

Canonical solar-band fixture (`geo_cell_key = [800, 0, 0]`, `refinement_level = 2`) yields:

- `planet_basic_artifact_count = 33`
- `moon_stub_count = 9`
- `planet_orbit_artifact_hash_chain = b016e3c70ed7ced8ff323abf77106822fc3e50838d2bba360303c51b6f61b78b`
- `planet_basic_artifact_hash_chain = e5fa430a63c4f2cd73ff357c68e45c81bb1cfafc15cc86a86959b7520700025a`
- `system_l2_summary_hash_chain = a12880a5d2b7c85ec0a9b8f86d0130095e9b6eeb31a5f7322833232439d1a803`
- combined L2 artifact hash `= 1e197bb1089acc92bc6f0fe054e9265f24c176a135a14273a6e3c9f759f4f193`
- authoritative `worldgen_result_hash_chain = 932d8c70066128b65aaeca682f1521ea5f9a5c56d2168331fdcb355008e13f85`

## Stability Constraints

MW-2 orbital stability remains coarse but deterministic.

The implemented algorithm:

1. Builds a multiplicative orbit ladder from the profile inner edge and spacing ratio.
2. Applies bounded deterministic jitter once.
3. If orbit `i` is too close to orbit `i-1`, pushes it outward with `push_out_ratio_permille`.
4. Clamps eccentricity with the periapsis-order bound from the previous apoapsis.
5. Never retries with fresh randomness.

Observed baseline properties on the canonical fixture:

- orbit ordering is stable by `planet_index`
- semi-major axis never regresses within a system
- periapsis ordering remains strictly monotone
- repeated L2 refinement is idempotent

## Query And Filter Integration

MW-1 discovery/query surfaces now enrich deterministically with MW-2 priors when `refinement_level >= 2`.

Available coarse query enrichment:

- `star_mass_milli_solar`
- `planet_count`
- `candidate_habitable_planet_count`
- `l2_available`

`filter_habitable_candidates(...)` remains a stub filter, but it now ranks candidates using:

- habitable-likely planet count
- star-mass closeness to solar
- MW-0 habitability bias
- metallicity proxy
- stable `object_id` tie-breaks

## Validation Snapshot

- Frozen contract hash guard: PASS on 2026-03-09
- Identity fingerprint check: PASS on 2026-03-09
- Replay proof tool: PASS on 2026-03-09
  - `tools/worldgen/tool_replay_system_l2.py`
  - repeated runs remained byte-stable
- Targeted RepoX MW-2 invariants: PASS on 2026-03-09
  - `INV-L2-OBJECTS-ID-STABLE`
  - `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN`
- Targeted AuditX MW-2 analyzers: PASS on 2026-03-09
  - `E359_NONDETERMINISTIC_ORBIT_SMELL`
  - `E360_UNBOUNDED_GENERATION_SMELL`
- Targeted TestX MW-2 subset: PASS on 2026-03-09
  - `test_star_properties_deterministic`
  - `test_planet_count_deterministic`
  - `test_orbital_spacing_constraints`
  - `test_idempotent_refinement_l2`
  - `test_cross_platform_l2_hash_match`
- AuditX full scan: completed on 2026-03-09
  - output root `build/mw2/auditx/`
  - `findings_count = 2267`
  - `promotion_candidates = 69`
- RepoX STRICT full-repo run: failed on 2026-03-09 due pre-existing repository-wide governance drift
  - output root `build/mw2/repox/`
  - MW task-local groups remained clean:
    - `repox.runtime.worldgen violation_count = 0`
    - `repox.runtime.bundle violation_count = 0`
  - dominant blocking classes remained `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-REPOX-STRUCTURE`, `INV-NO-RAW-PATHS`, and `INV-TOOL-VERSION-MISMATCH`
- Strict build lane: blocked on 2026-03-09
  - `cmake --build --preset msvc-verify`
  - environment lacks `Visual Studio 18 2026`

## Topology Map

- `docs/audit/TOPOLOGY_MAP.json` regenerated on 2026-03-09
- deterministic fingerprint `f7cf938f498ae7845c29b90e8bad399b6a6a74be209886e43dcd62593cfb0e1c`
- node count `4349`
- edge count `9172`

## MW-3 And SOL-0 Readiness

MW-2 leaves the repository ready for:

- MW-3 surface macro generation from stable planet identities and coarse body priors
- SOL-0 overlay pinning onto stable star, planet, and moon stub identities
- continued habitable-likely discovery without reopening MW-0 or MW-1 identity law
