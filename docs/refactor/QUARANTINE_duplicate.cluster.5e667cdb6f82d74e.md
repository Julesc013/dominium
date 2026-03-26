Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.5e667cdb6f82d74e`

- Symbol: `dom_launcher`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `launcher/include/launcher/_internal/dom_launcher/launcher_ui_cli.h`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `launcher/include/launcher/_internal/dom_launcher/launcher_context.h`
- `launcher/include/launcher/_internal/dom_launcher/launcher_db.h`
- `launcher/include/launcher/_internal/dom_launcher/launcher_discovery.h`
- `launcher/include/launcher/_internal/dom_launcher/launcher_state.h`
- `launcher/include/launcher/_internal/dom_launcher/launcher_ui_cli.h`
- `launcher/include/launcher/_internal/dom_launcher/launcher_ui_gui.h`
- `launcher/include/launcher/_internal/dom_launcher/launcher_ui_tui.h`

## Scorecard

- `launcher/include/launcher/_internal/dom_launcher/launcher_ui_cli.h` disposition=`canonical` rank=`1` total_score=`88.21` risk=`HIGH`
- `launcher/include/launcher/_internal/dom_launcher/launcher_context.h` disposition=`quarantine` rank=`2` total_score=`87.26` risk=`HIGH`
- `launcher/include/launcher/_internal/dom_launcher/launcher_db.h` disposition=`quarantine` rank=`3` total_score=`86.73` risk=`HIGH`
- `launcher/include/launcher/_internal/dom_launcher/launcher_state.h` disposition=`quarantine` rank=`4` total_score=`86.07` risk=`HIGH`
- `launcher/include/launcher/_internal/dom_launcher/launcher_ui_gui.h` disposition=`quarantine` rank=`5` total_score=`78.69` risk=`HIGH`
- `launcher/include/launcher/_internal/dom_launcher/launcher_ui_tui.h` disposition=`drop` rank=`6` total_score=`73.93` risk=`HIGH`
- `launcher/include/launcher/_internal/dom_launcher/launcher_discovery.h` disposition=`drop` rank=`7` total_score=`73.26` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLI_CONTRACTS.md, docs/app/IDE_WORKFLOW.md, docs/app/TESTX_INVENTORY.md, docs/appshell/CLI_REFERENCE.md, docs/architecture/APPLICATION_CONTRACTS.md, docs/architecture/APP_CANON0.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/COMPONENTS.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
