Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Star System Orbital Priors

This document freezes the MW-2 star and orbital prior contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/STAR_SYSTEM_SEED_MODEL.md`

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E2` Deterministic ordering
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- `docs/worldgen/STAR_SYSTEM_SEED_MODEL.md`

## 1. Scope

MW-2 upgrades MW-1 star-system artifacts into coarse deterministic stellar and orbital priors.

MW-2 defines:

- one primary star per system for MVP
- planet count priors
- coarse orbital elements
- coarse planet body priors
- moon identity stubs only

MW-2 does not define:

- N-body dynamics
- full multi-star systems
- surface generation
- detailed climate
- authored catalogs

## 2. Primary Star Priors

Primary-star generation is deterministic and IMF-driven.

Inputs:

- `system_seed_value`
- inherited `metallicity_proxy`
- MW-0 age/IMF buckets
- realism-declared `system_priors`

Required outputs:

- `star_mass`
- `luminosity_proxy`
- `age_proxy`
- inherited `metallicity_proxy`

Rules:

- star mass is sampled deterministically from the IMF bucket band
- luminosity is an approximate deterministic mass-luminosity proxy
- age is an approximate deterministic value drawn inside the MW-0 age bucket range
- metallicity is inherited from the parent star-system artifact without reinterpretation

## 3. Planet Count Priors

Planet count is a deterministic proxy distribution conditioned by:

- primary star mass band
- metallicity proxy
- MW-0 habitability bias proxy
- realism-declared `planet_count_params`

Rules:

- count derivation is deterministic and bounded
- the cap is explicit profile data
- no random retry loops are permitted

## 4. Orbital Element Priors

For each planet `i`, MW-2 emits coarse orbital priors:

- `semi_major_axis`
- `eccentricity`
- `inclination`

Rules:

- orbital bands are multiplicative/log-spaced rather than linearly spaced
- eccentricity is bounded and must preserve periapsis ordering
- inclination remains small by default
- all ordering is canonical by `planet_index`

## 5. Major Body Seeds

For each planet, MW-2 emits coarse body priors:

- radius
- density class
- atmosphere class
- ocean fraction
- rotation period
- axial tilt

Allowed class examples:

- rocky
- terrestrial
- oceanic
- icy
- gas dwarf

Moon rule:

- moon presence is a deterministic stub probability only
- moon IDs may exist at L2
- moon surfaces and detailed moon body priors remain later work

## 6. Refinement Level L2

At `worldgen_request.refinement_level >= 2`, MW-2 may materialize:

- `kind.star`
- `kind.planet`
- `kind.moon` stubs

Attached model artifacts at `L2`:

- `star_artifact`
- `planet_orbit_artifact`
- `planet_basic_artifact`

Identity rules:

- primary star local subkey: `star:0`
- planet local subkey: `planet:<planet_index>`
- moon stub local subkey: `moon:<planet_index>:<moon_index>`

These IDs must remain stable for the same:

- universe lineage
- parent star-system identity
- local index ordering

## 7. Discovery Versus Instantiation

Discovery and instantiation remain distinct.

Discovery:

- may derive read-only L2 priors on demand
- may support habitable-likely filtering from those priors
- does not mutate authoritative state

Instantiation:

- occurs only through `process.worldgen_request`
- persists star/planet artifact models idempotently
- must not duplicate spawned objects or model artifacts

## 8. Named RNG Stream Law

MW-2 remains under GEO named RNG law.

Required derivation rule:

- cell-level named stream roots come from GEO-8 worldgen policy
- system-local substreams derive from `system_seed_value` plus deterministic stream-name salts

Canonical substream names:

- `rng.worldgen.system.primary_star`
- `rng.worldgen.system.planet_count`
- `rng.worldgen.system.planet.<i>`
- `rng.worldgen.system.moon_stub.<i>`

No wall-clock, process-global RNG, or anonymous random source is allowed.

## 9. Deterministic Stability Algorithm

MW-2 orbital spacing uses a deterministic forward pass only.

Definitions:

- `a_i`: semi-major axis of planet `i`
- `e_i`: eccentricity of planet `i` in permille
- `apo_i = ceil(a_i * (1000 + e_i) / 1000)`
- `peri_i = floor(a_i * (1000 - e_i) / 1000)`

Algorithm:

1. Compute a nominal multiplicative orbit ladder from the profile inner edge and spacing ratio.
2. Apply bounded deterministic jitter to each nominal orbit.
3. For `i > 0`, compute:
   - `min_allowed_i = ceil(a_(i-1) * min_spacing_ratio_permille / 1000)`
4. If `a_i < min_allowed_i`, replace it with:
   - `a_i = ceil(a_(i-1) * push_out_ratio_permille / 1000)`
5. Sample a raw deterministic eccentricity bound from profile data.
6. For `i > 0`, compute the largest allowed eccentricity that preserves ordered periapsis:
   - `max_e_i = 1000 - ceil(apo_(i-1) * periapsis_gap_ratio_permille / a_i)`
7. Clamp:
   - `e_i = min(raw_e_i, base_e_max_i, max(0, max_e_i))`

Consequences:

- no retry loops
- no unstable orbit crossings inside the coarse prior model
- identical inputs always yield identical orbital ladders

## 10. Habitable-Likely Stub

MW-2 may refine the MW-1 habitable-likely filter using:

- primary star mass band
- luminosity-derived temperate-band proxy
- presence of at least one rocky/oceanic planet with compatible atmosphere/ocean classes

This remains a procedural filter only.
It is not a claim of physical habitability.

## 11. Overlay Safety

MW-2 base identities remain overlay-safe.

Rules:

- catalogs or Sol pin packs must map onto stable star/planet IDs
- later overlays may sharpen priors or replace coarse model detail through lawful patches
- base IDs must not change absent explicit migration

## 12. Non-Goals

MW-2 does not include:

- real star catalogs
- barycentric simulation
- multi-body numerical integration
- terrain/surface tiles
- detailed moon generation

## 13. Readiness Outcome

MW-2 provides the minimum deterministic star-and-orbit substrate needed for:

- system inspection
- coarse habitability filtering
- later MW-3 surface macro generation
- later Sol overlay pinning

It does so without reopening MW-0 or MW-1 identity law.
