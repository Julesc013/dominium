Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.68af9cf2cec36339`

- Symbol: `_read_topology`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/auditx/analyzers/e129_control_plane_bypass_smell.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/auditx/analyzers/e106_undeclared_subsystem_smell.py`
- `tools/auditx/analyzers/e107_undeclared_schema_smell.py`
- `tools/auditx/analyzers/e108_undeclared_registry_smell.py`
- `tools/auditx/analyzers/e129_control_plane_bypass_smell.py`
- `tools/auditx/analyzers/e130_hidden_privilege_escalation_smell.py`
- `tools/auditx/analyzers/e131_silent_downgrade_smell.py`
- `tools/auditx/analyzers/e132_missing_decision_log_smell.py`

## Scorecard

- `tools/auditx/analyzers/e129_control_plane_bypass_smell.py` disposition=`canonical` rank=`1` total_score=`64.65` risk=`HIGH`
- `tools/auditx/analyzers/e106_undeclared_subsystem_smell.py` disposition=`quarantine` rank=`2` total_score=`63.69` risk=`HIGH`
- `tools/auditx/analyzers/e107_undeclared_schema_smell.py` disposition=`quarantine` rank=`3` total_score=`63.69` risk=`HIGH`
- `tools/auditx/analyzers/e108_undeclared_registry_smell.py` disposition=`quarantine` rank=`4` total_score=`63.69` risk=`HIGH`
- `tools/auditx/analyzers/e130_hidden_privilege_escalation_smell.py` disposition=`quarantine` rank=`5` total_score=`63.69` risk=`HIGH`
- `tools/auditx/analyzers/e131_silent_downgrade_smell.py` disposition=`quarantine` rank=`6` total_score=`63.69` risk=`HIGH`
- `tools/auditx/analyzers/e132_missing_decision_log_smell.py` disposition=`quarantine` rank=`7` total_score=`63.69` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

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
