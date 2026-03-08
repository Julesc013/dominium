Status: AUDIT
Last Updated: 2026-03-08
Version: 1.0.0
Scope: GEO-1 retro-consistency audit for deterministic spatial indexing and stable identity.

# GEO-1 Retro Audit

## 1) Referenced Invariants

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A6 Provenance is mandatory
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C3 CompatX obligations
- `docs/geo/GEO_CONSTITUTION.md`

## 2) Existing Identity Schemes

### Universe identity

- `UniverseIdentity` already anchors immutable creation identity through:
  - `universe_id`
  - `identity_hash`
  - `physics_profile_id`
  - GEO profile IDs added in GEO-0:
    - `topology_profile_id`
    - `metric_profile_id`
    - `partition_profile_id`
    - `projection_profile_id`
- Current identity is stable and hash-backed.
- This is the correct root anchor for future deterministic spatial object IDs.

### Assembly IDs

- `assembly_id` remains common across runtime rows and tooling.
- Existing assembly IDs are mostly authored or ad hoc string identifiers:
  - cameras/instruments in `tools/xstack/sessionx/creator.py`
  - system placeholder assemblies in `src/system/system_collapse_engine.py`
  - body assemblies and ownership references in SRZ/runtime paths
- These IDs are not currently derived from topology/partition/cell-key inputs.
- GEO-1 must not rewrite these IDs without explicit CompatX migration.

### Object and site IDs

- Astronomy/site navigation currently uses pack-authored stable IDs such as:
  - `object.earth`
  - `object.sol_system`
  - `site.*`
- These appear in:
  - `schemas/astronomy_catalog_entry.schema.json`
  - `src/net/srz/routing.py`
  - `src/net/srz/shard_coordinator.py`
  - UI/session tooling paths that target `object_id` / `site_id`
- Current object IDs are stable enough for authored catalog content, but not yet tied to partition-aware GEO cell identity.
- GEO-1 should provide the future derived-ID path for procedural spatial objects without changing authored catalog IDs.

## 3) Existing Spatial Partitioning

### Field partitioning

- FIELD now routes position-to-cell mapping through `geo_partition_cell_key(...)`.
- `build_field_cell(...)` and downstream consumers still store a legacy string `cell_id`.
- Legacy `cell_id` remains an opaque token, not a structured `GeoCellKey` object.
- Migration need:
  - preserve legacy `cell_id` compatibility,
  - introduce structured `GeoCellKey` for future spatial indexing and identity derivation.

### ROI scheduling

- SYS ROI scheduling in `src/system/roi/system_roi_scheduler.py` currently works on `system_id` sets and tier transition decisions.
- It does not yet partition by GEO cell key range.
- Migration need:
  - future GEO-aware ROI refinement should map system/object scope to deterministic geo cell ranges rather than only system IDs.

### Shard ownership

- SRZ routing and shard ownership are currently keyed primarily by `object_id` and fallback ownership maps.
- `src/net/srz/shard_coordinator.py` uses deterministic hashing of `object_id` for interest ordering and shard fallback.
- Cross-shard references already prefer stable IDs, but shard assignment is not yet expressed as geo-cell-key range ownership.
- Migration need:
  - shard assignment should become explicitly geo-cell-key range based for spatial workloads,
  - cross-shard references should keep using stable object IDs.

## 4) Existing Spatial ID Smells

- Legacy `cell.*` string formatting remains in tests, tools, and a few runtime compatibility paths.
- Pollution and thermal helpers still consume string cell IDs rather than structured GEO cell keys.
- Some stress generators create synthetic cell IDs by local naming patterns rather than topology/partition-derived keys.
- Existing object/site IDs are mixed:
  - pack-authored navigational IDs for astronomy/site data,
  - runtime assembly IDs for embodied assemblies,
  - field cell IDs for scalar/vector fields.

## 5) Migration Needs

- Future spatial objects must derive identity from:
  - `universe_identity_hash`
  - `topology_profile_id`
  - `partition_profile_id`
  - `geo_cell_key`
  - `object_kind_id`
  - deterministic local subkey
- Existing authored object IDs must remain unchanged unless a CompatX migration path is added.
- Existing assembly IDs must remain unchanged unless a CompatX migration path is added.
- Future procedural generation should target `GeoCellKey`, not float positions or opaque legacy strings.
- Future field/object rows should be able to carry:
  - legacy `cell_id` for compatibility
  - structured `geo_cell_key` for canonical GEO identity
- Future shard planners should assign ownership by deterministic geo cell ranges, while cross-shard references remain stable-ID based.

## 6) GEO-1 Acceptance Boundary

GEO-1 should:

- introduce deterministic structured cell keys
- introduce deterministic spatial object ID derivation
- preserve existing authored/runtime identity schemes unless explicit migration is later added
- keep topology/partition awareness first-class and profile-driven

GEO-1 should not:

- rewrite existing astronomy `object_id` values
- rewrite existing `assembly_id` values
- force all current field/runtime rows to migrate in one step
- introduce non-deterministic local indexing
