Status: DERIVED
Last Reviewed: 2026-03-28
Supersedes: docs/restructure/XI_5A_EXECUTION_INPUTS.md (v2 content)
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5a bounded execution against v3 approved lock

# XI-5A Execution Inputs

## Required Inputs

- Approved lock: `data/restructure/src_domain_mapping_lock_approved_v3.json`
- Readiness contract: `data/restructure/xi5_readiness_contract_v3.json`
- Target path index: `data/restructure/src_domain_mapping_target_paths_v3.json`

## Execution Contract

- Approved move rows: `769`
- Approved attic rows: `23`
- Deferred rows to leave untouched: `3`
- Path derivation policy: `forbidden`
- Xi-5a must use the explicit `source_path` and `target_path` values in the v3 lock.
- No further package-root derivation is allowed during Xi-5a.

## Collision Normalization Applied

- `platform` rebound from `src/platform/` to `engine/platform/` under `engine.platform`.
- `time` rebound from `src/time/` to `engine/time/` under `engine.time`.
