Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c30e2335eecce337`

- Symbol: `d_tui_panel`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/tui/tui.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/tui/tui.h`
- `runtime/ui/tui/tui.c`

## Scorecard

- `engine/include/domino/tui/tui.h` disposition=`canonical` rank=`1` total_score=`88.51` risk=`HIGH`
- `runtime/ui/tui/tui.c` disposition=`quarantine` rank=`2` total_score=`82.86` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/apps/CLIENT_READONLY_INTEGRATION.md, docs/runtime/shell/IPC_ATTACH_CONSOLES.md, docs/runtime/shell/LOGGING_AND_TRACING.md, docs/runtime/shell/TUI_FRAMEWORK.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/GUI_BASELINE.md, docs/audit/APPSHELL3_RETRO_AUDIT.md`

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
