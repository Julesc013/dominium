Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.75392aa20b2652ab`

- Symbol: `d_input_shutdown`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/input/input.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/input/input.h`
- `engine/modules/input/input.c`

## Scorecard

- `engine/include/domino/input/input.h` disposition=`canonical` rank=`1` total_score=`81.37` risk=`HIGH`
- `engine/modules/input/input.c` disposition=`quarantine` rank=`2` total_score=`80.48` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/RUNTIME_LOOP.md, docs/app/TESTX_INVENTORY.md, docs/architecture/session_lifecycle.md, docs/audit/INTERFACE_LAUNCH_REPORT.md, docs/audit/MACROCAPSULE_BEHAVIOR_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/THERM1_RETRO_AUDIT.md`

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
