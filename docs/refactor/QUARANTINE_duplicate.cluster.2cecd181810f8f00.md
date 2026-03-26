Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.2cecd181810f8f00`

- Symbol: `_sorted_unique_strings`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/control/proof/control_proof_bundle.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/client/render/renderers/hw_renderer_gl.py`
- `src/client/render/snapshot_capture.py`
- `src/control/proof/control_proof_bundle.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/geo/edit/geometry_state_engine.py`
- `src/geo/overlay/overlay_merge_engine.py`
- `src/geo/worldgen/worldgen_engine.py`
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/mw/mw_surface_refiner_l3.py`

## Scorecard

- `src/control/proof/control_proof_bundle.py` disposition=`canonical` rank=`1` total_score=`59.34` risk=`HIGH`
- `src/worldgen/earth/climate_field_engine.py` disposition=`quarantine` rank=`2` total_score=`55.56` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`quarantine` rank=`3` total_score=`53.43` risk=`HIGH`
- `src/client/render/snapshot_capture.py` disposition=`quarantine` rank=`4` total_score=`50.84` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`quarantine` rank=`5` total_score=`49.39` risk=`HIGH`
- `src/client/render/renderers/hw_renderer_gl.py` disposition=`merge` rank=`6` total_score=`48.59` risk=`HIGH`
- `src/geo/overlay/overlay_merge_engine.py` disposition=`merge` rank=`7` total_score=`46.04` risk=`HIGH`
- `src/worldgen/mw/mw_surface_refiner_l3.py` disposition=`drop` rank=`8` total_score=`45.69` risk=`HIGH`
- `src/embodiment/collision/macro_heightfield_provider.py` disposition=`drop` rank=`9` total_score=`45.44` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
