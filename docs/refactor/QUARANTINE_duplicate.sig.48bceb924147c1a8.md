Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.48bceb924147c1a8`

- Symbol: `d_world_height_at`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/world/d_world_terrain.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/world/d_world_terrain.c`
- `engine/modules/world/d_world_terrain.h`

## Scorecard

- `engine/modules/world/d_world_terrain.c` disposition=`canonical` rank=`1` total_score=`84.38` risk=`HIGH`
- `engine/modules/world/d_world_terrain.h` disposition=`quarantine` rank=`2` total_score=`79.8` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/audit/EARTH5_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/geo/GEOMETRY_EDIT_CONTRACT.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPEC_FIELDS.md, docs/specs/SPEC_WORLD_SOURCE_STACK.md, docs/worldgen/EARTH_PROCEDURAL_CONSTITUTION.md`

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
