Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.56d24d16c4730f3d`

- Symbol: `_seed_embodied_agent`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_cross_shard_move_handling.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_cross_shard_move_handling.py`
- `tools/xstack/testx/tests/test_movement_anti_cheat_event.py`

## Scorecard

- `tools/xstack/testx/tests/test_cross_shard_move_handling.py` disposition=`canonical` rank=`1` total_score=`63.12` risk=`HIGH`
- `tools/xstack/testx/tests/test_movement_anti_cheat_event.py` disposition=`quarantine` rank=`2` total_score=`60.63` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

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
