# Spatial Index And Identity

Status: CANONICAL
Last Updated: 2026-03-08
Scope: GEO-1 doctrine for deterministic spatial cell keys, stable object identity, and refinement lineage.

## 1) Purpose

Freeze the identity contract that lets procedural space, authored overlays, mods, and save edits target the same spatial substrate without depending on float coordinates or unstable generation order.

This doctrine is additive to GEO-0:

- GEO-0 defines topology, metric, partition, and projection law
- GEO-1 defines stable spatial addressing and stable spatial object identity

## 2) Constitutional Dependencies

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C3 CompatX obligations
- `docs/canon/glossary_v1.md` Space
- `docs/canon/glossary_v1.md` Shard
- `docs/geo/GEO_CONSTITUTION.md`

## 3) Core Normative Rule

Authoritative spatial identity is not a float position and not an ad hoc string.

Authoritative spatial identity is the composition of:

1. `topology_profile_id`
2. `partition_profile_id`
3. `GeoCellKey`
4. deterministic object-kind lineage inputs

Future spatial workloads must address cells by key and derive procedural object identity from those keys.

## 4) GeoCellKey

`GeoCellKey` is the canonical deterministic address of a partition cell.

### 4.1 Required shape

Every canonical `GeoCellKey` must include:

- `partition_profile_id`
- `topology_profile_id`
- `chart_id`
- `index_tuple`
- `refinement_level`
- `deterministic_fingerprint`

### 4.2 Semantics

`GeoCellKey` addresses a cell within a declared partition and topology:

- grid spaces use integer lattice indices
- atlas spaces use deterministic chart plus tile indices
- tree partitions use deterministic node path or node coordinates
- higher-dimensional spaces use index tuples whose length matches the declared partition addressing dimension

`GeoCellKey` must be:

- serializable
- hashable
- deterministic across platforms
- pure data with no hidden runtime state

### 4.3 Canonical examples

The baseline constitutional forms are:

- grid `Z^D`: `(partition_profile_id, topology_profile_id, chart_id, [i0, i1, ...], refinement_level)`
- atlas tile: `(partition_profile_id, topology_profile_id, chart_id, [u_idx, v_idx], refinement_level)`
- octree stub: `(partition_profile_id, topology_profile_id, chart_id, [depth, ix, iy, iz], refinement_level)`

Legacy opaque strings such as `cell.*` may remain as compatibility aliases, but they are not the canonical GEO-1 identity surface.

## 5) Position To Cell Mapping

The canonical mapping is:

`position + topology_profile_id + partition_profile_id + chart_id -> GeoCellKey`

Rules:

- position-to-key mapping must be deterministic
- float use is allowed only as deterministic quantization input when deriving the partition cell
- once a `GeoCellKey` is derived, downstream spatial identity must use the key rather than the source float
- chart selection must be explicit for atlas or multi-chart spaces

## 6) Stable Object Identity

Future spatial object identity is derived, not improvised.

### 6.1 Formula

`object_id = H(universe_identity_hash, topology_profile_id, partition_profile_id, geo_cell_key, object_kind_id, local_subkey)`

Where:

- `H` is the canonical deterministic repo hash function
- `geo_cell_key` is the canonical serialized GEO-1 cell key payload
- `object_kind_id` identifies the stable spatial object kind
- `local_subkey` is deterministic inside the cell and kind scope

### 6.2 Local subkey rule

`local_subkey` must be derived from deterministic ordering only.

Allowed examples:

- `star:0`
- `planet:2`
- `tile:12`
- authored subkey names when the authored order is stable and canonicalized

Forbidden examples:

- insertion-order-dependent counters
- wall-clock stamps
- thread-dependent iteration indexes
- random UUIDs

### 6.3 Compatibility rule

GEO-1 does not rewrite existing authored object IDs or assembly IDs.

Existing identity surfaces may remain for:

- authored astronomy catalogs
- legacy assemblies
- navigational site IDs

New procedural spatial identity must use GEO-derived identity unless and until CompatX migration law declares otherwise.

## 7) Refinement Lineage

Partition refinement must preserve parent-child lineage explicitly.

### 7.1 Rule

A child cell key must name its parent lineage through a deterministic refinement relation.

Examples:

- galaxy cell -> system cell
- system cell -> planet region
- atlas tile -> refined sub-tile

### 7.2 Requirements

Refinement must be:

- explicit
- deterministic
- reversible to parent lineage where contractually possible
- stable under replay

Refinement level is part of the identity envelope but does not replace the full index tuple.

## 8) Shard Boundaries

Shard ownership for spatial workloads is assigned by `GeoCellKey` range, set, or deterministic partition subset.

Rules:

- shard planners assign by cell keys, not raw floats
- cross-shard references use stable object IDs only
- boundary exchange surfaces may summarize neighboring cell ranges, but not bypass shard contracts
- topology seams, wraps, and atlas transitions must still resolve through the same key lineage

## 9) GEO API Obligations

The following GEO-1 APIs are authoritative:

- `geo_cell_key_from_position(...)`
- `geo_cell_key_neighbors(...)`
- `geo_refine_cell_key(...)`
- `geo_object_id(...)`

Domains must not:

- create ad hoc spatial key formats
- derive spatial IDs from floats directly
- rely on nondeterministic local indexing inside cells

## 10) Proof And Replay

Proof surfaces that reason about spatial identity should include:

- `topology_profile_id`
- `partition_profile_id`
- canonical cell key payload or hash
- derived object ID hash where relevant

Replay equivalence requires identical outputs for identical:

- universe identity
- GEO profile set
- input positions
- canonical local subkeys

## 11) Non-Goals

GEO-1 does not:

- implement worldgen content
- implement pathfinding
- change existing authored object IDs without migration
- introduce nondeterminism
- use wall clock

## 12) Constitutional Outcome

After GEO-1, future spatial content can target:

- infinite grids
- torus wraps
- sphere-surface atlas tiles
- volumetric galaxy cells
- minimal `R^4` partitions

through stable cell keys and stable derived object IDs that remain portable as world detail evolves.
