Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.998a347139be3205`

- Symbol: `_sorted_strings`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/platform/platform_input.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/client/render/renderers/null_renderer.py`
- `src/client/render/renderers/software_renderer.py`
- `src/client/ui/teleport_controller.py`
- `src/geo/kernel/geo_kernel.py`
- `src/geo/lens/lens_engine.py`
- `src/geo/projection/projection_engine.py`
- `src/geo/projection/view_adapters.py`
- `src/platform/platform_gfx.py`
- `src/platform/platform_input.py`
- `src/platform/platform_input_routing.py`
- `tools/earth/earth9_stress_common.py`

## Scorecard

- `src/platform/platform_input.py` disposition=`canonical` rank=`1` total_score=`76.43` risk=`HIGH`
- `tools/earth/earth9_stress_common.py` disposition=`quarantine` rank=`2` total_score=`74.58` risk=`HIGH`
- `src/platform/platform_gfx.py` disposition=`quarantine` rank=`3` total_score=`71.55` risk=`HIGH`
- `src/client/render/renderers/null_renderer.py` disposition=`quarantine` rank=`4` total_score=`70.18` risk=`HIGH`
- `src/client/render/renderers/software_renderer.py` disposition=`merge` rank=`5` total_score=`65.18` risk=`HIGH`
- `src/geo/lens/lens_engine.py` disposition=`drop` rank=`6` total_score=`60.95` risk=`HIGH`
- `src/platform/platform_input_routing.py` disposition=`merge` rank=`7` total_score=`58.57` risk=`HIGH`
- `src/geo/kernel/geo_kernel.py` disposition=`drop` rank=`8` total_score=`57.62` risk=`HIGH`
- `src/client/ui/teleport_controller.py` disposition=`drop` rank=`9` total_score=`57.26` risk=`HIGH`
- `src/geo/projection/projection_engine.py` disposition=`drop` rank=`10` total_score=`56.67` risk=`HIGH`
- `src/geo/projection/view_adapters.py` disposition=`drop` rank=`11` total_score=`55.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/app/CLIENT_UI_LAYER.md, docs/app/CLI_CONTRACTS.md, docs/app/RUNTIME_LOOP.md, docs/app/TESTX_INVENTORY.md, docs/app/TUI_MODE.md, docs/architecture/ARCH_BUILD_ENFORCEMENT.md, docs/architecture/ARCH_ENFORCEMENT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
