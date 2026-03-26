Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7442b938bc1ad883`

- Symbol: `_ensure_repo_root`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/earth5_testlib.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/astro/sol2_runtime_common.py`
- `tools/embodiment/emb2_probe.py`
- `tools/server/server_mvp0_probe.py`
- `tools/server/server_mvp1_probe.py`
- `tools/xstack/testx/tests/earth0_testlib.py`
- `tools/xstack/testx/tests/earth10_testlib.py`
- `tools/xstack/testx/tests/earth1_testlib.py`
- `tools/xstack/testx/tests/earth2_testlib.py`
- `tools/xstack/testx/tests/earth3_testlib.py`
- `tools/xstack/testx/tests/earth4_testlib.py`
- `tools/xstack/testx/tests/earth5_testlib.py`
- `tools/xstack/testx/tests/earth6_testlib.py`
- `tools/xstack/testx/tests/earth7_testlib.py`
- `tools/xstack/testx/tests/earth8_testlib.py`
- `tools/xstack/testx/tests/earth9_testlib.py`
- `tools/xstack/testx/tests/emb2_testlib.py`
- `tools/xstack/testx/tests/gal0_testlib.py`
- `tools/xstack/testx/tests/gal1_testlib.py`
- `tools/xstack/testx/tests/geo10_testlib.py`
- `tools/xstack/testx/tests/mw3_testlib.py`
- `tools/xstack/testx/tests/mw4_testlib.py`
- `tools/xstack/testx/tests/sol0_testlib.py`
- `tools/xstack/testx/tests/sol2_testlib.py`
- `tools/xstack/testx/tests/ux0_testlib.py`

## Scorecard

- `tools/xstack/testx/tests/earth5_testlib.py` disposition=`canonical` rank=`1` total_score=`87.36` risk=`HIGH`
- `tools/xstack/testx/tests/earth9_testlib.py` disposition=`quarantine` rank=`2` total_score=`85.32` risk=`HIGH`
- `tools/xstack/testx/tests/earth0_testlib.py` disposition=`quarantine` rank=`3` total_score=`85.3` risk=`HIGH`
- `tools/xstack/testx/tests/earth4_testlib.py` disposition=`quarantine` rank=`4` total_score=`84.36` risk=`HIGH`
- `tools/xstack/testx/tests/earth6_testlib.py` disposition=`quarantine` rank=`5` total_score=`83.37` risk=`HIGH`
- `tools/xstack/testx/tests/emb2_testlib.py` disposition=`quarantine` rank=`6` total_score=`82.4` risk=`HIGH`
- `tools/xstack/testx/tests/geo10_testlib.py` disposition=`quarantine` rank=`7` total_score=`81.64` risk=`HIGH`
- `tools/xstack/testx/tests/earth1_testlib.py` disposition=`quarantine` rank=`8` total_score=`81.44` risk=`HIGH`
- `tools/xstack/testx/tests/earth2_testlib.py` disposition=`quarantine` rank=`9` total_score=`81.44` risk=`HIGH`
- `tools/xstack/testx/tests/earth3_testlib.py` disposition=`quarantine` rank=`10` total_score=`81.44` risk=`HIGH`
- `tools/xstack/testx/tests/earth7_testlib.py` disposition=`quarantine` rank=`11` total_score=`81.44` risk=`HIGH`
- `tools/xstack/testx/tests/earth8_testlib.py` disposition=`quarantine` rank=`12` total_score=`80.47` risk=`HIGH`
- `tools/xstack/testx/tests/earth10_testlib.py` disposition=`quarantine` rank=`13` total_score=`79.71` risk=`HIGH`
- `tools/xstack/testx/tests/gal1_testlib.py` disposition=`quarantine` rank=`14` total_score=`79.71` risk=`HIGH`
- `tools/xstack/testx/tests/sol2_testlib.py` disposition=`quarantine` rank=`15` total_score=`79.71` risk=`HIGH`
- `tools/xstack/testx/tests/gal0_testlib.py` disposition=`merge` rank=`16` total_score=`75.83` risk=`HIGH`
- `tools/xstack/testx/tests/sol0_testlib.py` disposition=`merge` rank=`17` total_score=`73.0` risk=`HIGH`
- `tools/xstack/testx/tests/mw3_testlib.py` disposition=`drop` rank=`18` total_score=`72.98` risk=`HIGH`
- `tools/xstack/testx/tests/mw4_testlib.py` disposition=`merge` rank=`19` total_score=`72.54` risk=`HIGH`
- `tools/embodiment/emb2_probe.py` disposition=`drop` rank=`20` total_score=`70.4` risk=`HIGH`
- `tools/server/server_mvp0_probe.py` disposition=`drop` rank=`21` total_score=`70.08` risk=`HIGH`
- `tools/server/server_mvp1_probe.py` disposition=`drop` rank=`22` total_score=`67.31` risk=`HIGH`
- `tools/astro/sol2_runtime_common.py` disposition=`merge` rank=`23` total_score=`61.48` risk=`HIGH`
- `tools/xstack/testx/tests/ux0_testlib.py` disposition=`merge` rank=`24` total_score=`61.17` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

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
