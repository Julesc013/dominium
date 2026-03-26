Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c4f8a796cb108db0`

- Symbol: `d_state_machine_set`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/state/state.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/state/state.h`
- `engine/modules/state/state.c`

## Scorecard

- `engine/modules/state/state.c` disposition=`canonical` rank=`1` total_score=`87.26` risk=`HIGH`
- `engine/include/domino/state/state.h` disposition=`quarantine` rank=`2` total_score=`86.73` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/SCHEMA_EVOLUTION.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/IPC_ATTACH_CONSOLES.md, docs/appshell/TUI_FRAMEWORK.md, docs/architecture/APP_CANON0.md, docs/architecture/APP_CANON1.md, docs/architecture/BEHAVIORAL_COMPONENTS_STANDARD.md, docs/architecture/CANON_INDEX.md`

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
