Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Geometry And Topology Constitution

Status: CANONICAL
Last Updated: 2026-03-08
Scope: GEO-0 constitutional contract for topology, metric, partition, and projection behavior.

## 1) Purpose

Freeze a deterministic geometry kernel so all present and future domains can operate across:

- arbitrary dimension `D`
- nontrivial topology
- metric variation
- multiple partitioning strategies
- projection and slice lenses

This constitution defines substrate contracts only. It does not implement world generation, pathfinding, or geometry editing.

## 2) Constitutional Dependencies

- `docs/canon/constitution_v1.md` A1 Determinism is primary
- `docs/canon/constitution_v1.md` A4 No runtime mode flags
- `docs/canon/constitution_v1.md` A7 Observer-Renderer-Truth separation
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` E2 Deterministic ordering
- `docs/canon/constitution_v1.md` E5 Thread-count invariance
- `docs/canon/constitution_v1.md` E6 Replay equivalence
- `docs/canon/constitution_v1.md` E7 Hash-partition equivalence
- `docs/canon/constitution_v1.md` C1 Version semantics
- `docs/canon/constitution_v1.md` C2 Skip-unknown preservation
- `docs/canon/glossary_v1.md` Space
- `docs/canon/glossary_v1.md` Lens
- `docs/canon/glossary_v1.md` PerceivedModel
- `docs/canon/glossary_v1.md` Shard

## 3) Core Normative Rule

Authoritative space is not an implicit coordinate convention.

Authoritative space is the composition of:

1. `SpaceTopologyProfile`
2. `MetricProfile`
3. `GeometryPartitionProfile`
4. `ProjectionProfile`

All authoritative domain logic that depends on:

- neighbors
- adjacency
- distances
- chart transforms
- partition keys
- projection requests

must route through GEO APIs or a local chart-declared micro-physics exception.

## 4) SpaceTopologyProfile

`SpaceTopologyProfile` defines the lawful topology of a universe or declared subspace.

### 4.1 Required semantics

Every `SpaceTopologyProfile` must declare:

- dimension `D`, where `D in {1, 2, 3, 4, ...}`
- one or more charts
- deterministic chart identifiers
- deterministic transforms between charts
- boundary rule semantics
- neighborhood policy semantics
- deterministic fingerprint

### 4.2 Coordinate atlas

Topology is represented as a coordinate atlas:

- one chart is legal for globally simple spaces
- multiple charts are legal for atlas-driven, spherical, identified, or higher-dimensional spaces
- transforms between charts must be deterministic pure functions of input coordinate plus profile parameters

Chart transforms must not depend on:

- wall clock
- thread count
- mutable cache state
- hidden renderer-only state

### 4.3 Boundary rules

The following boundary rule families are constitutional:

- infinite
- finite walls
- periodic wrap
- reflective
- identified faces or edges
- portal identifications modeled as deterministic graph edges

Boundary behavior is topology law, not domain-local ad hoc code.

### 4.4 Neighborhood function

`SpaceTopologyProfile` must define a neighborhood function:

`neighbor(cell_key, radius, policy) -> ordered cell_keys`

Requirements:

- deterministic ordering
- explicit radius semantics
- bounded enumeration
- topology-aware adjacency across wraps, identified edges, atlas seams, or portal links

Neighbor enumeration is authoritative input for domains such as:

- FIELD
- POLL
- FLUID
- THERM
- future path/ROI/indexing systems

## 5) MetricProfile

`MetricProfile` defines how separation and measure are computed over a topology.

### 5.1 Required queries

Every `MetricProfile` must provide deterministic evaluation for:

- `dist(a, b)`
- optional `geodesic(a, b)` approximation
- measure elements such as area or volume weighting where relevant

### 5.2 Allowed metric families

The constitutional baseline allows:

- Euclidean
- spherical geodesic
- torus wrap metric
- hyperbolic placeholder
- custom deterministic metric

### 5.3 Error bounds

Any approximate metric or geodesic routine must declare:

- bounded error
- tolerance policy identifier
- deterministic approximation algorithm

Approximation is legal only when:

- the algorithm is deterministic
- the bound is data-declared
- the tolerance policy is explicit
- replay/hash equivalence is preserved

### 5.4 Measure elements

Densities and field laws may require a measure element:

- length element in `D=1`
- area element in surface spaces
- volume element in volumetric spaces
- chart-weighted local measure in mixed atlas spaces

Measure semantics must be profile-declared and bounded.

## 6) GeometryPartitionProfile

`GeometryPartitionProfile` defines how authoritative space is partitioned for storage, sampling, sharding, and activation.

### 6.1 Required use cases

Partition profiles govern:

- field grids
- on-demand world cells
- ROI refinement
- shard-facing boundary artifacts
- stable cell-key generation

### 6.2 Allowed partition families

The constitutional baseline allows:

- `grid Z^D`
- `quadtree`
- `octree`
- sphere tiling such as icosahedral or atlas tiles
- mixed atlas partitions

### 6.3 Rules

Partitioning must be:

- deterministic
- stable for identical profile inputs
- explicit about resolution and subdivision rules
- suitable for hashable cell keys

Partition selection must not be hardwired by runtime mode branches.

## 7) ProjectionProfile

`ProjectionProfile` defines lawful mappings from authoritative coordinates to render-oriented coordinate spaces.

### 7.1 Projection kinds

The constitutional baseline allows:

- orthographic map projections
- perspective camera projections
- atlas unwraps
- slice and cross-section projections for `N -> M` views such as `4D -> 3D -> 2D`

### 7.2 Lens rule

Projection is a Lens request, not a truth mutation.

Therefore:

- projection outputs are observational or presentational artifacts
- projection may be filtered by law, authority, and instrumentation
- projection must not mutate authoritative topology, metric, or truth state

### 7.3 Epistemic gating

Projection requests must be gated through Lens and instrumentation policy:

- diegetic instruments may expose limited projections
- non-diegetic tools may expose broader projections only under explicit law/profile permission
- hidden truth leakage through projection shortcuts is forbidden

## 8) GEO API Obligation For Domains

Domains must not embed global coordinate assumptions beyond local micro physics within a declared chart.

The following categories must use GEO APIs:

- neighbor iteration
- distance queries
- coordinate transforms
- projection requests
- partition-derived cell addressing

Allowed narrow exception:

- local micro physics inside a declared chart may operate in local chart coordinates for bounded integration
- such local computation must not redefine topology, global adjacency, or cross-chart metrics

## 9) Determinism And Caching

All GEO queries must be:

- deterministic
- pure functions of inputs plus profile parameters
- cacheable by canonical hash

Cache rules:

- cache hit/miss must not change authoritative outputs
- cache keys must be canonical and deterministic
- cache content must be derivable from query inputs only

Approximate routines are lawful only when:

- algorithm choice is explicit
- error bound is explicit
- ordering is deterministic
- tolerance policy is explicit

## 10) Sharding And Boundary Artifacts

Cross-shard geometry must not rely on direct cross-shard reads.

Authoritative cross-shard adjacency or metric evaluation must use:

- shard-safe boundary artifacts
- deterministic boundary summaries
- explicit handoff contracts

Rules:

- no direct remote shard truth reads for neighbor lookup
- no direct remote shard truth reads for metric correction
- no hidden portal/cross-face shortcuts that bypass SRZ contracts

## 11) META-PROFILE Integration

GEO behavior composition must use profiles, not mode flags.

### 11.1 Baseline binding

`UniverseIdentity` declares the default GEO profile set:

- `topology_profile_id`
- `metric_profile_id`
- `partition_profile_id`
- default `projection_profile_id`

### 11.2 Overrides

`SessionSpec` may override GEO bindings only through explicit profile bindings under the unified profile system.

### 11.3 Invariant break handling

If an override breaks immutable lineage invariants, runtime must:

- refuse or log the override deterministically
- emit canonical `exception_event` when required by policy

Changing dimension mid-session is invariant-breaking unless explicitly allowed by a lawful transition contract.

## 12) Pack-Driven Integration

Topologies, metrics, partitions, and projections are integrated via registries and packs.

Rules:

- no hardwired mandatory topology beyond selected defaults
- missing optional GEO content must refuse or degrade deterministically
- profile IDs remain registry-addressable

## 13) Non-Goals

GEO-0 does not:

- implement world generation
- implement pathfinding
- implement geometry editing
- introduce nondeterminism
- use wall clock
- make any one topology mandatory

## 14) Constitutional Outcome

After GEO-0, universes may lawfully express:

- infinite Euclidean `R^3`
- flat `R^2` factory maps
- torus worlds
- sphere-surface atlas worlds
- portal-identified cube spaces
- minimal `R^4` slice spaces
- authored atlas maps

without forcing domain-local rewrites of distance, neighbor, partition, or projection semantics.
