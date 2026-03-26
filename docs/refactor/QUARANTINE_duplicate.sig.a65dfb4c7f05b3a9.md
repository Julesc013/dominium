Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a65dfb4c7f05b3a9`

- Symbol: `make_task`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/tests/execution_scheduler_law_tests.cpp`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/tests/execution_contract_tests.cpp`
- `engine/tests/execution_scheduler_law_tests.cpp`

## Scorecard

- `engine/tests/execution_scheduler_law_tests.cpp` disposition=`canonical` rank=`1` total_score=`67.19` risk=`HIGH`
- `engine/tests/execution_contract_tests.cpp` disposition=`quarantine` rank=`2` total_score=`61.08` risk=`HIGH`

## Usage Sites

- Build Targets: `execution_scheduler_law_tests`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/guides/WORK_IR_EMISSION_GUIDE.md`

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
