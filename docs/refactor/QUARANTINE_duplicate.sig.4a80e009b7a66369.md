Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4a80e009b7a66369`

- Symbol: `d_build_shutdown`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/build/d_build.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/build/d_build.c`
- `engine/modules/build/d_build.h`

## Scorecard

- `engine/modules/build/d_build.c` disposition=`canonical` rank=`1` total_score=`84.64` risk=`HIGH`
- `engine/modules/build/d_build.h` disposition=`quarantine` rank=`2` total_score=`82.5` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/app/RUNTIME_LOOP.md, docs/app/TESTX_INVENTORY.md, docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/SUPERVISOR_MODEL.md, docs/architecture/THERMAL_MODEL.md, docs/architecture/session_lifecycle.md, docs/archive/app/APR1_RUNTIME_AUDIT.md, docs/audit/APPSHELL_IPC_BASELINE.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
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
