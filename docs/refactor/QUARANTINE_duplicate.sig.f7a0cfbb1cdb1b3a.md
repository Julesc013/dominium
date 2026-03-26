Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f7a0cfbb1cdb1b3a`

- Symbol: `_state_payload`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/process/tool_replay_capsule_window.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/pollution/tool_replay_poll_window.py`
- `tools/pollution/tool_verify_poll_mass_balance.py`
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
- `tools/system/tool_replay_capsule_window.py`
- `tools/system/tool_replay_certification_window.py`
- `tools/system/tool_replay_sys_window.py`
- `tools/system/tool_replay_system_failure_window.py`
- `tools/system/tool_replay_tier_transitions.py`
- `tools/system/tool_verify_explain_determinism.py`
- `tools/system/tool_verify_statevec_roundtrip.py`

## Scorecard

- `tools/process/tool_replay_capsule_window.py` disposition=`canonical` rank=`1` total_score=`88.33` risk=`HIGH`
- `tools/process/tool_replay_process_window.py` disposition=`drop` rank=`2` total_score=`87.8` risk=`HIGH`
- `tools/process/tool_replay_qc_window.py` disposition=`drop` rank=`3` total_score=`87.8` risk=`HIGH`
- `tools/process/tool_replay_quality_window.py` disposition=`quarantine` rank=`4` total_score=`87.8` risk=`HIGH`
- `tools/system/tool_replay_sys_window.py` disposition=`drop` rank=`5` total_score=`84.88` risk=`HIGH`
- `tools/process/tool_replay_proc_window.py` disposition=`drop` rank=`6` total_score=`83.21` risk=`HIGH`
- `tools/system/tool_replay_capsule_window.py` disposition=`quarantine` rank=`7` total_score=`81.96` risk=`HIGH`
- `tools/system/tool_replay_system_failure_window.py` disposition=`merge` rank=`8` total_score=`80.12` risk=`HIGH`
- `tools/process/tool_replay_maturity_window.py` disposition=`drop` rank=`9` total_score=`77.76` risk=`HIGH`
- `tools/process/tool_replay_drift_window.py` disposition=`drop` rank=`10` total_score=`75.89` risk=`HIGH`
- `tools/process/tool_replay_pipeline_window.py` disposition=`merge` rank=`11` total_score=`75.89` risk=`HIGH`
- `tools/pollution/tool_replay_poll_window.py` disposition=`drop` rank=`12` total_score=`74.67` risk=`HIGH`
- `tools/system/tool_replay_certification_window.py` disposition=`merge` rank=`13` total_score=`72.46` risk=`HIGH`
- `tools/process/tool_replay_experiment_window.py` disposition=`merge` rank=`14` total_score=`70.96` risk=`HIGH`
- `tools/process/tool_replay_reverse_engineering_window.py` disposition=`merge` rank=`15` total_score=`70.0` risk=`HIGH`
- `tools/process/tool_verify_proc_compaction.py` disposition=`drop` rank=`16` total_score=`68.51` risk=`HIGH`
- `tools/system/tool_replay_tier_transitions.py` disposition=`merge` rank=`17` total_score=`67.62` risk=`HIGH`
- `tools/pollution/tool_verify_poll_mass_balance.py` disposition=`merge` rank=`18` total_score=`66.05` risk=`HIGH`
- `tools/system/tool_verify_statevec_roundtrip.py` disposition=`drop` rank=`19` total_score=`65.08` risk=`HIGH`
- `tools/system/tool_verify_explain_determinism.py` disposition=`merge` rank=`20` total_score=`63.13` risk=`HIGH`

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
