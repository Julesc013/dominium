Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f2e7370920c2c2d8`

- Symbol: `d_build_validate_world`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/build/d_build_validate.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/build/d_build.h`
- `engine/modules/build/d_build_validate.c`

## Scorecard

- `engine/modules/build/d_build_validate.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/modules/build/d_build.h` disposition=`quarantine` rank=`2` total_score=`82.5` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/SCHEMA_CANON_ALIGNMENT.md, docs/SCHEMA_EVOLUTION.md, docs/app/CLI_CONTRACTS.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/APP_CANON0.md, docs/architecture/ARCH_BUILD_ENFORCEMENT.md, docs/architecture/ARCH_REPO_LAYOUT.md`

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
