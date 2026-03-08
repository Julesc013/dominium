# Metric Query Engine

Status: CANONICAL
Last Updated: 2026-03-09
Scope: GEO-3 doctrine for deterministic distance, geodesic, and neighborhood queries.

## 1) Purpose

GEO-3 freezes the canonical metric query layer used by domains to ask:

- how far apart two authoritative positions are
- what the bounded geodesic approximation is when the metric requires it
- which cells are neighbors inside a declared topology and partition

GEO-3 extends, and does not replace:

- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`

## 2) Governing Invariants

- determinism is primary
- topology and metric semantics are profile-declared, not hardcoded
- truth uses frame-resolved positions, not implicit global XYZ
- bounded approximation is lawful only when error bounds are declared and TOL-aligned
- cache hits and misses must not change authoritative outputs

## 3) Core Normative Rule

Domains do not define their own geometry law.

Authoritative distance, geodesic, and neighborhood queries must route through GEO metric APIs.

The only tolerated narrow exception is local micro physics inside a declared chart, and even there the metric law must remain a GEO-declared local-frame interpretation rather than an ad hoc world assumption.

## 4) Distance Query

### 4.1 Canonical API

`geo_distance(pos_a_ref, pos_b_ref, ...)`

Canonical behavior:

- resolve frame context through GEO-2 when position refs are supplied
- convert both positions into a deterministic comparison frame
- apply the declared `metric_profile_id`
- return a fixed-point distance value plus bounded error metadata

### 4.2 Metric profile behavior

Distance behavior varies by `MetricProfile`:

- Euclidean exact: deterministic fixed-point Euclidean distance in the resolved frame
- torus wrap exact: minimal wrapped displacement under periodic axes
- spherical geodesic stub: bounded approximation of surface arc length
- hyperbolic/custom stubs: declared placeholder algorithm with explicit bounded-error semantics

### 4.3 Output contract

Distance results must expose:

- resolved `topology_profile_id`
- resolved `metric_profile_id`
- `tolerance_policy_id`
- fixed-point distance value
- bounded error
- deterministic fingerprint

Compatibility aliases such as `distance_mm` may remain for existing callers, but the canonical semantics are “fixed-point distance plus explicit error bound”.

## 5) Geodesic Query

### 5.1 Canonical API

`geo_geodesic(pos_a_ref, pos_b_ref, ...)`

### 5.2 Rule

Geodesic queries are required when the metric is not adequately represented by direct straight-line comparison in the local frame.

Baseline GEO-3 behavior:

- spherical and atlas-backed surface profiles may return a bounded approximation
- Euclidean and torus profiles may fall back to the canonical distance result
- custom metrics may provide a declared stub until a richer solver exists

### 5.3 Approximation doctrine

Every approximate geodesic algorithm must declare:

- algorithm identifier
- worst-case error bound
- deterministic iteration or closed-form rule
- TOL policy used to quantize output

No approximation may hide its error model.

## 6) Neighborhood Enumeration

### 6.1 Canonical API

`geo_neighbors(cell_key, radius, ...)`

### 6.2 Rule

Neighborhood enumeration is a GEO query over:

- `SpaceTopologyProfile`
- `PartitionProfile`
- `MetricProfile`

The canonical neighborhood result is:

- deterministic
- ordered
- bounded by radius and policy caps
- topology-aware across wraps, seams, identified boundaries, or portal-style adjacency

### 6.3 Baseline topology behavior

- grid partitions: iterate a bounded integer offset box and filter by the metric radius
- torus partitions: apply periodic wrapping before canonical ordering
- sphere atlas partitions: use deterministic atlas tile adjacency and seam transitions
- tree or mixed partitions: use declared partition rules and explicit refinement lineage

### 6.4 Ordering

Neighbor ordering must be stable and deterministic.

Baseline ordering priority:

1. smaller metric distance
2. smaller refinement level delta
3. canonical chart id
4. canonical index tuple order

## 7) Bounded Error And TOL Discipline

### 7.1 TOL integration

Metric queries must quantize outputs through the declared `tolerance_policy_id`.

This includes:

- fixed-point rounding scale
- deterministic rounding mode
- explicit bounded error reporting

### 7.2 Exact vs bounded

`error_bound = 0` is legal only when the metric is exact at the declared output resolution.

If an internal continuous computation is quantized to fixed-point output, the quantized representation itself becomes the canonical value and any remaining error must still be surfaced explicitly when non-zero.

### 7.3 Float discipline

Floating-point intermediates may exist inside a declared deterministic algorithm, but:

- they must not leak as authoritative outputs
- outputs must be quantized before crossing the GEO boundary
- bounded error must be declared

## 8) Caching

Metric query caching is lawful only when it is observationally pure.

Cache keys must be canonical hashes of:

- topology profile id
- metric profile id
- partition profile id when neighborhood queries depend on it
- input positions or cell keys
- algorithm or policy ids
- graph version when frame conversion is involved
- engine version

Cache rules:

- cache hit/miss does not change the answer
- eviction is deterministic
- verification lanes may execute without cache to confirm purity

## 9) Domain Obligations

The following domain workloads must route through GEO-3 APIs:

- MOB pathing or movement distance heuristics
- FIELD falloff or radius-based field sampling
- POLL neighborhood iteration
- SYS ROI radius checks
- presentation LOD or topology-aware distance checks outside renderer-local raster math

Forbidden:

- direct raw Euclidean distance in domain code
- `sqrt(dx*dx + dy*dy + dz*dz)` outside GEO metric or local chart micro helpers
- hardcoded topology branches such as “if torus then wrap else Euclidean”

## 10) Proof And Replay

Proof surfaces using GEO metric queries should include:

- `topology_profile_id`
- `metric_profile_id`
- metric or geodesic policy identifiers when used
- canonical hash of representative metric outputs when relevant

Replay equivalence requires identical metric outputs for identical:

- profile sets
- frame graphs
- position refs
- cell keys
- algorithm policies

## 11) Baseline GEO-3 Outcome

After GEO-3:

- domains ask GEO for distance, geodesic, and neighborhood answers
- metric behavior changes by profile rather than code fork
- approximations are bounded, explicit, and TOL-disciplined
- deterministic caching is allowed without changing truth

This establishes the substrate required for GEO-4 field sampling and partition binding.
