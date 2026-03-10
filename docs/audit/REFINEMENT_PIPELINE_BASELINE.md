Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Refinement Pipeline Baseline

## Scope

This baseline records the MW-4 seamless refinement pipeline after scheduler,
cache, UI trigger, and replay integration were added on top of GEO-8 worldgen.

It confirms that traversal stays nonblocking while refinement remains
contract-pinned, budgeted, cacheable, evictable, and replay-stable.

## Scheduling Rules

- Canonical work enters through `process.refinement_request_enqueue` and is
  stored as `refinement_request_record`.
- Sources are `roi`, `teleport`, `inspect`, and `path`.
- Per tick, `process.refinement_scheduler_tick` sorts requests by:
  `priority_class`, request-kind precedence, request tick, GEO cell ordering,
  refinement level, then request id.
- Under budget pressure, higher-priority work is approved first and the rest is
  deferred with `explain.refinement_deferred`.

## Cache Key Structure

MW-4 cache identity is derived from:

- `universe_identity_hash`
- `universe_contract_bundle_hash`
- `generator_version_id`
- `realism_profile_id`
- `overlay_manifest_hash`
- `mod_policy_id`
- `geo_cell_key`
- `refinement_level`

This prevents semantically stale cache reuse across contract, overlay, and mod
policy boundaries.

## Eviction Policy

- Cache entries are derived only; canonical `worldgen_result` artifacts remain
  in provenance/runtime state.
- Eviction is deterministic by refinement tier:
  LRU by canonical tick with cache-key tie-break.
- Evicted entries regenerate identically from the same pinned inputs.

## Nonblocking UI Behavior

- UI and teleport flows enqueue refinement instead of calling worldgen
  synchronously.
- Viewer state exposes `derived.refinement_status_view` plus a nonblocking
  marker and provenance-tool hook.
- Coarse views remain visible until refinement arrives.

## Stress and Replay Summary

- The rapid-teleport and ROI-thrash fixture approves only the highest-priority
  requests on the first constrained tick and leaves the remainder deferred
  deterministically.
- Replay verifies the same request ordering, refined artifacts, cache state,
  and hash chains for identical inputs.
- Proof surfaces include contract-bundle hash, overlay-manifest hash,
  mod-policy id, refinement request hash chain, refinement cache hash chain,
  and worldgen result hash chain.

## Known Stub Boundaries

- No eager galaxy or planet-wide prefetch exists.
- Cache is process-local for MVP; persistence remains on canonical results and
  overlay/save layers.
- Provenance display reuses the existing GEO-9 property-origin tooling rather
  than introducing a separate MW-4 provenance format.

## Readiness

MW-4 is ready to support:

- EMB-1 toolbelt interactions against progressively refined cells
- server and APPSHELL work that need deterministic refinement status,
  contract-pinned cache keys, and nonblocking traversal
