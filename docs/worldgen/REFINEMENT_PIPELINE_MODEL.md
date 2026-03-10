Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Refinement Pipeline Model

## 1) Purpose

MW-4 adds a deterministic, contract-pinned refinement pipeline over GEO-8
worldgen so traversal can remain seamless while refinement stays on-demand,
budgeted, cacheable, and evictable.

This document defines scheduling, cache identity, eviction, and UI-facing status
surfaces.

It does not change the meaning of worldgen refinement levels. That meaning
remains pinned by `contract.worldgen.refinement.v1`.

## 2) Refinement Levels

`contract.worldgen.refinement.v1` fixes the semantic meaning of refinement
levels:

- `L0`: galaxy-cell existence plus deterministic system-seed list
- `L1`: star-system artifacts instantiated
- `L2`: primary star plus planet prior artifacts instantiated
- `L3`: surface tiles and macro field/geometry initialization instantiated

Each level must preserve stable IDs and replay-stable artifact boundaries.

## 3) Canonical Request Sources

MW-4 introduces canonical refinement-request records. Requests may originate
from:

- `roi`
- `teleport`
- `inspect`
- `path`

These request kinds are canonical metadata only. They do not change worldgen
semantics.

## 4) Request Priority Rules

The deterministic scheduling order is:

1. teleport destination
2. current ROI cells
3. nearby ROI expansion
4. inspect or path support requests
5. background prefetch

Sorting must be deterministic by:

1. `priority_class`
2. request-kind precedence
3. canonical tick
4. semantic `geo_cell_key`
5. `request_id`

No wall-clock order is allowed.

## 5) Cache Key Contract

The refinement cache key is:

`cache_key = H(`
`  universe_identity_hash,`
`  universe_contract_bundle_hash,`
`  generator_version_id,`
`  realism_profile_id,`
`  overlay_manifest_hash,`
`  mod_policy_id,`
`  geo_cell_key,`
`  refinement_level`
`)`

The cache key must not omit semantic pins that affect replay, overlay meaning,
or mod-policy behavior.

The cache key must not depend on:

- wall clock
- thread count
- unordered iteration
- presentation-only UI state

## 6) Cache Reuse Rules

- Cache entries are derived runtime aids only.
- Canonical `worldgen_result` artifacts remain authoritative and provenance-safe.
- Cache reuse is permitted only when the full cache key matches.
- Contract, overlay, or mod-policy mismatch must refuse cache reuse and force
  regeneration.
- Such mismatches must emit `explain.contract_mismatch_cache`.

## 7) Eviction Rules

MW-4 uses deterministic eviction for derived cache entries only.

- Eviction is tiered by refinement level.
- Each level has a bounded entry cap.
- Eviction order is least-recently-used by canonical tick.
- Stable tie-break is lexicographic `cache_key`.

Eviction must never delete canonical:

- `worldgen_request` records
- `worldgen_result` records
- provenance/artifact rows
- overlay save patches

Evicted cells must regenerate identically from pinned inputs.

## 8) Degradation Under Load

Budget enforcement is deterministic.

- Scheduler work is budgeted through META-COMPUTE.
- Lower-priority refinement may be deferred under budget pressure.
- Deferral order must follow the deterministic priority rules above.
- Deferral must emit `explain.refinement_deferred`.

No UI thread or viewer shell path may block waiting for generation completion.

## 9) No-Seams Guarantee

MW-4 does not promise that every requested region is instantly refined.
It guarantees that:

- traversal and teleport stay responsive
- movement/teleport never blocks on generation
- UI shows coarse view until refined
- coarse state remains available while refinement is pending
- refinement status is exposed as a derived view surface
- canonical refinement requests are replayable
- realized artifacts remain stable once generated

## 10) UI and Provenance Surface

The UI may display:

- queued refinement levels
- resident refinement levels
- deferred refinement states
- contributing layers and property provenance for selected objects

The UI must consume derived status and provenance artifacts only.
It must not read process runtime truth directly.

## 11) Contract and Compatibility Pins

MW-4 cache reuse and replay proof must incorporate:

- `UniverseIdentity.identity_hash`
- `UniverseIdentity.universe_contract_bundle_hash`
- locked `generator_version_id`
- locked `realism_profile_id`
- `overlay_manifest_hash`
- `mod_policy_id`

Forward and backward compatibility remain governed by CompatX semantic-contract
pinning. Cache reuse across incompatible semantic pins is forbidden.
