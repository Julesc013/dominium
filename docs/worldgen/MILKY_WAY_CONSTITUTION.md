Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Milky Way Constitution

This document freezes the Dominium v0.0.0 procedural Milky Way base model.

It is subordinate to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`,
`docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`, and the GEO worldgen contract.

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/geo/WORLDGEN_CONSTITUTION.md`

## 1. Scope

The Milky Way procedural base is a deterministic, data-light, on-demand galaxy model.

It is defined only from:

- `universe_seed`
- `realism_profile_id`
- `generator_version_id`
- `geo_cell_key`

It does not require:

- star catalogs
- real-data Milky Way packs
- eager galaxy instantiation
- wall-clock inputs

## 2. Macro Model

The procedural Milky Way uses realism-like analytic priors, not an exact claim of astronomical truth.

The canonical macro prior set must define:

- disk radius
- bulge radius
- disk thickness
- spiral arm count
- spiral arm pitch-angle prior
- stellar density tendency as a function of galactocentric radius `R` and height `z`

The default v0.0.0 prior target is:

- barred spiral tendency
- four-arm prior
- thin disk plus central bulge
- lower stellar density away from the midplane
- lower stellar density toward the far outer disk

## 3. Metallicity Gradient

The procedural base must encode a monotonic realism-like metallicity prior:

- higher metallicity toward the inner galaxy
- lower metallicity toward the outer galaxy

The base model is a gradient prior only.

It is not:

- a catalog
- a spectroscopy dataset
- a claim of exact observed abundance values

## 4. Star Formation Priors

The procedural base must encode deterministic star-formation tendencies through priors, not authored content.

Required priors:

- age-distribution tendency
- IMF tendency
- habitable-filter bias tendency

These priors may bias later system generation toward plausible Earth-like filtering, but they do not guarantee inhabited or authored systems.

## 5. Cell Resolution

The Milky Way base is partitioned through GEO cell keys in the galaxy frame.

Rules:

- the partition profile remains GEO-owned
- the Milky Way layer interprets that partition through a `cell_size_pc` prior
- cell generation is always local to the requested `geo_cell_key`
- no whole-galaxy enumeration is allowed

The default v0.0.0 Milky Way priors use:

- `cell_size_pc = 10`
- `max_systems_per_cell = 24`

These values are realism-like and deliberately bounded for deterministic on-demand generation.

## 6. On-Demand Generation

Each galaxy cell is generated only when requested.

Per-cell generation must:

1. derive a deterministic galactocentric position from the GEO cell key in the canonical galaxy frame
2. evaluate density and metallicity priors for that cell
3. compute an expected star-system count `lambda`
4. resolve a bounded deterministic system count `N`
5. emit a deterministically ordered `system_seed` list for local indices `0..N-1`

No eager background pass may instantiate the galaxy.

## 7. Refinement Ladder

The canonical Milky Way refinement ladder is:

- `L0`
  - the cell exists
  - deterministic system-seed descriptors are emitted
  - no star/system body expansion is required
- `L1`
  - deterministic star-system assembly anchors may be instantiated from the seed list
- `L2`
  - deterministic stars and major bodies may be instantiated
- `L3`
  - planet surface refinement is delegated onward to later Earth/surface work

Rules:

- higher refinement is explicit
- lower refinement does not imply deeper materialization
- previously emitted local indices for a cell must remain stable for the same generator version

## 8. Identity

Milky Way system identity remains GEO-owned and overlay-safe.

Required rule:

- star-system lineage must be derived from stable GEO object identity with
  - locked universe identity
  - `geo_cell_key`
  - `object_kind_id = kind.star_system`
  - `local_subkey = star_system:<local_index>`

Effective consequence:

- the same universe lineage and cell always produce the same base star-system IDs
- later catalog overlays, named-star packs, and lore anchors must bind onto these stable IDs through overlay patches
- overlay packs must not replace the base identity derivation

## 9. Determinism

Milky Way generation must preserve:

- named RNG streams only
- deterministic local-index ordering
- deterministic remainder or deterministic PRNG count selection
- deterministic cap enforcement
- replay/hash equivalence for repeated requests

Forbidden:

- wall-clock dependence
- unordered iteration dependence
- nondeterministic catalog fallback
- runtime special-casing by platform

## 10. Overlay Safety

The procedural Milky Way is the canonical base layer.

Later layers may add:

- named stars
- real catalogs
- lore anchors
- official astronomy packs

They must do so only as overlays above the procedural base.

They must not:

- replace base IDs
- reinterpret local indices silently
- require the base generator to depend on catalog content

## 11. Non-Goals

MW-0 does not include:

- named star catalogs
- eager galaxy construction
- authored lore anchors
- interstellar travel mechanics
- civilization content
- exact astrophysical claim surfaces

## 12. Readiness Outcome

This constitution makes the Milky Way base ready for:

- deterministic cell-addressed galaxy generation
- replay-stable system-seed enumeration
- later MW-1 query/teleport integration
- later overlay packs for Sol, catalogs, and named anchors

It does not reopen:

- GEO identity law
- generator-version locking
- overlay merge rules
- pack-driven layering
