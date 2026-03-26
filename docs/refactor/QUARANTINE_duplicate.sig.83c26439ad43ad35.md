Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.83c26439ad43ad35`

- Symbol: `_hash_chains`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/time/tool_replay_time_window.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/chem/tool_replay_combustion_window.py`
- `tools/chem/tool_replay_degradation_window.py`
- `tools/chem/tool_replay_process_run.py`
- `tools/time/tool_replay_time_window.py`

## Scorecard

- `tools/time/tool_replay_time_window.py` disposition=`canonical` rank=`1` total_score=`67.01` risk=`HIGH`
- `tools/chem/tool_replay_degradation_window.py` disposition=`quarantine` rank=`2` total_score=`65.69` risk=`HIGH`
- `tools/chem/tool_replay_process_run.py` disposition=`quarantine` rank=`3` total_score=`65.69` risk=`HIGH`
- `tools/chem/tool_replay_combustion_window.py` disposition=`quarantine` rank=`4` total_score=`64.19` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md, docs/archive/stray_root_docs/CI_ENFORCEMENT_MATRIX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/LOGIC_PROTOCOL_BASELINE.md, docs/audit/LOGIC_TIMING_BASELINE.md, docs/audit/REPO_TREE_INDEX.md`

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
