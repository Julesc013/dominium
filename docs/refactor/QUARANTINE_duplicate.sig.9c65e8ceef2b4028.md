Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9c65e8ceef2b4028`

- Symbol: `d_system_process_spawn`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/system/d_system.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/system/d_system.h`
- `engine/modules/system/d_system.h`

## Scorecard

- `engine/include/domino/system/d_system.h` disposition=`canonical` rank=`1` total_score=`79.88` risk=`HIGH`
- `engine/modules/system/d_system.h` disposition=`quarantine` rank=`2` total_score=`77.2` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/STAR_SYSTEM_SEED_BASELINE.md, docs/audit/SYS4_RETRO_AUDIT.md, docs/audit/VALIDATION_STACK_MAP.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/geo/WORLDGEN_CONSTITUTION.md, docs/governance/REPOX_RULESETS.md`

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
