Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# RepoX Scope Final Report

## Outcome

RepoX cold-path structural invalidation was narrowed to scoped groups with artifact-aware dep hashing and per-group cache reuse.

## Before vs After

- Baseline (pre-fix, `docs/audit/xstack/PROFILE_BASELINE.json`)
  - strict total: ~`779.9s`
  - `repox.core.structure`: `823676 ms`
- After fix (this pass)
  - strict cold (`gate.py strict --profile-report`): `91.50s`
  - strict warm (`gate.py strict --profile-report`): `0.031s`
  - full (`gate.py full --profile-report`): `203.25s`

## Structural Group Timing (Latest RepoX Profile)

Source: `docs/audit/repox/REPOX_PROFILE.json`

- `repox.structure.code`: `3767 ms`
- `repox.structure.schema`: `3 ms`
- `repox.structure.ruleset`: `959 ms`

All structural groups now declare:

- explicit `scope_subtrees`
- explicit `artifact_classes`
- dep hash from scoped Merkle roots with run-meta/derived exclusions and structural prefix exclusions

## Cache Verification

- Cache path: `.xstack_cache/repox/<group_id>/`
- Cache key: `group_id + input_hash`
- Reuse behavior confirmed by tests:
  - `tests/invariant/test_repox_cache_equivalence.py`
  - `tests/invariant/test_repox_dep_hash_stability_when_run_meta_changes.py`
  - `tests/invariant/test_repox_run_meta_change_does_not_trigger_structure.py`

## Remaining Heavy Groups

Cold RepoX is no longer dominated by structure. Current heavy groups are:

- `repox.runtime.policy`: `39702 ms`
- `repox.runtime.heavy_scans`: `13784 ms`

These are expected full-content policy scans and now represent the primary optimization frontier.
