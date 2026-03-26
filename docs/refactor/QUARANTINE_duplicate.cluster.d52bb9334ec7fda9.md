Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.d52bb9334ec7fda9`

- Symbol: `_parser`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/geo/tool_run_geo_stress.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/earth/tool_generate_earth_mvp_stress.py`
- `tools/earth/tool_replay_earth_physics_window.py`
- `tools/geo/tool_run_geo_stress.py`

## Scorecard

- `tools/geo/tool_run_geo_stress.py` disposition=`canonical` rank=`1` total_score=`67.55` risk=`HIGH`
- `tools/earth/tool_generate_earth_mvp_stress.py` disposition=`quarantine` rank=`2` total_score=`64.65` risk=`HIGH`
- `tools/earth/tool_replay_earth_physics_window.py` disposition=`quarantine` rank=`3` total_score=`64.65` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
