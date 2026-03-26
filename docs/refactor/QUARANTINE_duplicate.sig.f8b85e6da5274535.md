Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f8b85e6da5274535`

- Symbol: `d_registry_add`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/d_registry.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/d_registry.c`
- `engine/modules/core/d_registry.h`

## Scorecard

- `engine/modules/core/d_registry.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/modules/core/d_registry.h` disposition=`quarantine` rank=`2` total_score=`87.26` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/CONTRIBUTING.md, docs/MODDER_GUIDE.md, docs/PROCESS_REGISTRY.md, docs/SCHEMA_CANON_ALIGNMENT.md, docs/app/ENGINE_GAME_DIAGNOSTICS.md, docs/app/TESTX_INVENTORY.md, docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/IPC_ATTACH_CONSOLES.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
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
