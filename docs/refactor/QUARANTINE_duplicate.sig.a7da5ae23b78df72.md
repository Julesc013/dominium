Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a7da5ae23b78df72`

- Symbol: `dom_ticks_to_ns`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/core/spacetime.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/core/spacetime.h`
- `engine/modules/core/spacetime.c`

## Scorecard

- `engine/include/domino/core/spacetime.h` disposition=`canonical` rank=`1` total_score=`76.88` risk=`HIGH`
- `engine/modules/core/spacetime.c` disposition=`quarantine` rank=`2` total_score=`69.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/specs/SPEC_DETERMINISM.md, docs/specs/SPEC_ORBITS_TIMEWARP.md, docs/specs/SPEC_REFERENCE_FRAMES.md, docs/specs/SPEC_SPACETIME.md`

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
