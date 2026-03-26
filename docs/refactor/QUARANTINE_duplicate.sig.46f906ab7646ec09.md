Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.46f906ab7646ec09`

- Symbol: `_load`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_logic_registries_valid.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_compiled_controller_io_only_without_expand.py`
- `tools/xstack/testx/tests/test_logic_policy_declared.py`
- `tools/xstack/testx/tests/test_logic_registries_valid.py`
- `tools/xstack/testx/tests/test_no_truth_leak_without_instrument.py`
- `tools/xstack/testx/tests/test_open_fault_blocks_signal.py`
- `tools/xstack/testx/tests/test_probe_requires_access.py`
- `tools/xstack/testx/tests/test_proc_contract_templates_present.py`
- `tools/xstack/testx/tests/test_proc_grammar_mappings_present.py`
- `tools/xstack/testx/tests/test_process_policies_registry_valid.py`
- `tools/xstack/testx/tests/test_replay_fault_hash_match.py`
- `tools/xstack/testx/tests/test_stuck_at_overrides_value.py`
- `tools/xstack/testx/tests/test_throttle_strategy_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_logic_registries_valid.py` disposition=`canonical` rank=`1` total_score=`72.9` risk=`HIGH`
- `tools/xstack/testx/tests/test_logic_policy_declared.py` disposition=`quarantine` rank=`2` total_score=`69.56` risk=`HIGH`
- `tools/xstack/testx/tests/test_process_policies_registry_valid.py` disposition=`quarantine` rank=`3` total_score=`67.18` risk=`HIGH`
- `tools/xstack/testx/tests/test_proc_contract_templates_present.py` disposition=`quarantine` rank=`4` total_score=`66.21` risk=`HIGH`
- `tools/xstack/testx/tests/test_proc_grammar_mappings_present.py` disposition=`quarantine` rank=`5` total_score=`65.25` risk=`HIGH`
- `tools/xstack/testx/tests/test_no_truth_leak_without_instrument.py` disposition=`quarantine` rank=`6` total_score=`65.15` risk=`HIGH`
- `tools/xstack/testx/tests/test_compiled_controller_io_only_without_expand.py` disposition=`drop` rank=`7` total_score=`61.7` risk=`HIGH`
- `tools/xstack/testx/tests/test_throttle_strategy_deterministic.py` disposition=`merge` rank=`8` total_score=`60.74` risk=`HIGH`
- `tools/xstack/testx/tests/test_probe_requires_access.py` disposition=`drop` rank=`9` total_score=`58.61` risk=`HIGH`
- `tools/xstack/testx/tests/test_replay_fault_hash_match.py` disposition=`drop` rank=`10` total_score=`56.69` risk=`HIGH`
- `tools/xstack/testx/tests/test_open_fault_blocks_signal.py` disposition=`drop` rank=`11` total_score=`55.87` risk=`HIGH`
- `tools/xstack/testx/tests/test_stuck_at_overrides_value.py` disposition=`drop` rank=`12` total_score=`53.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO_CONSTITUTION_BASELINE.md, docs/audit/INSTRUMENTATION_SURFACE_BASELINE.md, docs/audit/LOGIC_CONSTITUTION_BASELINE.md, docs/audit/MOB6_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SIGNALING_INTERLOCKING_BASELINE.md, docs/audit/SIGNAL_BUS_BASELINE.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
