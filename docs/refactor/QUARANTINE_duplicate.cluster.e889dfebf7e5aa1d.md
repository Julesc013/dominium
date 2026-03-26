Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e889dfebf7e5aa1d`

- Symbol: `parse_report`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/integration/integration_meta_test.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/integration/integration_meta_test.py`
- `tests/integration/renderer_backend_contracts.py`

## Scorecard

- `tests/integration/integration_meta_test.py` disposition=`canonical` rank=`1` total_score=`62.63` risk=`HIGH`
- `tests/integration/renderer_backend_contracts.py` disposition=`quarantine` rank=`2` total_score=`60.85` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/EXPLORATION_SCALING_PROOF.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/HYGIENE_QUEUE.md, docs/specs/SPEC_DUI.md, docs/specs/SPEC_GAME_CLI.md, docs/specs/SPEC_WORLD_SOURCE_STACK.md`

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
