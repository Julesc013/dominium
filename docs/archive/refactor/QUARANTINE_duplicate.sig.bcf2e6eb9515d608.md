Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.bcf2e6eb9515d608`

- Symbol: `tm`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `client/shell/client_shell.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `client/shell/client_shell.c`
- `apps/server/main_server.c`

## Scorecard

- `client/shell/client_shell.c` disposition=`canonical` rank=`1` total_score=`85.83` risk=`HIGH`
- `apps/server/main_server.c` disposition=`quarantine` rank=`2` total_score=`84.64` risk=`HIGH`

## Usage Sites

- Build Targets: `dominium_client`
- Docs: `docs/apps/CLI_CONTRACTS.md, docs/apps/GUI_MODE.md, docs/apps/OBSERVABILITY_PIPELINES.md, docs/apps/PRODUCT_BOUNDARIES.md, docs/apps/README.md, docs/apps/UI_MODES.md, docs/runtime/shell/APPSHELL_CONSTITUTION.md, docs/runtime/shell/CLI_REFERENCE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
