Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.aa541b06cf37f8ec`

- Symbol: `dom_game_runtime_create`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/tests/game/contract/dominium_no_modal_tests.cpp`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/tests/game/contract/dominium_no_modal_tests.cpp`
- `tests/tests/game/contract/dominium_qos_tests.cpp`
- `tests/tests/game/contract/dominium_session_tests.cpp`

## Scorecard

- `tests/tests/game/contract/dominium_no_modal_tests.cpp` disposition=`canonical` rank=`1` total_score=`74.29` risk=`HIGH`
- `tests/tests/game/contract/dominium_qos_tests.cpp` disposition=`quarantine` rank=`2` total_score=`74.29` risk=`HIGH`
- `tests/tests/game/contract/dominium_session_tests.cpp` disposition=`quarantine` rank=`3` total_score=`74.29` risk=`HIGH`

## Usage Sites

- Build Targets: `dominium_no_modal_tests`
- Docs: `docs/apps/TESTX_INVENTORY.md, docs/archive/app/APR4_ENGINE_GAME_INTERFACE_INVENTORY.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPEC_DOMINO_SYS.md, docs/specs/SPEC_DUI.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
