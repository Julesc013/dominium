Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e6424f6ade067785`

- Symbol: `d_worldgen_register`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/world/d_worldgen.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/world/d_worldgen.c`
- `engine/modules/world/d_worldgen.h`

## Scorecard

- `engine/modules/world/d_worldgen.h` disposition=`canonical` rank=`1` total_score=`74.15` risk=`HIGH`
- `engine/modules/world/d_worldgen.c` disposition=`quarantine` rank=`2` total_score=`71.88` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/WORLDDEFINITION.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/WORLDGEN_CONSTRAINT_SOLVER_REPORT.md, docs/geo/WORLDGEN_CONSTITUTION.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/worldgen/TEMPLATE_REGISTRY.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
