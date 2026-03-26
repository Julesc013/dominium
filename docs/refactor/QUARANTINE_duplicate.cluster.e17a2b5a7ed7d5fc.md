Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e17a2b5a7ed7d5fc`

- Symbol: `overlay_effective_object_hash_chain`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/overlay/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/overlay/__init__.py`
- `src/geo/overlay/overlay_merge_engine.py`

## Scorecard

- `src/geo/overlay/__init__.py` disposition=`canonical` rank=`1` total_score=`70.48` risk=`HIGH`
- `src/geo/overlay/overlay_merge_engine.py` disposition=`quarantine` rank=`2` total_score=`63.87` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/OVERLAY_MERGE_BASELINE.md, docs/geo/OVERLAY_MERGE_CONSTITUTION.md, docs/geo/WORLDGEN_CONSTITUTION.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
