Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4b606ae90f6bd28c`

- Symbol: `d_registry_add_with_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/kernel/d_registry.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/kernel/d_registry.c`
- `engine/kernel/d_registry.h`

## Scorecard

- `engine/kernel/d_registry.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/kernel/d_registry.h` disposition=`quarantine` rank=`2` total_score=`87.26` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/CONTRIBUTING.md, docs/MODDER_GUIDE.md, docs/PROCESS_REGISTRY.md, docs/SCHEMA_CANON_ALIGNMENT.md, docs/apps/TESTX_INVENTORY.md, docs/runtime/shell/APPSHELL_CONSTITUTION.md, docs/runtime/shell/IPC_ATTACH_CONSOLES.md, docs/runtime/shell/TUI_FRAMEWORK.md`

## Tests Involved

- `python tools/validators/shell/tool_run_ipc_unify.py --repo-root .`
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
