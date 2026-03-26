Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.967fb7fae7c6e331`

- Symbol: `d_sim_hash_world`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/sim/d_sim_hash.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/sim/d_sim_hash.c`
- `engine/modules/sim/d_sim_hash.h`

## Scorecard

- `engine/modules/sim/d_sim_hash.h` disposition=`canonical` rank=`1` total_score=`85.77` risk=`HIGH`
- `engine/modules/sim/d_sim_hash.c` disposition=`quarantine` rank=`2` total_score=`84.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLI_CONTRACTS.md, docs/architecture/ARCH0_CONSTITUTION.md, docs/architecture/ARCH_BUILD_ENFORCEMENT.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/CANON_INDEX.md, docs/architecture/DIRECTORY_CONTEXT.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/VALIDATION_RULES.md`

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
