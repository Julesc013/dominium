Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: STORE-GC
Replacement Target: release-pinned store lifecycle bundles and transaction-backed shared-store cleanup after v0.0.0-mock.

# Store GC Baseline

## Policy Definitions

- `gc.aggressive`
- `gc.none`
- `gc.safe`

## Reachability Sources

- `bundle_manifest` `bundle.pinned.fixture` -> repro/ab6b2b79ced0775dc82c606e9c342b409e0e9f4140e2b1ea2c718c48eab06a0a
- `install_manifest` `install.store_gc_fixture` -> locks/262a0af7113a079d5622b0d646b726113012d0217f91609b32fbd0699e44e791, locks/c65795a71f2dd0b0703923b6e6ed4b5066b330e25532d7eb3c72847878c5560d, profiles/5d5d4ccb7379aed7c9cbd5454c11d771387f3be869f6f582714384300b46fbc5
- `instance_manifest` `instance.default` -> locks/c65795a71f2dd0b0703923b6e6ed4b5066b330e25532d7eb3c72847878c5560d, profiles/5d5d4ccb7379aed7c9cbd5454c11d771387f3be869f6f582714384300b46fbc5
- `release_index` `release.v0.0.0-mock-store_gc_fixture` -> locks/262a0af7113a079d5622b0d646b726113012d0217f91609b32fbd0699e44e791, profiles/5d5d4ccb7379aed7c9cbd5454c11d771387f3be869f6f582714384300b46fbc5
- `release_manifest` `release.v0.0.0-mock-store_gc_fixture` -> locks/262a0af7113a079d5622b0d646b726113012d0217f91609b32fbd0699e44e791, profiles/5d5d4ccb7379aed7c9cbd5454c11d771387f3be869f6f582714384300b46fbc5
- `save_manifest` `save.default` -> locks/c65795a71f2dd0b0703923b6e6ed4b5066b330e25532d7eb3c72847878c5560d

## Quarantine Behavior

- `gc.none` is report-only and does not mutate the store.
- `gc.safe` moves only unreachable artifacts into `store/quarantine/<category>/<hash>`.
- `gc.aggressive` deletes unreachable artifacts only when `--allow-aggressive` is supplied.
- Portable bundle stores refuse GC unless explicitly overridden with `--allow-portable-store`.

## Readiness

- DIST-7 packaging artifacts can include store health checks through `tool_store_verify` and `setup store gc --policy gc.none`.
- Shared installs remain protected by deterministic reachability traversal and quarantine-first cleanup in safe mode.

## Deterministic Outputs

- store_verify_fingerprint: `e1530180827d65329ddcffc3665277c82bf3c937bdd7e96f71d0a2039c869bf7`
- reachability_fingerprint: `487048911df2efcc66320b07e062b0ca5621a71b8836af7ac329651c35bbdbf3`
- gc_none_fingerprint: `978cedafa61d58a01d2b209ab962dea4a3ff01e2a4f8cbd061287b3bebaf5e8a`
- gc_safe_fingerprint: `4ae56ce92a7df0555cb0c1c384f796ff80550dfdabef7561603108988fcbb0a8`
- aggressive_refusal_code: `refusal.store.gc.explicit_flag_required`
