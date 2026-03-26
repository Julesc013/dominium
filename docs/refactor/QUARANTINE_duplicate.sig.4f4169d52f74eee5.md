Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4f4169d52f74eee5`

- Symbol: `AppShellIPCEndpointServer`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/appshell/ipc/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/appshell/ipc/__init__.py`
- `src/appshell/ipc/ipc_endpoint_server.py`

## Scorecard

- `src/appshell/ipc/__init__.py` disposition=`canonical` rank=`1` total_score=`63.57` risk=`HIGH`
- `src/appshell/ipc/ipc_endpoint_server.py` disposition=`quarantine` rank=`2` total_score=`54.35` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/IPC_DISCOVERY.md, docs/appshell/SUPERVISOR_MODEL.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/audit/APPSHELL4_RETRO_AUDIT.md, docs/audit/APPSHELL6_RETRO_AUDIT.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
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
