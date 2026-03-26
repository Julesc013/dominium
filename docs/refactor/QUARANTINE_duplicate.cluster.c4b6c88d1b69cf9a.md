Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.c4b6c88d1b69cf9a`

- Symbol: `canonicalize_governance_mode_row`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/governance/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/governance/__init__.py`
- `src/governance/governance_profile.py`

## Scorecard

- `src/governance/__init__.py` disposition=`canonical` rank=`1` total_score=`64.76` risk=`HIGH`
- `src/governance/governance_profile.py` disposition=`quarantine` rank=`2` total_score=`59.58` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/audit/GEO_METRIC_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/GATE_AUTONOMY_POLICY.md, docs/governance/REPOX_TOOL_RULES.md`

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
