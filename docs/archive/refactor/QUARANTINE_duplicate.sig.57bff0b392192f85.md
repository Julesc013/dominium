Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.57bff0b392192f85`

- Symbol: `d_sim_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `game/domain/simulation/d_sim.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `game/domain/simulation/d_sim.c`
- `game/domain/simulation/d_sim.h`

## Scorecard

- `game/domain/simulation/d_sim.h` disposition=`canonical` rank=`1` total_score=`83.75` risk=`HIGH`
- `game/domain/simulation/d_sim.c` disposition=`quarantine` rank=`2` total_score=`82.62` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/apps/CLI_CONTRACTS.md, docs/apps/COMPATIBILITY_ENFORCEMENT.md, docs/apps/READONLY_ADAPTER.md, docs/architecture/ARCH0_CONSTITUTION.md, docs/architecture/ARCH_BUILD_ENFORCEMENT.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/CANON_INDEX.md, docs/architecture/CHANGELOG_ARCH.md`

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
