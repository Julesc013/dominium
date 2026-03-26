Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7a39eba86cdb2f32`

- Symbol: `_write_contract`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/invariant/test_repox_run_meta_change_does_not_trigger_structure.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/invariant/test_repox_dep_hash_stability_when_run_meta_changes.py`
- `tests/invariant/test_repox_run_meta_change_does_not_trigger_structure.py`

## Scorecard

- `tests/invariant/test_repox_run_meta_change_does_not_trigger_structure.py` disposition=`canonical` rank=`1` total_score=`61.21` risk=`HIGH`
- `tests/invariant/test_repox_dep_hash_stability_when_run_meta_changes.py` disposition=`quarantine` rank=`2` total_score=`53.69` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO_FRAMES_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PERFORMANCE_CONSTITUTION_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SIGNAL_BUS_BASELINE.md, docs/audit/UNIVERSE_PHYSICS_PROFILE_BASELINE.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
