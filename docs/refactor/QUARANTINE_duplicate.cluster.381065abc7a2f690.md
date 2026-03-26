Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.381065abc7a2f690`

- Symbol: `_load_rows`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_logic_contracts_present.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_fluid_contracts_present.py`
- `tools/xstack/testx/tests/test_logic_contracts_present.py`

## Scorecard

- `tools/xstack/testx/tests/test_logic_contracts_present.py` disposition=`canonical` rank=`1` total_score=`67.18` risk=`HIGH`
- `tools/xstack/testx/tests/test_fluid_contracts_present.py` disposition=`quarantine` rank=`2` total_score=`66.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/LOGIC_CONSTITUTION_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/UNITS_AND_DIMENSIONS_BASELINE.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/governance/REPOX_RULESETS.md, docs/guides/SETUP_GAPS.md, docs/specs/SPEC_DOCTRINE_AUTONOMY.md`

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
