Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MW4 Retro Audit

## Scope

This audit records the pre-MW-4 refinement/runtime state so the seamless traversal
pipeline can be added without silently changing GEO-8 worldgen semantics.

## Current GEO-8 Worldgen Request Flow

- Authoritative generation still enters through `process.worldgen_request` in
  `tools/xstack/sessionx/process_runtime.py`.
- The process normalizes a canonical `worldgen_request`, appends it to
  `state["worldgen_requests"]`, and immediately calls
  `src/geo/worldgen/worldgen_engine.py::generate_worldgen_result(...)`.
- `generate_worldgen_result(...)` already respects locked
  `generator_version_id` and `realism_profile_id`, emits stable object/artifact
  rows for refinement `L0` through `L3`, and returns deterministic
  `worldgen_result` payloads.
- Worldgen results are persisted into canonical/provenance state via
  `_append_worldgen_result(...)`; field and geometry initializations are also
  applied there.

## Current Caching Behavior

- `src/geo/worldgen/worldgen_engine.py` maintains an in-memory process-local
  `_WORLDGEN_CACHE`.
- The current cache key is internal to GEO-8 and is based on:
  - universe seed
  - semantic GEO cell key
  - refinement level
  - generator version
  - realism profile
  - current tick
  - request extensions
- This cache is deterministic for repeated identical calls, but it is not yet
  pinned to:
  - universe contract bundle hash
  - overlay manifest hash
  - mod policy id
- Eviction is currently simple bounded dictionary truncation rather than an
  explicit deterministic per-level LRU policy.

## Current Request Sources

### Teleport

- `src/client/ui/teleport_controller.py` currently emits
  `process.worldgen_request` directly before `process.camera_teleport` for Sol
  and random-star flows.
- This ensures destination generation is requested, but it still models the
  refinement path as an immediate process execution rather than a queued
  nonblocking pipeline.

### ROI / Map / Viewer

- `src/client/ui/map_views.py` builds projection requests whose extensions
  already carry:
  - `worldgen_refinement_level`
  - `worldgen_reason = "roi"`
- The map/view layer currently derives projected cells, but it does not persist
  a separate canonical refinement-request queue.
- `src/client/ui/viewer_shell.py` consumes derived view artifacts and water/sky
  layers correctly, but it does not yet expose:
  - refinement status
  - deferred/refused refinement explanations
  - deterministic provenance for cache reuse/deferral

### Inspect / Query / Pathing

- Query and inspect surfaces already call GEO/MW helpers, but they do not share
  a dedicated MW-4 scheduler queue.
- Pathing-driven refinement hooks are not yet represented as canonical
  refinement-request records.

## Current Blocking Risk

- `process.worldgen_request` performs generation inline in the authoritative
  process path.
- Teleport/view code can therefore describe the correct generation target, but
  there is no explicit queued scheduler layer that guarantees nonblocking
  traversal semantics for UI-facing flows.
- The primary MW-4 integration point is therefore above the existing
  `process.worldgen_request` branch, not inside the generator algorithms.

## Existing Semantic / Contract Pins Available

- Session and runtime surfaces already carry:
  - `contract_bundle_hash`
  - `semantic_contract_registry_hash`
  - `mod_policy_id`
  - `overlay_manifest_hash`
- `UniverseIdentity` already carries `universe_contract_bundle_hash`.
- This means MW-4 can add contract-aware cache keys and reuse/refusal logic
  without changing the meaning of refinement levels.

## Minimum Safe MW-4 Integration Points

- Add canonical `refinement_request_record` rows rather than changing the
  meaning of `worldgen_request`.
- Add a deterministic scheduler that decides when to invoke the existing
  authoritative `process.worldgen_request` logic.
- Add a derived refinement cache keyed by:
  - universe identity hash
  - universe contract bundle hash
  - generator version
  - realism profile
  - overlay manifest hash
  - mod policy id
  - GEO cell key
  - refinement level
- Add viewer-shell status surfaces so UI can show coarse state plus queued or
  deferred refinement status instead of assuming immediate realization.

## Retrofit Conclusion

MW-4 can be implemented as a deterministic scheduling/cache/status layer over
the existing GEO-8 process-only mutation path. No worldgen algorithm rewrite is
required; the main work is:

- canonical request queueing
- derived cache key hardening
- deterministic eviction
- nonblocking ROI/teleport/view integration
- proof, replay, and enforcement updates
