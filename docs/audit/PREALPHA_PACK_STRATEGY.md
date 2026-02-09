Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Prealpha Pack Strategy

## Scope

Validation that disposable pre-alpha content remains data-only and does not leak into runtime code assumptions.

## Implemented

- Placeholder packs added:
  - `data/packs/org.dominium.content.worldgen.placeholder`
  - `data/packs/org.dominium.content.terrain.placeholder`
  - `data/packs/org.dominium.content.institutions.placeholder`
  - `data/packs/org.dominium.content.resources.placeholder`
- Each placeholder pack manifest declares:
  - `pack.maturity.prealpha` tag
  - `pack.stability.disposable` tag
  - extensions `maturity=prealpha` and `stability=disposable`.
- Runtime pre-alpha profiles added:
  - `data/profiles/profile.runtime_min_prealpha.json`
  - `data/profiles/profile.runtime_full_prealpha.json`
- RepoX enforcement added:
  - `INV-PREALPHA-PACK-ISOLATION`
  - checks explicit pre-alpha markers;
  - fails if runtime source files reference pre-alpha pack IDs.

## Test Coverage

- `tests/distribution/distribution_prealpha_pack_tests.py`
  - validates marker completeness;
  - validates no runtime literal pre-alpha pack IDs;
  - validates replacement behavior using:
    - `tests/distribution/fixtures/packs_prealpha_a/...`
    - `tests/distribution/fixtures/packs_prealpha_b/...`
  - validates deterministic refusal when required capability is absent.

## Readiness Statement

- Pre-alpha pack churn is isolated to pack/data surfaces.
- Runtime code remains pack-ID-agnostic under RepoX and TestX coverage.
