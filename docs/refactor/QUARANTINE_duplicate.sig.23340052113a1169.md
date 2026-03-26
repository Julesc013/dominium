Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.23340052113a1169`

- Symbol: `dg_work_queue_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/execution/ir/dg_work_queue.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/execution/ir/dg_work_queue.c`
- `engine/modules/execution/ir/dg_work_queue.h`

## Scorecard

- `engine/modules/execution/ir/dg_work_queue.h` disposition=`canonical` rank=`1` total_score=`76.89` risk=`HIGH`
- `engine/modules/execution/ir/dg_work_queue.c` disposition=`quarantine` rank=`2` total_score=`73.8` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/app/RUNTIME_LOOP.md, docs/architecture/CANON_INDEX.md, docs/architecture/CODE_DATA_BOUNDARY.md, docs/architecture/REFUSAL_SEMANTICS.md, docs/architecture/SYS_CAPS_AND_EXEC_POLICY.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/audit/CANON_MAP.md, docs/audit/CTRL1_RETRO_AUDIT.md`

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
