Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: STORE-GC
Replacement Target: release-pinned store lifecycle bundles after shared install/store transactions are hardened

# STORE-GC-0 Retro Audit

## Current Store Layout

- The current content-addressable store layout is rooted under `store/<category>/<artifact_hash>/`.
- Canonical payload types already exist for JSON payloads and tree payloads through `tools/lib/content_store.py`.
- `store.root.json` exists as the store-root marker and identity surface.

## Current Reference Surfaces

- Install manifests can point at a shared or adjacent store through `store_root_ref`.
- Instance manifests reference `pack_lock_hash`, `profile_bundle_hash`, and optional embedded artifacts.
- Save manifests reference `pack_lock_hash`.
- Pack locks already carry nested `pack_hashes`, which form the critical lock -> pack reachability edge.
- Release manifests, release indices, and bundle manifests already exist as potential reachability roots but were not yet unified into a GC reachability scan.

## Current Gaps

- No deterministic whole-store verification report existed for long-lived CAS health checks.
- No canonical reachability graph existed across installs, instances, saves, release caches, and pinned bundles.
- No GC policy registry existed.
- No quarantine-first cleanup path existed for safe unreachable-artifact cleanup.
- No setup CLI command existed for governed store GC.

## Current Risk Summary

- Growth risk: unreachable artifacts can accumulate indefinitely in shared stores.
- Integrity risk: corruption and partial writes can persist without a governed verification pass.
- Safety risk: cleanup without a reachability proof would risk deleting live artifacts.
- Portability risk: portable bundle stores need explicit protection from accidental mutation.
