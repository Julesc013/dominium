Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.5cebbd429f731645`

- Symbol: `dom_time_event_pop`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/core/dom_time_events.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/core/dom_time_events.h`
- `engine/modules/core/dom_time_events.c`

## Scorecard

- `engine/include/domino/core/dom_time_events.h` disposition=`canonical` rank=`1` total_score=`74.88` risk=`HIGH`
- `engine/modules/core/dom_time_events.c` disposition=`quarantine` rank=`2` total_score=`72.38` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/DOC_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md`

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
