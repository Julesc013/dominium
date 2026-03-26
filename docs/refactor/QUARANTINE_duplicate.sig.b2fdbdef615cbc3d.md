Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b2fdbdef615cbc3d`

- Symbol: `d_tui_list`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/tui/tui.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/tui/tui.h`
- `engine/modules/tui/tui.c`

## Scorecard

- `engine/include/domino/tui/tui.h` disposition=`canonical` rank=`1` total_score=`90.89` risk=`HIGH`
- `engine/modules/tui/tui.c` disposition=`quarantine` rank=`2` total_score=`85.24` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/app/CLIENT_READONLY_INTEGRATION.md, docs/app/CLI_CONTRACTS.md, docs/app/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md, docs/app/GUI_MODE.md, docs/app/IDE_WORKFLOW.md, docs/app/NATIVE_UI_POLICY.md`

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
