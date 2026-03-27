Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5a bounded execution against v2 approved lock

# XI-5A Execution Inputs

## Required Inputs

- Approved lock: `data/restructure/src_domain_mapping_lock_approved_v2.json`
- Readiness contract: `data/restructure/xi5_readiness_contract_v2.json`
- Target path index: `data/restructure/src_domain_mapping_target_paths.json`

## Execution Contract

- Approved move rows: `769`
- Approved attic rows: `23`
- Deferred rows to leave untouched: `3`
- Xi-5a must use the explicit `source_path` and `target_path` values in the v2 lock.
- Path derivation policy: `forbidden`
- Separate validation/preflight state remains an external gate and is not changed by Xi-4z-fix1.

## Newly Deferred From V1 Approved

- `src/worldgen/__init__.py` deferred because `worldgen/__init__.py` is already occupied.
