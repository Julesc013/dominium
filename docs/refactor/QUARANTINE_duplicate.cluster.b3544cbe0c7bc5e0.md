Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.b3544cbe0c7bc5e0`

- Symbol: `_load_fixture`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_session_script_law_forbidden_refusal.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_session_region_budget_exceed.py`
- `tools/xstack/testx/tests/test_session_region_thread_invariance_stub.py`
- `tools/xstack/testx/tests/test_session_region_traversal_determinism.py`
- `tools/xstack/testx/tests/test_session_script_determinism.py`
- `tools/xstack/testx/tests/test_session_script_entitlement_refusal.py`
- `tools/xstack/testx/tests/test_session_script_law_forbidden_refusal.py`
- `tools/xstack/testx/tests/test_session_thread_invariance_stub.py`
- `tools/xstack/testx/tests/test_srz_hash_anchor_replay.py`
- `tools/xstack/testx/tests/test_srz_init.py`
- `tools/xstack/testx/tests/test_srz_logical_two_shard_consistency.py`
- `tools/xstack/testx/tests/test_srz_target_shard_invalid_refusal.py`
- `tools/xstack/testx/tests/test_srz_worker_invariance.py`

## Scorecard

- `tools/xstack/testx/tests/test_session_script_law_forbidden_refusal.py` disposition=`canonical` rank=`1` total_score=`80.4` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_region_budget_exceed.py` disposition=`quarantine` rank=`2` total_score=`76.45` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_script_determinism.py` disposition=`quarantine` rank=`3` total_score=`76.45` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_init.py` disposition=`quarantine` rank=`4` total_score=`76.45` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_target_shard_invalid_refusal.py` disposition=`quarantine` rank=`5` total_score=`76.45` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_script_entitlement_refusal.py` disposition=`quarantine` rank=`6` total_score=`71.24` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_region_traversal_determinism.py` disposition=`quarantine` rank=`7` total_score=`70.73` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_thread_invariance_stub.py` disposition=`drop` rank=`8` total_score=`63.58` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_worker_invariance.py` disposition=`merge` rank=`9` total_score=`62.62` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_hash_anchor_replay.py` disposition=`merge` rank=`10` total_score=`62.17` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_logical_two_shard_consistency.py` disposition=`merge` rank=`11` total_score=`61.43` risk=`HIGH`
- `tools/xstack/testx/tests/test_session_region_thread_invariance_stub.py` disposition=`drop` rank=`12` total_score=`60.98` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/setup_and_launcher.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md, docs/roadmap/milestone_lab_galaxy.md, docs/testing/xstack_profiles.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
