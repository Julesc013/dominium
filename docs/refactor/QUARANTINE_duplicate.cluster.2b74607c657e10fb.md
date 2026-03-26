Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.2b74607c657e10fb`

- Symbol: `_load`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_logic_registries_valid.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_logic_policy_declared.py`
- `tools/xstack/testx/tests/test_logic_registries_valid.py`
- `tools/xstack/testx/tests/test_proc_contract_templates_present.py`
- `tools/xstack/testx/tests/test_proc_grammar_mappings_present.py`
- `tools/xstack/testx/tests/test_process_policies_registry_valid.py`

## Scorecard

- `tools/xstack/testx/tests/test_logic_registries_valid.py` disposition=`canonical` rank=`1` total_score=`72.9` risk=`HIGH`
- `tools/xstack/testx/tests/test_logic_policy_declared.py` disposition=`quarantine` rank=`2` total_score=`69.56` risk=`HIGH`
- `tools/xstack/testx/tests/test_process_policies_registry_valid.py` disposition=`quarantine` rank=`3` total_score=`67.18` risk=`HIGH`
- `tools/xstack/testx/tests/test_proc_contract_templates_present.py` disposition=`quarantine` rank=`4` total_score=`66.21` risk=`HIGH`
- `tools/xstack/testx/tests/test_proc_grammar_mappings_present.py` disposition=`quarantine` rank=`5` total_score=`65.25` risk=`HIGH`

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

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
