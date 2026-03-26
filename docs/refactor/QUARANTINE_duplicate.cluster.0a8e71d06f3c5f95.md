Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.0a8e71d06f3c5f95`

- Symbol: `_runtime`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/server/runtime/tick_loop.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `src/server/net/loopback_transport.py`
- `src/server/runtime/tick_loop.py`
- `src/server/server_console.py`

## Scorecard

- `src/server/runtime/tick_loop.py` disposition=`canonical` rank=`1` total_score=`63.69` risk=`HIGH`
- `src/server/net/loopback_transport.py` disposition=`quarantine` rank=`2` total_score=`57.86` risk=`HIGH`
- `src/server/server_console.py` disposition=`drop` rank=`3` total_score=`51.43` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/session_lifecycle.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/audit/APPSHELL2_RETRO_AUDIT.md, docs/audit/CAP_NEGOTIATION_BASELINE.md, docs/audit/CTRL2_RETRO_AUDIT.md, docs/audit/CTRL4_RETRO_AUDIT.md, docs/audit/CTRL8_RETRO_AUDIT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
