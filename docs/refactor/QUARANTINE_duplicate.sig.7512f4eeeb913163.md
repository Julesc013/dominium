Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7512f4eeeb913163`

- Symbol: `DEFAULT_SCENARIO_REL`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/earth/earth9_stress_common.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/earth/earth9_stress_common.py`
- `tools/lib/lib_stress_common.py`
- `tools/mvp/mvp_smoke_common.py`

## Scorecard

- `tools/earth/earth9_stress_common.py` disposition=`canonical` rank=`1` total_score=`73.62` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`2` total_score=`72.26` risk=`HIGH`
- `tools/lib/lib_stress_common.py` disposition=`quarantine` rank=`3` total_score=`68.24` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
