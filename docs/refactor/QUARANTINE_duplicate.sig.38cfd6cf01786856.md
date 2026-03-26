Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.38cfd6cf01786856`

- Symbol: `d_job_planner_tick`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/job/d_job_planner.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/job/d_job_planner.c`
- `engine/modules/job/d_job_planner.h`

## Scorecard

- `engine/modules/job/d_job_planner.h` disposition=`canonical` rank=`1` total_score=`62.8` risk=`HIGH`
- `engine/modules/job/d_job_planner.c` disposition=`quarantine` rank=`2` total_score=`61.73` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/specs/SPEC_JOBS.md, docs/specs/SPEC_JOB_AI.md, docs/worldgen/AI_AUTONOMY_BASELINE.md`

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
