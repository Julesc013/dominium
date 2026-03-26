Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.54e35a2a895b61e1`

- Symbol: `timeval`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/system/dsys_term.c`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, deprecate, quarantine`

## Competing Files

- `engine/modules/system/dsys_platform_stub.c`
- `engine/modules/system/dsys_posix.c`
- `engine/modules/system/dsys_sdl2_stub.c`
- `engine/modules/system/dsys_term.c`

## Scorecard

- `engine/modules/system/dsys_term.c` disposition=`canonical` rank=`1` total_score=`56.19` risk=`HIGH`
- `engine/modules/system/dsys_platform_stub.c` disposition=`quarantine` rank=`2` total_score=`48.21` risk=`HIGH`
- `engine/modules/system/dsys_posix.c` disposition=`quarantine` rank=`3` total_score=`48.21` risk=`HIGH`
- `engine/modules/system/dsys_sdl2_stub.c` disposition=`merge` rank=`4` total_score=`35.36` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `none`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
