Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.0f45ea8d2a75c02c`

- Symbol: `d_rng_stream_seed`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/core/rng_streams.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/core/rng_streams.h`
- `engine/modules/core/rng_streams.c`

## Scorecard

- `engine/include/domino/core/rng_streams.h` disposition=`canonical` rank=`1` total_score=`77.67` risk=`HIGH`
- `engine/modules/core/rng_streams.c` disposition=`quarantine` rank=`2` total_score=`75.7` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CODE_CHANGE_JUSTIFICATION.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/RNG_MODEL.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/WORLDGEN_CONSTITUTION_BASELINE.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md, docs/audit/WORLDGEN_LOCK_BASELINE.md, docs/geo/WORLDGEN_CONSTITUTION.md`

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
