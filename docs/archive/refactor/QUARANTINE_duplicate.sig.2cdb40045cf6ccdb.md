Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2cdb40045cf6ccdb`

- Symbol: `d_env_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `game/domain/environment/d_env.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `game/domain/environment/d_env.c`
- `game/domain/environment/d_env.h`

## Scorecard

- `game/domain/environment/d_env.h` disposition=`canonical` rank=`1` total_score=`83.15` risk=`HIGH`
- `game/domain/environment/d_env.c` disposition=`quarantine` rank=`2` total_score=`81.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/SURVIVAL_SLICE.md, docs/runtime/shell/UI_MODE_RESOLUTION.md, docs/architecture/CANON_INDEX.md, docs/architecture/DIRECTORY_CONTEXT.md, docs/architecture/DIRECTORY_STRUCTURE.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/TERRAIN_FIELDS.md, docs/architecture/srz_contract.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
