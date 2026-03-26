Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e06e9a2aac843707`

- Symbol: `d_net_apply_for_tick`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/net/d_net_apply.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/net/d_net_apply.c`
- `engine/modules/net/d_net_apply.h`

## Scorecard

- `engine/modules/net/d_net_apply.h` disposition=`canonical` rank=`1` total_score=`86.67` risk=`HIGH`
- `engine/modules/net/d_net_apply.c` disposition=`quarantine` rank=`2` total_score=`81.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/archive/stray_root_docs/PERF_BUDGETS.md, docs/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md, docs/audit/APPSHELL2_RETRO_AUDIT.md, docs/audit/CAP_NEGOTIATION_BASELINE.md, docs/audit/CONTROL_PLANE_FINAL_BASELINE.md, docs/audit/CTRL10_RETRO_AUDIT.md`

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
