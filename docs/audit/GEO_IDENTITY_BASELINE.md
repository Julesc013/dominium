Status: BASELINE
Last Updated: 2026-03-08
Version: 1.0.0
Scope: GEO-1 deterministic spatial indexing and stable identity baseline.

# GEO Identity Baseline

## 1) Scope

GEO-1 freezes deterministic spatial addressing and stable spatial identity on top of the GEO-0 topology/metric/partition/projection constitution.

The authoritative doctrine is `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`.

Relevant invariants and contracts upheld:

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C3 CompatX obligations
- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`

## 2) Retro Audit Summary

Retro-consistency findings are recorded in `docs/audit/GEO1_RETRO_AUDIT.md`.

The audit confirmed:

- `UniverseIdentity.identity_hash` is the correct immutable root anchor for future spatial identity derivation
- authored astronomy `object_id` and runtime `assembly_id` surfaces must remain unchanged until explicit CompatX migration exists
- FIELD partitioning already routes through GEO-0 compatibility helpers but still stores opaque legacy `cell_id` strings
- ROI scheduling and shard routing still use legacy system/object scopes and will need later GEO-aware range migration

GEO-1 therefore stays additive:

- structured `GeoCellKey` becomes the canonical spatial address
- legacy `cell.*` and `atlas.*` aliases remain compatibility surfaces only
- new procedural spatial identity uses GEO-derived object IDs without rewriting existing authored IDs

## 3) Schema and Registry Baseline

Strict v1.0.0 schema set added:

- `schema/geo/geo_cell_key.schema`
- `schema/geo/object_identity.schema`
- `schema/geo/cell_refinement_relation.schema`

CompatX integration added corresponding entries in `tools/xstack/compatx/version_registry.json`.

Baseline registry added:

- `data/registries/object_kind_registry.json`

Representative object kinds now include:

- `kind.galaxy_cell`
- `kind.star_system`
- `kind.star`
- `kind.planet`
- `kind.moon`
- `kind.surface_tile`
- `kind.interior_cell`
- `kind.structure`
- `kind.vehicle`
- `kind.signal_node`
- `kind.logic_network`

## 4) Cell Key Formats

Canonical spatial cell identity is now a structured `GeoCellKey` record with:

- `partition_profile_id`
- `topology_profile_id`
- `chart_id`
- `index_tuple`
- `refinement_level`
- `deterministic_fingerprint`

Baseline address forms frozen by GEO-1:

- grid and volumetric partitions:
  - `chart.global.* + index_tuple[N]`
- torus grid partitions:
  - canonicalized to fundamental-domain cell indices using topology-declared `period_cell_counts`
- sphere atlas partitions:
  - `chart.atlas.north|south + [u_idx, v_idx]`
- tree stubs:
  - spatial index tuples plus explicit `refinement_level`

Compatibility aliases remain available in `GeoCellKey.extensions.legacy_cell_alias`, but they are no longer the canonical identity surface.

## 5) ID Derivation Rules

The stable GEO object ID rule is:

`object_id_hash = H(universe_identity_hash, topology_profile_id, partition_profile_id, geo_cell_key, object_kind_id, local_subkey)`

The runtime implementation lives in:

- `src/geo/index/geo_index_engine.py`
- `src/geo/index/object_id_engine.py`

Key rules now enforced:

- world-facing cell targeting uses `geo_cell_key_from_position(...)`
- neighbor traversal over structured keys uses `geo_cell_key_neighbors(...)`
- refinement lineage uses `geo_refine_cell_key(...)`
- spatial object identity uses `geo_object_id(...)`
- `local_subkey` must be deterministic string or integer input only
- object ID hashing uses semantic cell-key fields, not incidental extension metadata

Existing authored `object_id` and `assembly_id` values remain unchanged.

## 6) Refinement Relationships

Refinement is now explicit through `cell_refinement_relation`:

- parent cell key preserved
- child cell key derived deterministically at target refinement level
- lineage is replay-stable and hash-stable

Baseline refinement rule in GEO-1:

- child anchor cell indices scale deterministically by the declared refinement branch factor
- parent-child relation is serialized and fingerprinted explicitly

This is sufficient for future coarse-to-fine workflows such as:

- galaxy cell -> system cell
- system cell -> planet region
- atlas tile -> refined sub-tile

## 7) Proof And Enforcement Baseline

Proof/replay integration added:

- `tools/geo/tool_verify_id_stability.py`
- GEO identity context is included in control proof bundle `extensions` when relevant GEO metadata is present

RepoX scaffolding added:

- `INV-SPATIAL-OBJECTS-MUST-USE-GEO_IDS`
- `INV-NO-ADHOC-SPATIAL-KEYS`

AuditX analyzers added:

- `E334_ADHOC_SPATIAL_KEY_SMELL`
- `E335_NONDETERMINISTIC_LOCAL_INDEX_SMELL`

These rules are intentionally narrow in GEO-1:

- they validate the canonical GEO indexing/identity surfaces
- they guard likely future regression points
- they do not silently rewrite legacy authored identity schemes

## 8) Contract and Schema Impact

Changed:

- GEO doctrine now includes stable spatial addressing and derived spatial object identity
- new schema family for `GeoCellKey`, `object_identity`, and refinement relation
- new object-kind registry
- new deterministic indexing and identity runtime APIs
- proof bundle extensions may now carry GEO identity context when relevant
- new RepoX/AuditX/TestX scaffolding for GEO identity discipline

Unchanged:

- process-only mutation invariant
- observer/renderer/truth separation
- authored astronomy/site IDs
- existing `assembly_id` behavior
- worldgen content responsibilities
- pathfinding responsibilities
- geometry editing responsibilities

## 9) Validation Snapshot

Executed during GEO-1 baseline:

- RepoX STRICT:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - findings: `17` warnings, `0` refusals after topology map regeneration
- AuditX STRICT:
  - `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass`
  - findings: `1425`
  - promoted blockers: `0`
- targeted GEO-1 TestX suite:
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_cell_key_from_position_deterministic,test_object_id_stable,test_refinement_relation_stable,test_torus_wrap_cell_keys,test_sphere_atlas_cell_keys_deterministic`
  - result: `pass`
- GEO ID stability verifier:
  - `py -3 tools/geo/tool_verify_id_stability.py`
  - result: `complete`
  - deterministic fingerprint: `ba5d6e209cbf5df78f7c0fa4b319b35844443e5f0552d8b80ee5cc1ad8bb3cfa`
  - run hash: `3da2fe772fd13fe5c8e02a45c1b241f7f96185b9df53b036ba19ce976163c31b`
- topology map regeneration:
  - `py -3 tools/governance/tool_topology_generate.py --repo-root .`
  - result: `complete`
  - deterministic fingerprint: `9e432ad8af427493bf4d439694bbdf57706c3d2a76564cab641faa808394baa0`
- strict build:
  - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.geo1 --cache on --format json`
  - result: `complete`
  - canonical content hash: `9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`

As with GEO-0, RepoX and AuditX still surface unrelated legacy warnings elsewhere in the repository, but GEO-1 introduced no promoted blockers and no new refusal-class invariant break after the topology map refresh.

## 10) Readiness for GEO-2

GEO-1 is ready for GEO-2 frames/floating-origin work because:

- topology-aware cell identity is now stable
- torus and sphere-atlas cell addressing are canonicalized deterministically
- refinement lineage is explicit
- object identity can survive world detail refinement and overlay layering
- shard-facing spatial planning can move from object-centric fallback maps toward key-range ownership without revisiting identity foundations

Deferred beyond GEO-1:

- floating-origin and frame hierarchies
- spatial index acceleration structures beyond the baseline stubs
- worldgen content generation
- geometry editing workflows
