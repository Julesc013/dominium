Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9972af258ab5a406`

- Symbol: `ensure_repo_on_path`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/cap_neg_testlib.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/appshell0_testlib.py`
- `tools/xstack/testx/tests/appshell1_testlib.py`
- `tools/xstack/testx/tests/appshell2_testlib.py`
- `tools/xstack/testx/tests/appshell3_testlib.py`
- `tools/xstack/testx/tests/appshell4_testlib.py`
- `tools/xstack/testx/tests/appshell6_testlib.py`
- `tools/xstack/testx/tests/cap_neg1_testlib.py`
- `tools/xstack/testx/tests/cap_neg4_testlib.py`
- `tools/xstack/testx/tests/cap_neg_testlib.py`
- `tools/xstack/testx/tests/compat_sem2_testlib.py`
- `tools/xstack/testx/tests/diag0_testlib.py`
- `tools/xstack/testx/tests/ipc_unify_testlib.py`
- `tools/xstack/testx/tests/mod_policy0_testlib.py`
- `tools/xstack/testx/tests/pack_compat0_testlib.py`
- `tools/xstack/testx/tests/pack_compat2_testlib.py`
- `tools/xstack/testx/tests/server_mvp0_testlib.py`
- `tools/xstack/testx/tests/server_mvp1_testlib.py`
- `tools/xstack/testx/tests/ui_reconcile_testlib.py`

## Scorecard

- `tools/xstack/testx/tests/cap_neg_testlib.py` disposition=`canonical` rank=`1` total_score=`90.48` risk=`HIGH`
- `tools/xstack/testx/tests/appshell4_testlib.py` disposition=`quarantine` rank=`2` total_score=`89.28` risk=`HIGH`
- `tools/xstack/testx/tests/appshell2_testlib.py` disposition=`quarantine` rank=`3` total_score=`87.88` risk=`HIGH`
- `tools/xstack/testx/tests/server_mvp0_testlib.py` disposition=`quarantine` rank=`4` total_score=`86.82` risk=`HIGH`
- `tools/xstack/testx/tests/cap_neg1_testlib.py` disposition=`quarantine` rank=`5` total_score=`85.02` risk=`HIGH`
- `tools/xstack/testx/tests/appshell6_testlib.py` disposition=`quarantine` rank=`6` total_score=`84.27` risk=`HIGH`
- `tools/xstack/testx/tests/appshell0_testlib.py` disposition=`quarantine` rank=`7` total_score=`83.91` risk=`HIGH`
- `tools/xstack/testx/tests/compat_sem2_testlib.py` disposition=`quarantine` rank=`8` total_score=`83.69` risk=`HIGH`
- `tools/xstack/testx/tests/appshell3_testlib.py` disposition=`quarantine` rank=`9` total_score=`81.67` risk=`HIGH`
- `tools/xstack/testx/tests/diag0_testlib.py` disposition=`merge` rank=`10` total_score=`80.31` risk=`HIGH`
- `tools/xstack/testx/tests/cap_neg4_testlib.py` disposition=`drop` rank=`11` total_score=`79.18` risk=`HIGH`
- `tools/xstack/testx/tests/pack_compat2_testlib.py` disposition=`merge` rank=`12` total_score=`77.62` risk=`HIGH`
- `tools/xstack/testx/tests/appshell1_testlib.py` disposition=`drop` rank=`13` total_score=`77.02` risk=`HIGH`
- `tools/xstack/testx/tests/server_mvp1_testlib.py` disposition=`merge` rank=`14` total_score=`76.43` risk=`HIGH`
- `tools/xstack/testx/tests/pack_compat0_testlib.py` disposition=`merge` rank=`15` total_score=`76.19` risk=`HIGH`
- `tools/xstack/testx/tests/mod_policy0_testlib.py` disposition=`merge` rank=`16` total_score=`75.0` risk=`HIGH`
- `tools/xstack/testx/tests/ipc_unify_testlib.py` disposition=`drop` rank=`17` total_score=`68.89` risk=`HIGH`
- `tools/xstack/testx/tests/ui_reconcile_testlib.py` disposition=`merge` rank=`18` total_score=`68.45` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/VALIDATION_STACK_MAP.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
