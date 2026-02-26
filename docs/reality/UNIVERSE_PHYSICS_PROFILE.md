Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# UniversePhysicsProfile

## Purpose
Define a canonical immutable physics selection artifact for every universe lineage and guarantee deterministic null boot with zero packs.

## A) UniversePhysicsProfile Contract
Universe physics selection is represented by `UniversePhysicsProfile`, a canonical immutable artifact referenced by `UniverseIdentity`.

Required fields:
- `physics_profile_id`
- `version`
- `enabled_domain_ids`
- `conservation_contract_set_id`
- `allowed_exception_types`
- `numeric_precision_policy_id`
- `tier_taxonomy_id`
- `time_model_id`
- `boundary_model_id`
- `default_error_budget`
- `extensions`

`UniversePhysicsProfile` declares policy and compatibility anchors only. It does not directly execute solver semantics.

Implementation note:
- Runtime payload uses `error_budget` schema field; doctrine alias `default_error_budget` refers to the same profile budget contract.

## B) Null Boot Doctrine
Engine runtime must boot and tick deterministically with no packs installed and no optional content present.

Null boot requirements:
- Empty domain set is valid.
- Empty material registry is valid.
- Empty world assemblies are valid.
- Simulation tick execution remains deterministic.
- Save/load works for empty universes.

Core runtime must not assume any specific domain, solver, material family, or realistic-physics pack.

## C) Defaults As Packs
Realistic physics defaults are data, not code assumptions.

- `physics.default.realistic` is an optional pack.
- It contributes one or more `UniversePhysicsProfile` payloads.
- Runtime must degrade/refuse deterministically if a requested non-null profile is unavailable.
- Runtime must continue with `physics.null` when no explicit profile is selected.

## D) Immutability Rule
`UniversePhysicsProfile` is immutable after `UniverseIdentity` creation.

Rules:
- `physics_profile_id` is part of universe identity hash input.
- Mid-session profile mutation is forbidden and must refuse deterministically.
- Physics changes require a new universe lineage.
- CompatX migration handles schema evolution, not in-place physics rewrite of existing lineage identity.

## Null Profile Baseline
Core runtime provides built-in `physics.null` for zero-pack execution:
- `enabled_domain_ids`: `[]`
- `conservation_contract_set_id`: `none`
- `allowed_exception_types`: `[]`
- `numeric_precision_policy_id`: `default_null`
- `tier_taxonomy_id`: `default_minimal`
- `time_model_id`: `default_single_tick`
- `boundary_model_id`: `procedural_infinite`

The built-in null profile is minimal, deterministic, and non-semantic by design.
