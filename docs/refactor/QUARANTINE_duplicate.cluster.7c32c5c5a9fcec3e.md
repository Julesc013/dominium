Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.7c32c5c5a9fcec3e`

- Symbol: `TestSink`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/tests/execution_contract_tests.cpp`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `engine/tests/execution_contract_tests.cpp`
- `engine/tests/execution_equivalence_tests.cpp`
- `engine/tests/execution_ir_tests.cpp`
- `engine/tests/streaming_work_ir_tests.cpp`

## Scorecard

- `engine/tests/execution_contract_tests.cpp` disposition=`canonical` rank=`1` total_score=`62.27` risk=`HIGH`
- `engine/tests/execution_equivalence_tests.cpp` disposition=`quarantine` rank=`2` total_score=`60.02` risk=`HIGH`
- `engine/tests/execution_ir_tests.cpp` disposition=`quarantine` rank=`3` total_score=`52.74` risk=`HIGH`
- `engine/tests/streaming_work_ir_tests.cpp` disposition=`drop` rank=`4` total_score=`52.14` risk=`HIGH`

## Usage Sites

- Build Targets: `execution_contract_tests`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
