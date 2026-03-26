Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b46db22bf4256c92`

- Symbol: `d_sim_process_tick`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/sim/d_sim_process.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/sim/d_sim_process.c`
- `engine/modules/sim/d_sim_process.h`

## Scorecard

- `engine/modules/sim/d_sim_process.h` disposition=`canonical` rank=`1` total_score=`83.21` risk=`HIGH`
- `engine/modules/sim/d_sim_process.c` disposition=`quarantine` rank=`2` total_score=`81.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/DOC_INDEX.md, docs/audit/FIDELITY_ARBITRATION_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MULTIPLAYER_BASELINE_FINAL.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/TIME_CONSTITUTION_BASELINE.md, docs/audit/VALIDATION_STACK_MAP.md, docs/canon/constitution_v1.md`

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
