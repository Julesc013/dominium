Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.726fca9fd3652f0e`

- Symbol: `dom_time_core_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/core/dom_time_core.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/core/dom_time_core.h`
- `engine/modules/core/dom_time_core.c`

## Scorecard

- `engine/include/domino/core/dom_time_core.h` disposition=`canonical` rank=`1` total_score=`91.9` risk=`HIGH`
- `engine/modules/core/dom_time_core.c` disposition=`quarantine` rank=`2` total_score=`87.26` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CODE_CHANGE_JUSTIFICATION.md, docs/app/TESTX_INVENTORY.md, docs/architecture/PLATFORM_RESPONSIBILITY.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/archive/app/APR4_ENGINE_GAME_INTERFACE_INVENTORY.md, docs/archive/build/APR5_BUILD_INVENTORY.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/archive/ci/PHASE6_AUDIT_REPORT.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
