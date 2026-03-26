Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c3bcb8da3696c497`

- Symbol: `d_job_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/job/d_job.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/job/d_job.c`
- `engine/modules/job/d_job.h`

## Scorecard

- `engine/modules/job/d_job.h` disposition=`canonical` rank=`1` total_score=`83.57` risk=`HIGH`
- `engine/modules/job/d_job.c` disposition=`quarantine` rank=`2` total_score=`81.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/DIRECTORY_CONTEXT.md, docs/architecture/ECONOMIC_MODEL.md, docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/archive/stray_root_docs/PERF_BUDGETS.md, docs/audit/CANON_MAP.md, docs/audit/DOCS_AUDIT_PROMPT0.md`

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
