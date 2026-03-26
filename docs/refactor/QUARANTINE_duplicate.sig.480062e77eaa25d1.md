Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.480062e77eaa25d1`

- Symbol: `_sorted_unique_strings`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/registry_compile/compiler.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/client/interaction/affordance_generator.py`
- `src/client/interaction/inspection_overlays.py`
- `src/client/interaction/interaction_dispatch.py`
- `src/client/interaction/interaction_panel.py`
- `src/client/interaction/preview_generator.py`
- `src/client/render/renderers/hw_renderer_gl.py`
- `src/client/render/representation_resolver.py`
- `src/client/render/snapshot_capture.py`
- `src/control/capability/capability_engine.py`
- `src/control/control_plane_engine.py`
- `src/control/effects/effect_engine.py`
- `src/control/fidelity/fidelity_engine.py`
- `src/control/ir/control_ir_compiler.py`
- `src/control/ir/control_ir_programs.py`
- `src/control/ir/control_ir_verifier.py`
- `src/control/negotiation/negotiation_kernel.py`
- `src/control/planning/plan_engine.py`
- `src/control/proof/control_proof_bundle.py`
- `src/control/view/view_engine.py`
- `src/core/constraints/constraint_engine.py`
- `src/core/flow/flow_engine.py`
- `src/core/graph/network_graph_engine.py`
- `src/core/graph/routing_engine.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/fields/field_engine.py`
- `src/geo/edit/geometry_state_engine.py`
- `src/geo/overlay/overlay_merge_engine.py`
- `src/geo/path/path_engine.py`
- `src/geo/worldgen/worldgen_engine.py`
- `src/infrastructure/formalization/inference_engine.py`
- `src/inspection/inspection_engine.py`
- `src/interaction/action_surface_engine.py`
- `src/interaction/mount/mount_engine.py`
- `src/interaction/pose/pose_engine.py`
- `src/interaction/task/task_engine.py`
- `src/interior/compartment_flow_builder.py`
- `src/interior/compartment_flow_engine.py`
- `src/interior/interior_engine.py`
- `src/lib/artifact/artifact_validator.py`
- `src/lib/instance/instance_validator.py`
- `src/lib/provides/provider_resolution.py`
- `src/logistics/logistics_engine.py`
- `src/machines/port_engine.py`
- `src/materials/commitments/commitment_engine.py`
- `src/materials/construction/construction_engine.py`
- `src/materials/maintenance/decay_engine.py`
- `src/materials/materialization/materialization_engine.py`
- `src/materials/provenance/event_stream_index.py`
- `src/mechanics/structural_graph_engine.py`
- `src/platform/target_matrix.py`
- `src/release/archive_policy.py`
- `src/release/component_graph_resolver.py`
- `src/release/update_resolver.py`
- `src/specs/spec_engine.py`
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/mw/mw_surface_refiner_l3.py`
- `tools/control/tool_determinism_compare.py`
- `tools/control/tool_global_control_stress.py`
- `tools/control/tool_run_control_stress.py`
- `tools/meta/observability_common.py`
- `tools/xstack/registry_compile/compiler.py`
- `tools/xstack/sessionx/net_handshake.py`

## Scorecard

- `tools/xstack/registry_compile/compiler.py` disposition=`canonical` rank=`1` total_score=`67.98` risk=`HIGH`
- `tools/xstack/sessionx/net_handshake.py` disposition=`quarantine` rank=`2` total_score=`67.98` risk=`HIGH`
- `src/core/graph/network_graph_engine.py` disposition=`quarantine` rank=`3` total_score=`64.17` risk=`HIGH`
- `src/core/graph/routing_engine.py` disposition=`quarantine` rank=`4` total_score=`62.74` risk=`HIGH`
- `tools/control/tool_run_control_stress.py` disposition=`quarantine` rank=`5` total_score=`62.58` risk=`HIGH`
- `src/control/capability/capability_engine.py` disposition=`quarantine` rank=`6` total_score=`61.96` risk=`HIGH`
- `tools/meta/observability_common.py` disposition=`quarantine` rank=`7` total_score=`61.83` risk=`HIGH`
- `src/specs/spec_engine.py` disposition=`quarantine` rank=`8` total_score=`59.58` risk=`HIGH`
- `src/control/proof/control_proof_bundle.py` disposition=`quarantine` rank=`9` total_score=`59.34` risk=`HIGH`
- `src/core/flow/flow_engine.py` disposition=`quarantine` rank=`10` total_score=`59.29` risk=`HIGH`
- `tools/control/tool_global_control_stress.py` disposition=`quarantine` rank=`11` total_score=`59.09` risk=`HIGH`
- `src/platform/target_matrix.py` disposition=`quarantine` rank=`12` total_score=`58.79` risk=`HIGH`
- `src/control/view/view_engine.py` disposition=`quarantine` rank=`13` total_score=`58.63` risk=`HIGH`
- `src/control/fidelity/fidelity_engine.py` disposition=`quarantine` rank=`14` total_score=`58.62` risk=`HIGH`
- `src/inspection/inspection_engine.py` disposition=`merge` rank=`15` total_score=`57.68` risk=`HIGH`
- `src/materials/commitments/commitment_engine.py` disposition=`drop` rank=`16` total_score=`57.32` risk=`HIGH`
- `src/fields/field_engine.py` disposition=`merge` rank=`17` total_score=`56.61` risk=`HIGH`
- `src/interior/interior_engine.py` disposition=`merge` rank=`18` total_score=`56.59` risk=`HIGH`
- `src/interaction/pose/pose_engine.py` disposition=`merge` rank=`19` total_score=`56.56` risk=`HIGH`
- `src/client/interaction/inspection_overlays.py` disposition=`merge` rank=`20` total_score=`56.31` risk=`HIGH`
- `src/lib/provides/provider_resolution.py` disposition=`merge` rank=`21` total_score=`56.27` risk=`HIGH`
- `src/release/component_graph_resolver.py` disposition=`drop` rank=`22` total_score=`55.94` risk=`HIGH`
- `tools/control/tool_determinism_compare.py` disposition=`drop` rank=`23` total_score=`55.83` risk=`HIGH`
- `src/worldgen/earth/climate_field_engine.py` disposition=`merge` rank=`24` total_score=`55.56` risk=`HIGH`
- `src/client/interaction/interaction_dispatch.py` disposition=`merge` rank=`25` total_score=`55.48` risk=`HIGH`
- `src/core/constraints/constraint_engine.py` disposition=`drop` rank=`26` total_score=`55.48` risk=`HIGH`
- `src/lib/instance/instance_validator.py` disposition=`merge` rank=`27` total_score=`55.3` risk=`HIGH`
- `src/logistics/logistics_engine.py` disposition=`merge` rank=`28` total_score=`55.1` risk=`HIGH`
- `src/materials/provenance/event_stream_index.py` disposition=`drop` rank=`29` total_score=`54.95` risk=`HIGH`
- `src/interaction/mount/mount_engine.py` disposition=`merge` rank=`30` total_score=`54.63` risk=`HIGH`
- `src/client/interaction/affordance_generator.py` disposition=`merge` rank=`31` total_score=`54.27` risk=`HIGH`
- `src/interaction/task/task_engine.py` disposition=`merge` rank=`32` total_score=`54.12` risk=`HIGH`
- `src/control/ir/control_ir_verifier.py` disposition=`drop` rank=`33` total_score=`53.99` risk=`HIGH`
- `src/client/interaction/interaction_panel.py` disposition=`merge` rank=`34` total_score=`53.45` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`merge` rank=`35` total_score=`53.43` risk=`HIGH`
- `src/interior/compartment_flow_builder.py` disposition=`drop` rank=`36` total_score=`53.31` risk=`HIGH`
- `src/release/archive_policy.py` disposition=`merge` rank=`37` total_score=`53.27` risk=`HIGH`
- `src/machines/port_engine.py` disposition=`drop` rank=`38` total_score=`53.01` risk=`HIGH`
- `src/materials/materialization/materialization_engine.py` disposition=`drop` rank=`39` total_score=`52.93` risk=`HIGH`
- `src/client/render/representation_resolver.py` disposition=`drop` rank=`40` total_score=`52.92` risk=`HIGH`
- `src/geo/path/path_engine.py` disposition=`merge` rank=`41` total_score=`52.8` risk=`HIGH`
- `src/materials/construction/construction_engine.py` disposition=`merge` rank=`42` total_score=`52.75` risk=`HIGH`
- `src/interior/compartment_flow_engine.py` disposition=`drop` rank=`43` total_score=`52.72` risk=`HIGH`
- `src/lib/artifact/artifact_validator.py` disposition=`drop` rank=`44` total_score=`52.19` risk=`HIGH`
- `src/control/ir/control_ir_programs.py` disposition=`drop` rank=`45` total_score=`51.89` risk=`HIGH`
- `src/infrastructure/formalization/inference_engine.py` disposition=`drop` rank=`46` total_score=`51.42` risk=`HIGH`
- `src/control/ir/control_ir_compiler.py` disposition=`drop` rank=`47` total_score=`51.26` risk=`HIGH`
- `src/client/render/snapshot_capture.py` disposition=`merge` rank=`48` total_score=`50.84` risk=`HIGH`
- `src/interaction/action_surface_engine.py` disposition=`drop` rank=`49` total_score=`50.36` risk=`HIGH`
- `src/control/negotiation/negotiation_kernel.py` disposition=`drop` rank=`50` total_score=`49.49` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`drop` rank=`51` total_score=`49.39` risk=`HIGH`
- `src/materials/maintenance/decay_engine.py` disposition=`drop` rank=`52` total_score=`48.67` risk=`HIGH`
- `src/client/render/renderers/hw_renderer_gl.py` disposition=`merge` rank=`53` total_score=`48.59` risk=`HIGH`
- `src/control/effects/effect_engine.py` disposition=`drop` rank=`54` total_score=`46.67` risk=`HIGH`
- `src/mechanics/structural_graph_engine.py` disposition=`drop` rank=`55` total_score=`46.4` risk=`HIGH`
- `src/release/update_resolver.py` disposition=`drop` rank=`56` total_score=`46.12` risk=`HIGH`
- `src/geo/overlay/overlay_merge_engine.py` disposition=`merge` rank=`57` total_score=`46.04` risk=`HIGH`
- `src/control/control_plane_engine.py` disposition=`merge` rank=`58` total_score=`46.01` risk=`HIGH`
- `src/worldgen/mw/mw_surface_refiner_l3.py` disposition=`drop` rank=`59` total_score=`45.69` risk=`HIGH`
- `src/embodiment/collision/macro_heightfield_provider.py` disposition=`drop` rank=`60` total_score=`45.44` risk=`HIGH`
- `src/client/interaction/preview_generator.py` disposition=`merge` rank=`61` total_score=`44.39` risk=`HIGH`
- `src/control/planning/plan_engine.py` disposition=`merge` rank=`62` total_score=`42.73` risk=`HIGH`

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
