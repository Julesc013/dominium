Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Star System Seed Model

This document freezes the MW-1 star-system seed and artifact contract for Dominium v0.0.0.

It is subordinate to:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/specs/SPEC_MVP0_SCOPE_CONSTITUTION.md`
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`
- the GEO worldgen contract

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A7` Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/worldgen/MILKY_WAY_CONSTITUTION.md`

## 1. Scope

MW-1 turns the MW-0 cell-local star-system seed list into a first-class deterministic artifact surface.

It does not yet define:

- star mass
- stellar spectra
- planet inventories
- orbital mechanics

Those remain later MW series work.

## 2. StarSystemSeed

A `StarSystemSeed` is the canonical deterministic descriptor for a Milky Way star-system lineage before deeper astrophysical expansion.

It is derived from:

- `geo_cell_key`
- `local_index`
- `system_seed_value`

The seed is subordinate to MW-0 cell generation and must remain replay-stable for the same:

- `universe_seed`
- `realism_profile_id`
- `generator_version_id`
- `geo_cell_key`

Rules:

- `local_index` ordering is canonical within a cell
- seed rows are deterministic derived views
- seed rows do not authorize mutation by themselves

## 3. StarSystem Artifact

At `worldgen_request.refinement_level >= 1`, each seed may materialize as a `kind.star_system` artifact.

The artifact is a deterministic model attached to the stable GEO object identity for that star system.

Required artifact content:

- stable `object_id`
- `system_seed_value`
- galaxy-frame position reference
- metallicity proxy

Allowed MW-1 metadata:

- habitable-likely bias proxy
- age bucket
- IMF bucket
- source cell and local index

Forbidden MW-1 metadata:

- derived star mass claims
- planet/body lists
- authored names
- catalog authority

## 4. Discovery Versus Instantiation

Discovery and instantiation are distinct surfaces.

### Discovery

Discovery is a derived, non-mutating view of procedural star-system availability.

Examples:

- list systems in a cell
- query nearest system to a position
- filter habitable-likely candidate systems

Discovery may read deterministic worldgen/query surfaces, but it does not mutate authoritative state.

### Instantiation

Instantiation is authoritative and must occur only through `process.worldgen_request`.

Rules:

- refinement `L1` is the canonical star-system instantiation threshold
- repeated requests for the same cell/refinement must be idempotent
- duplicate star-system artifacts are forbidden

## 5. Identity

Star-system artifact identity remains MW-0 and GEO-1 derived.

Required lineage rule:

- `object_kind_id = kind.star_system`
- `local_subkey = star_system:<local_index>`

Consequences:

- the same universe lineage and cell always yield the same star-system object IDs
- teleport/query integration must reference those stable IDs
- later catalog overlays must bind onto these IDs rather than replacing them

## 6. Query Contract

MW-1 query surfaces must remain:

- deterministic
- ordered
- on-demand
- budget-bounded by the requested search scope

Required operations:

- `list_systems_in_cell(cell_key)`
- `query_nearest_system(position_ref, radius)`
- `filter_habitable_candidates(criteria_stub)`

Rules:

- deterministic cell enumeration order is mandatory
- query results must sort stably
- discovery may trigger derived refinement reads, but not eager galaxy instantiation

## 7. Teleport Integration

Teleport to a procedural star system must resolve through stable `target_object_id` semantics.

Required behavior:

- if the target star-system artifact is not yet materialized, the runtime requests deterministic `L1` worldgen for the containing cell
- the resolved teleport target remains the stable star-system `object_id`
- no catalog is required

This keeps teleport within the existing lawful process and navigation surfaces.

## 8. Replay And Proof

MW-1 replay/proof must capture:

- star-system seed values
- instantiated star-system artifact IDs
- deterministic artifact ordering

Repeated runs with the same inputs must reproduce the same:

- seed rows
- artifact rows
- worldgen result hash

## 9. Non-Goals

MW-1 does not include:

- full stellar generation
- planet generation
- named stars
- real star catalogs
- eager procedural galaxy indexing

## 10. Readiness Outcome

This model makes MW-0 seeds usable by MVP discovery and teleport workflows while preserving:

- process-only mutation
- stable object identity
- overlay safety
- replay equivalence

It prepares the repository for MW-2 star and orbital priors without reopening the MW-0 constitutional base.
