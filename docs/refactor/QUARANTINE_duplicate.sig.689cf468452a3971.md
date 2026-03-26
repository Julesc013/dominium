Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.689cf468452a3971`

- Symbol: `REFUSAL_COMPAT_FEATURE_DISABLED`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/compat/negotiation/degrade_enforcer.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/compat/negotiation/__init__.py`
- `src/compat/negotiation/degrade_enforcer.py`

## Scorecard

- `src/compat/negotiation/degrade_enforcer.py` disposition=`canonical` rank=`1` total_score=`62.5` risk=`HIGH`
- `src/compat/negotiation/__init__.py` disposition=`quarantine` rank=`2` total_score=`60.95` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/STABILITY_CLASSIFICATION_BASELINE.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
