Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.11e0405d00848a23`

- Symbol: `build_log_event`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/appshell/logging/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/logging/__init__.py`
- `src/appshell/logging/log_engine.py`
- `src/appshell/logging_sink.py`

## Scorecard

- `src/appshell/logging/__init__.py` disposition=`canonical` rank=`1` total_score=`79.05` risk=`HIGH`
- `src/appshell/logging/log_engine.py` disposition=`quarantine` rank=`2` total_score=`69.46` risk=`HIGH`
- `src/appshell/logging_sink.py` disposition=`drop` rank=`3` total_score=`54.68` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/TESTX_INVENTORY.md, docs/appshell/APPSHELL_CONSTITUTION.md, docs/appshell/IPC_ATTACH_CONSOLES.md, docs/appshell/LOGGING_AND_TRACING.md, docs/appshell/LOG_MERGE_RULES.md, docs/appshell/SUPERVISOR_MODEL.md, docs/appshell/TUI_FRAMEWORK.md, docs/appshell/VIRTUAL_PATHS.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
