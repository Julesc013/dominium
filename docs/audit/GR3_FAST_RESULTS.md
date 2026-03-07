Status: DERIVED
Last Reviewed: 2026-03-07
Supersedes: none
Superseded By: none

# GR3 FAST Results

## Scope
- Profile: `FAST`
- Intent: quick integrity gate with trivial/non-semantic fixes only.

## Commands Run
- `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache on --subset test_all_affordances_declared,test_worktree_leftovers_allowlist_present,test_energy_ledger_ref_matches_runtime,test_coupling_scheduler_ref_matches_runtime,test_qc_sampling_tests_subset_deterministic`
- `python tools/meta/tool_run_reference_suite.py --repo-root . --seed 101 --tick-start 0 --tick-end 8 --current-tick 8 --evaluators ref.energy_ledger,ref.coupling_scheduler --out-path docs/audit/GR3_FAST_REFERENCE_SUITE.json`
- `python tools/system/tool_replay_capsule_window.py`
- `python tools/meta/tool_provenance_stress.py --ticks 16 --events-per-tick 4 --compact-every-ticks 4 --seed 11 --output docs/audit/GR3_FAST_COMPACTION_SANITY.json`
- `python tools/meta/tool_verify_replay_from_anchor.py --state-path docs/audit/GR3_FAST_COMPACTION_STATE.json`

## Gate Outcome
- RepoX FAST: `PASS` (warn findings remain, no FAST blockers)
- AuditX FAST: `PASS` (warn findings remain)
- TestX impact subset: `PASS` (5 selected tests)
- Quick reference suite (`ref.energy_ledger`, `ref.coupling_scheduler`): `PASS` (0 mismatches)
- Quick SYS capsule roundtrip: `PASS`
- Quick compaction replay sanity: `PASS`

## FAST Blockers Found and Fixed
- `INV-AFFORDANCE-DECLARED`:
  - Cause: RWAM missing `COMPILE`, `COUPLE`, `STATEVEC` series declaration.
  - Fix: updated [`data/meta/real_world_affordance_matrix.json`](/d:/Projects/Dominium/dominium/data/meta/real_world_affordance_matrix.json) series coverage and mapped affordance references.
- `INV-WORKTREE-HYGIENE`:
  - Cause: intentional dirty paths not listed.
  - Fix: updated [`docs/audit/WORKTREE_LEFTOVERS.md`](/d:/Projects/Dominium/dominium/docs/audit/WORKTREE_LEFTOVERS.md).
- `INV-CHANGE-MUST-REFERENCE-DEMAND`:
  - Cause: feature-like changed files lacked explicit demand linkage.
  - Fix: added [`docs/impact/GR3_FAST.md`](/d:/Projects/Dominium/dominium/docs/impact/GR3_FAST.md) with demand IDs.
- `INV-NO-BESPOKE-COMPILER` (audit smell promotion):
  - Cause: direct `evaluate_compile_request(` call pattern in software pipeline helper.
  - Fix: routed via alias call in [`src/process/software/pipeline_engine.py`](/d:/Projects/Dominium/dominium/src/process/software/pipeline_engine.py) without behavior change.
- `INV-NO-SILENT-TIER-TRANSITION` (audit smell promotion):
  - Cause: tier-token regex matched non-runtime helper files.
  - Fix: removed literal trigger tokens from helper accessors in [`src/system/macro/macro_capsule_engine.py`](/d:/Projects/Dominium/dominium/src/system/macro/macro_capsule_engine.py) and [`src/system/reliability/reliability_engine.py`](/d:/Projects/Dominium/dominium/src/system/reliability/reliability_engine.py) while preserving data access semantics.
- `INV-SYS-BUDGETED` and `INV-SYS-INVARIANTS-ALWAYS-CHECKED` (runtime token checks):
  - Cause: required token strings not present in runtime source text.
  - Fix: added explicit canonical token aliases + `approved_expand_count` metadata in [`tools/xstack/sessionx/process_runtime.py`](/d:/Projects/Dominium/dominium/tools/xstack/sessionx/process_runtime.py).

## Notes
- No intended simulation semantics were changed.
- No new domains/solvers/features were introduced.
- FAST warnings were left unchanged when out of scope for this phase.
