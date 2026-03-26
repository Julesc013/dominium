Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.bc3bd51adf8b5f15`

- Symbol: `REFUSAL_INTERIOR_FLOW_INVALID`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/interior/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/interior/__init__.py`
- `src/interior/compartment_flow_builder.py`

## Scorecard

- `src/interior/__init__.py` disposition=`canonical` rank=`1` total_score=`60.36` risk=`HIGH`
- `src/interior/compartment_flow_builder.py` disposition=`quarantine` rank=`2` total_score=`57.62` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CTRL8_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/NETWORKGRAPH_STANDARD_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/VALIDATION_STACK_MAP.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
