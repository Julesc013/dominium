Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.0f48fd0c64543a54`

- Symbol: `_state_payload`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/process/tool_replay_capsule_window.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/process/tool_replay_capsule_window.py`
- `tools/process/tool_replay_drift_window.py`
- `tools/process/tool_replay_experiment_window.py`
- `tools/process/tool_replay_maturity_window.py`
- `tools/process/tool_replay_pipeline_window.py`
- `tools/process/tool_replay_proc_window.py`
- `tools/process/tool_replay_process_window.py`
- `tools/process/tool_replay_qc_window.py`
- `tools/process/tool_replay_quality_window.py`
- `tools/process/tool_replay_reverse_engineering_window.py`
- `tools/process/tool_verify_proc_compaction.py`

## Scorecard

- `tools/process/tool_replay_capsule_window.py` disposition=`canonical` rank=`1` total_score=`88.33` risk=`HIGH`
- `tools/process/tool_replay_process_window.py` disposition=`drop` rank=`2` total_score=`87.8` risk=`HIGH`
- `tools/process/tool_replay_qc_window.py` disposition=`drop` rank=`3` total_score=`87.8` risk=`HIGH`
- `tools/process/tool_replay_quality_window.py` disposition=`quarantine` rank=`4` total_score=`87.8` risk=`HIGH`
- `tools/process/tool_replay_proc_window.py` disposition=`drop` rank=`5` total_score=`83.21` risk=`HIGH`
- `tools/process/tool_replay_maturity_window.py` disposition=`drop` rank=`6` total_score=`77.76` risk=`HIGH`
- `tools/process/tool_replay_drift_window.py` disposition=`drop` rank=`7` total_score=`75.89` risk=`HIGH`
- `tools/process/tool_replay_pipeline_window.py` disposition=`merge` rank=`8` total_score=`75.89` risk=`HIGH`
- `tools/process/tool_replay_experiment_window.py` disposition=`merge` rank=`9` total_score=`70.96` risk=`HIGH`
- `tools/process/tool_replay_reverse_engineering_window.py` disposition=`merge` rank=`10` total_score=`70.0` risk=`HIGH`
- `tools/process/tool_verify_proc_compaction.py` disposition=`drop` rank=`11` total_score=`68.51` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/LOCKLIST.md, docs/architecture/RISK_AND_LIABILITY_MODEL.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
