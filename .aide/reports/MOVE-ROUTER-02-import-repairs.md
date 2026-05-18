Status: DERIVED
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-02

# MOVE-ROUTER-02 Import Repairs

## Summary

| Metric | Count |
| --- | ---: |
| `python_files_scanned` | 4010 |
| `files_changed` | 74 |
| `import_replacements` | 76 |
| `remaining_old_imports` | 0 |
| `promoted_quarantine_packages` | 3 |
| `shims_created` | 0 |

## Changed Files

- `apps/client/interaction/interaction_dispatch.py`
- `apps/server/server_boot.py`
- `content/packs/compatibility_payload/pack_verification_pipeline.py`
- `tools/import/import_engine.py`
- `engine/time/time_mapping_engine.py`
- `game/domain/chemistry/degradation/degradation_engine.py`
- `game/domain/electricity/power_network_engine.py`
- `game/domain/fields/field_engine.py`
- `game/domain/fluids/network/fluid_network_engine.py`
- `game/domain/logic/eval/propagate_engine.py`
- `game/domain/mechanics/structural_graph_engine.py`
- `game/domain/mobility/maintenance/wear_engine.py`
- `game/domain/mobility/micro/constrained_motion_solver.py`
- `game/domain/mobility/traffic/traffic_engine.py`
- `game/domain/mobility/travel/travel_engine.py`
- `game/domain/processes/capsules/capsule_builder.py`
- `game/domain/processes/process_run_engine.py`
- `game/domain/signals/institutions/dispatch_engine.py`
- `game/domain/signals/trust/trust_engine.py`
- `game/domain/systems/certification/system_cert_engine.py`
- `game/domain/systems/macro/macro_capsule_engine.py`
- `game/domain/thermal/network/thermal_network_engine.py`
- `tools/release/update_resolver.py`
- `tools/control/tool_determinism_compare.py`
- `tools/control/tool_global_control_stress.py`
- `tools/control/tool_run_control_stress.py`
- `tools/release/dist/dist_tree_common.py`
- `tools/governance/governance_model_common.py`
- `tools/mvp/runtime_bundle.py`
- `tools/release/archive_policy_common.py`
- `tools/release/offline_archive_common.py`
- `tools/release/update_model_common.py`
- `tools/repo/meta/reference/reference_engine.py`
- `tools/setup/setup_cli.py`
- `tools/xstack/pack_loader/loader.py`
- `tools/xstack/registry_compile/compiler.py`
- `tools/xstack/session_create.py`
- `tools/xstack/sessionx/creator.py`
- `tools/xstack/sessionx/process_runtime.py`
- `tools/xstack/sessionx/runner.py`
- `tools/xstack/sessionx/script_runner.py`
- `tools/xstack/testx/tests/control_ir_testlib.py`
- `tools/xstack/testx/tests/governance_testlib.py`
- `tools/xstack/testx/tests/sys5_testlib.py`
- `tools/xstack/testx/tests/test_budget_degrade_stable.py`
- `tools/xstack/testx/tests/test_cache_reuse_by_inputs_hash.py`
- `tools/xstack/testx/tests/test_civil_time_mapping_deterministic.py`
- `tools/xstack/testx/tests/test_control_determinism_lockstep.py`
- `tools/xstack/testx/tests/test_control_plane_enforces_template_requirements.py`
- `tools/xstack/testx/tests/test_control_policy_blocks_forbidden_action.py`
- `tools/xstack/testx/tests/test_control_resolution_deterministic.py`
- `tools/xstack/testx/tests/test_control_resolution_uses_capability.py`
- `tools/xstack/testx/tests/test_control_save_compat_replay.py`
- `tools/xstack/testx/tests/test_cross_platform_time_hash_match.py`
- `tools/xstack/testx/tests/test_decision_log_emitted.py`
- `tools/xstack/testx/tests/test_decision_log_hash_stable_across_peers.py`
- `tools/xstack/testx/tests/test_drift_deterministic.py`
- `tools/xstack/testx/tests/test_effect_influences_control_resolution.py`
- `tools/xstack/testx/tests/test_freecam_forbidden_in_ranked.py`
- `tools/xstack/testx/tests/test_inputs_hash_deterministic.py`
- `tools/xstack/testx/tests/test_ir_compilation_deterministic.py`
- `tools/xstack/testx/tests/test_ir_cost_budget_enforced.py`
- `tools/xstack/testx/tests/test_ir_rejects_forbidden_op.py`
- `tools/xstack/testx/tests/test_ir_replay_deterministic.py`
- `tools/xstack/testx/tests/test_ir_verification_deterministic.py`
- `tools/xstack/testx/tests/test_model_binding_order_deterministic.py`
- `tools/xstack/testx/tests/test_phase_transition_trigger_deterministic.py`
- `tools/xstack/testx/tests/test_proper_time_mapping_deterministic.py`
- `tools/xstack/testx/tests/test_ranked_forbids_meta_actions.py`
- `tools/xstack/testx/tests/test_ranked_no_meta_override.py`
- `tools/xstack/testx/tests/test_replay_cannot_mutate_truth.py`
- `tools/xstack/testx/tests/test_replay_mode_readonly.py`
- `tools/xstack/testx/tests/test_rng_usage_only_when_declared.py`
- `tools/xstack/testx/tests/test_spec_registry_valid.py`

## Remaining Old Imports

None detected in active non-archive Python files.
