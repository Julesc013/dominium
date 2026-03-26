Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.553e99146b46226a`

- Symbol: `dom_sim_schema_id`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/build_info.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/build_info.h`
- `engine/include/domino/io/schema_registry.h`

## Scorecard

- `engine/include/domino/build_info.h` disposition=`canonical` rank=`1` total_score=`84.17` risk=`HIGH`
- `engine/include/domino/io/schema_registry.h` disposition=`quarantine` rank=`2` total_score=`82.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/COMPATIBILITY_ENFORCEMENT.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/archive/app/APR4_ENGINE_GAME_INTERFACE_INVENTORY.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/ci/HYGIENE_QUEUE.md`

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
