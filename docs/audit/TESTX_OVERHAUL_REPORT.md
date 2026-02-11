Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# TestX Overhaul Report

## Implemented

- Added suite stratification registry: `testx_fast`, `testx_verify`, `testx_dist`.
- Added manifest-aware TestX proof engine runner: `scripts/dev/testx_proof_engine.py`.
- Added gate mapping updates so `gate dev/verify/dist` route to stratified TestX suite targets.
- Added proof manifest contract fields (`changed_paths`, `impacted_subsystems`, `impacted_invariants`, `required_test_tags`).
- Added determinism envelope tests:
  - `test_determinism_thread`
  - `test_determinism_srz`
  - `test_determinism_budget`
  - `test_rng_stream_consistency`
- Added derived artifact determinism tests:
  - `test_canonical_artifact_hash_stability`
  - `test_no_timestamp_in_canonical`
- Added workspace isolation proofs:
  - `test_workspace_isolation_build`
  - `test_workspace_isolation_dist`
  - `test_no_global_write`
- Added historical blocker regression locks under `tests/regression/historical_blockers/`.
- Added empty-PATH and arbitrary-CWD TestX self-containment tests:
  - `test_testx_empty_path`
  - `test_testx_arbitrary_cwd`

## Behavioral Contract

- Fast suite uses manifest-driven selection and deterministic fallback.
- Verify and dist suites preserve strict deterministic coverage expectations.
- Canonical summary output is emitted to:
  - `docs/audit/testx/TESTX_SUMMARY.json` (canonical)
  - `docs/audit/testx/TESTX_SUMMARY.md` (derived view)
  - `docs/audit/testx/TESTX_RUN_META.json` (run metadata)

## Remaining Flexibility

- Tag-to-test mappings in `data/registries/testx_suites.json` remain data-driven and extensible.
- Additional deterministic envelopes can be added without changing gate orchestration contracts.

## Risks

- Large full-suite runtime may still be substantial in `testx_verify` and `testx_dist`.
- Distribution lane coverage depends on dist prerequisites being available in the active workspace.

## Next Safe Expansions

- Expand tag mappings to include finer subsystem ownership tags.
- Add ControlX-linked proof tags once ControlX manifests are emitted in the same shape.
- Promote selected historical blocker checks into stricter CI ratchets after stability observation.
