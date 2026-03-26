Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2e65a2871c618313`

- Symbol: `_create_session`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_srz_logical_two_shard_consistency.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_srz_hash_anchor_replay.py`
- `tools/xstack/testx/tests/test_srz_logical_two_shard_consistency.py`
- `tools/xstack/testx/tests/test_srz_worker_invariance.py`

## Scorecard

- `tools/xstack/testx/tests/test_srz_logical_two_shard_consistency.py` disposition=`canonical` rank=`1` total_score=`68.35` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_hash_anchor_replay.py` disposition=`quarantine` rank=`2` total_score=`62.17` risk=`HIGH`
- `tools/xstack/testx/tests/test_srz_worker_invariance.py` disposition=`quarantine` rank=`3` total_score=`60.24` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/testing/xstack_profiles.md`

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
