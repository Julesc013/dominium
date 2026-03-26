Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9f3acba561ab7a43`

- Symbol: `dg_delta_registry_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/sim/act/dg_delta_registry.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/sim/act/dg_delta_registry.c`
- `engine/modules/sim/act/dg_delta_registry.h`

## Scorecard

- `engine/modules/sim/act/dg_delta_registry.h` disposition=`canonical` rank=`1` total_score=`86.49` risk=`HIGH`
- `engine/modules/sim/act/dg_delta_registry.c` disposition=`quarantine` rank=`2` total_score=`86.31` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/TIME_DILATION_WITHOUT_TIME_WARP.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/audit/DOC_INDEX.md, docs/ci/HYGIENE_QUEUE.md, docs/specs/SPEC_TIME_WARP.md`

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
