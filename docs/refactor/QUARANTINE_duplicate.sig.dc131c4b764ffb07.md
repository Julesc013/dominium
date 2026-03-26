Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.dc131c4b764ffb07`

- Symbol: `_schema_paths`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/auditx/analyzers/e107_undeclared_schema_smell.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/auditx/analyzers/e107_undeclared_schema_smell.py`
- `tools/xstack/testx/tests/test_topology_map_includes_all_schemas.py`

## Scorecard

- `tools/auditx/analyzers/e107_undeclared_schema_smell.py` disposition=`canonical` rank=`1` total_score=`64.65` risk=`HIGH`
- `tools/xstack/testx/tests/test_topology_map_includes_all_schemas.py` disposition=`quarantine` rank=`2` total_score=`64.19` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/TOPOLOGY_MAP_BASELINE.md, docs/audit/VALIDATION_STACK_MAP.md`

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
