Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2aa9d1b9512fecf8`

- Symbol: `dg_budget_set_limits`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/execution/budgets/dg_budget.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/execution/budgets/dg_budget.c`
- `engine/modules/execution/budgets/dg_budget.h`

## Scorecard

- `engine/modules/execution/budgets/dg_budget.h` disposition=`canonical` rank=`1` total_score=`76.02` risk=`HIGH`
- `engine/modules/execution/budgets/dg_budget.c` disposition=`quarantine` rank=`2` total_score=`73.38` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md, docs/architecture/LAW_AND_META_LAW.md, docs/audit/GR3_PERFORMANCE_TUNING.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/worldgen/REFINEMENT_CONTRACT.md`

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
