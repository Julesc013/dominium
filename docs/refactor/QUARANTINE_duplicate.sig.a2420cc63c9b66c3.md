Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a2420cc63c9b66c3`

- Symbol: `dg_pose_compose`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/dg_pose.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/dg_pose.c`
- `engine/modules/core/dg_pose.h`

## Scorecard

- `engine/modules/core/dg_pose.h` disposition=`canonical` rank=`1` total_score=`64.23` risk=`HIGH`
- `engine/modules/core/dg_pose.c` disposition=`quarantine` rank=`2` total_score=`63.26` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/interior/INTERIOR_VOLUME_MODEL.md, docs/specs/SPEC_POSE_AND_ANCHORS.md`

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
