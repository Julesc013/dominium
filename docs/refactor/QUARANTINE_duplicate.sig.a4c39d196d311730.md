Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a4c39d196d311730`

- Symbol: `d_q48_16_from_q16_16`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/fixed.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/core/fixed.h`
- `engine/modules/core/fixed.c`

## Scorecard

- `engine/modules/core/fixed.c` disposition=`canonical` rank=`1` total_score=`72.98` risk=`HIGH`
- `engine/include/domino/core/fixed.h` disposition=`quarantine` rank=`2` total_score=`71.9` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/policies/DETERMINISTIC_MATH.md, docs/specs/SPEC_IDENTITY.md, docs/specs/SPEC_NUMERIC.md, docs/specs/SPEC_ORBITS.md, docs/specs/SPEC_ORBITS_TIMEWARP.md, docs/specs/SPEC_REENTRY_THERMAL.md, docs/specs/SPEC_SURFACE_STREAMING.md`

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
