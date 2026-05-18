Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b008ab556f6b1d58`

- Symbol: `build_default_log_file_path`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/appshell/logging/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/appshell/logging/__init__.py`
- `src/appshell/logging/log_engine.py`

## Scorecard

- `src/appshell/logging/__init__.py` disposition=`canonical` rank=`1` total_score=`79.05` risk=`HIGH`
- `src/appshell/logging/log_engine.py` disposition=`quarantine` rank=`2` total_score=`69.46` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/apps/TESTX_INVENTORY.md, docs/runtime/shell/APPSHELL_CONSTITUTION.md, docs/runtime/shell/IPC_ATTACH_CONSOLES.md, docs/runtime/shell/LOGGING_AND_TRACING.md, docs/runtime/shell/LOG_MERGE_RULES.md, docs/runtime/shell/SUPERVISOR_MODEL.md, docs/runtime/shell/TUI_FRAMEWORK.md, docs/runtime/shell/VIRTUAL_PATHS.md`

## Tests Involved

- `python tools/validators/shell/tool_run_ipc_unify.py --repo-root .`
- `python tools/validators/shell/tool_run_supervisor_hardening.py --repo-root .`
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
