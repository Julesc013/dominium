Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e89974b433d9c35c`

- Symbol: `mod_loader_status_to_string`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `game/include/dominium/mods/mod_loader.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `game/include/dominium/mods/mod_loader.h`
- `game/mods/runtime/mod_loader.cpp`

## Scorecard

- `game/include/dominium/mods/mod_loader.h` disposition=`canonical` rank=`1` total_score=`62.88` risk=`HIGH`
- `game/mods/runtime/mod_loader.cpp` disposition=`quarantine` rank=`2` total_score=`62.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MOD_POLICY0_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/HYGIENE_QUEUE.md, docs/specs/SPEC_DOMINIUM_LAYER.md, docs/specs/SPEC_DOMINO_MOD.md`

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
