"""AuditX analyzer registry."""

from analyzers import a1_reachability_orphaned
from analyzers import a2_ownership_boundary
from analyzers import a3_canon_drift
from analyzers import a4_schema_usage
from analyzers import a5_capability_misuse
from analyzers import a6_ui_parity_bypass
from analyzers import a7_legacy_contamination
from analyzers import a8_derived_freshness_smell
from analyzers import b1_duplicate_concept
from analyzers import b2_schema_shadowing
from analyzers import b3_capability_drift
from analyzers import b4_derived_artifact_contract
from analyzers import b5_cross_pack_entropy
from analyzers import b6_prompt_drift
from analyzers import b7_workspace_contamination
from analyzers import b8_blocker_recurrence
from analyzers import c1_security_boundary
from analyzers import c2_mode_flag_smell
from analyzers import c3_capability_bypass_smell
from analyzers import c4_terminology_misuse
from analyzers import c5_experience_profile_drift
from analyzers import c6_authority_bypass_smell
from analyzers import c7_lens_bypass_smell
from analyzers import c8_run_meta_input_smell
from analyzers import d1_constraint_drift
from analyzers import d2_seed_policy
from analyzers import e1_net_policy_drift
from analyzers import e2_truth_over_net_smell
from analyzers import e3_handshake_policy_bypass_smell
from analyzers import e4_authoritative_truth_leak
from analyzers import e5_cross_shard_write_smell
from analyzers import e6_shard_map_drift
from analyzers import e7_epistemic_leak_smell
from analyzers import e8_precision_leak_smell
from analyzers import e9_hidden_termination_smell
from analyzers import e10_nondeterministic_anti_cheat_smell
from analyzers import e11_ranked_policy_drift
from analyzers import e12_signature_bypass_smell
from analyzers import e13_player_special_case_smell
from analyzers import e14_control_bypass_smell
from analyzers import e15_collision_nondeterministic_smell
from analyzers import e16_movement_bypass_smell
from analyzers import e17_ownership_bypass_smell
from analyzers import e18_view_mode_bypass_smell
from analyzers import e19_watermark_missing_smell
from analyzers import e20_cosmetic_semantics_smell
from analyzers import e21_unauthorized_cosmetic_pack_smell
from analyzers import e22_memory_truth_leak_smell
from analyzers import e23_memory_nondeterminism_smell
from analyzers import e24_instrument_truth_leak_smell
from analyzers import e25_omniscient_map_smell
from analyzers import e26_diegetic_bypass_smell
from analyzers import e27_hidden_nondiegetic_window_smell
from analyzers import e28_precision_leak_on_refinement_smell
from analyzers import e29_hidden_state_leak_smell
from analyzers import e30_faction_orphan_smell
from analyzers import e31_territory_ownership_drift_smell
from analyzers import e32_cohort_leak_smell
from analyzers import e33_nondeterministic_cohort_mapping_smell
from analyzers import e34_order_bypass_smell
from analyzers import e35_role_escalation_smell
from analyzers import e36_render_truth_leak_smell
from analyzers import e37_hardcoded_representation_smell
from analyzers import e38_demography_leak_smell
from analyzers import e39_nondeterministic_rate_usage_smell
from analyzers import e40_physics_assumption_smell
from analyzers import e41_implicit_default_profile_smell
from analyzers import e42_unaccounted_violation_smell
from analyzers import e43_excessive_numeric_loss_smell
from analyzers import e44_wall_clock_time_usage_smell
from analyzers import e45_nondeterministic_checkpoint_smell
from analyzers import e46_transition_thrash_smell
from analyzers import e47_nondeterministic_arbitration_smell
from analyzers import e48_performance_nondeterminism_smell
from analyzers import e49_unbounded_micro_expansion_smell
from analyzers import e50_renderer_truth_leak_smell
from analyzers import e51_render_snapshot_misclassified_smell
from analyzers import e52_interaction_bypass_smell
from analyzers import e53_preview_info_leak_smell
from analyzers import e54_platform_leak_smell
from analyzers import e55_renderer_backend_truth_leak_smell
from analyzers import e56_raw_float_in_invariant_smell
from analyzers import e57_dimension_drift_smell
from analyzers import e58_hardcoded_periodic_table_smell
from analyzers import e59_material_mass_drift_smell
from analyzers import e60_hardcoded_blueprint_smell
from analyzers import e61_nondeterministic_graph_order_smell
from analyzers import e62_silent_shipment_smell
from analyzers import e63_nondeterministic_routing_smell
from analyzers import e64_silent_construction_smell
from analyzers import e65_missing_provenance_smell
from analyzers import e66_silent_failure_smell
from analyzers import e67_nondeterministic_hazard_smell
from analyzers import e68_micro_entity_leak_smell
from analyzers import e69_collapse_drift_smell
from analyzers import e70_uncommitted_macro_change_smell
from analyzers import e71_reenactment_leak_smell
from analyzers import e72_inspection_leak_smell
from analyzers import e73_unbounded_inspection_smell
from analyzers import e74_unbounded_work_smell
from analyzers import e75_thrash_smell
from analyzers import e76_hardcoded_interaction_smell
from analyzers import e77_surface_leak_smell
from analyzers import e78_tool_bypass_smell
from analyzers import e79_tool_truth_leak_smell
from analyzers import e80_task_nondeterminism_smell
from analyzers import e81_task_bypass_smell
from analyzers import e82_silent_batch_creation_smell
from analyzers import e83_port_truth_leak_smell
from analyzers import e84_graph_duplication_smell
from analyzers import e85_adhoc_scheduler_smell
from analyzers import e86_adhoc_state_machine_smell
from analyzers import e87_flow_bypass_smell
from analyzers import e88_routing_duplication_smell
from analyzers import e89_nondeterministic_routing_smell
from analyzers import e90_silent_flow_smell
from analyzers import e91_nondeterministic_flow_smell
from analyzers import e92_flow_bypass_ledger_smell
from analyzers import e93_adhoc_state_flag_smell
from analyzers import e94_duplicate_scheduler_smell
from analyzers import e95_hazard_logic_duplication_smell
from analyzers import e96_interior_occlusion_leak_smell
from analyzers import e97_duplicate_interior_graph_smell
from analyzers import e98_compartment_flow_duplication_smell
from analyzers import e99_instrument_truth_leak_smell
from analyzers import e100_interior_info_leak_smell
from analyzers import e101_alarm_truth_leak_smell
from analyzers import e102_pose_bypass_smell
from analyzers import e103_mount_bypass_smell
from analyzers import e104_direct_intent_bypass_smell
from analyzers import e105_legacy_reference_smell
from analyzers import e106_undeclared_subsystem_smell
from analyzers import e107_undeclared_schema_smell
from analyzers import e108_undeclared_registry_smell
from analyzers import e109_boundary_violation_analyzer
from analyzers import e110_tools_contamination_smell
from analyzers import e111_intent_bypass_smell
from analyzers import e112_legacy_import_smell
from analyzers import e113_deprecated_usage_smell
from analyzers import e114_adapter_missing_smell
from analyzers import e115_removed_still_referenced_smell
from analyzers import e116_macro_behavior_smell
from analyzers import e117_ir_nondeterminism_smell
from analyzers import e118_silent_downgrade_smell
from analyzers import e119_unlogged_refusal_smell
from analyzers import e120_direct_assembly_mutation_smell
from analyzers import e121_plan_bypass_smell
from analyzers import e122_silent_fidelity_downgrade_smell
from analyzers import e123_unbounded_cost_smell
from analyzers import e124_camera_bypass_smell
from analyzers import e125_type_branch_smell
from analyzers import e126_hidden_feature_flag_smell
from analyzers import e127_temp_modifier_smell
from analyzers import e128_effect_bypass_smell
from analyzers import e129_control_plane_bypass_smell
from analyzers import e130_hidden_privilege_escalation_smell
from analyzers import e131_silent_downgrade_smell
from analyzers import e132_missing_decision_log_smell
from analyzers import e133_spec_hardcode_smell
from analyzers import e134_spec_bypass_smell
from analyzers import e135_hidden_auto_formalize_smell
from analyzers import e136_inference_truth_mutation_smell
from analyzers import e137_structural_bypass_smell
from analyzers import e138_inline_strength_check_smell
from analyzers import e139_inline_friction_smell
from analyzers import e140_inline_temperature_smell
from analyzers import e141_weather_hack_smell
from analyzers import e142_mobility_special_case_smell
from analyzers import e143_direct_position_mutation_smell
from analyzers import e144_adhoc_speed_limit_smell
from analyzers import e145_geometry_mutation_bypass_smell
from analyzers import e146_hardcoded_track_spec_smell
from analyzers import e147_mobility_graph_duplication_smell
from analyzers import e148_switch_bypass_smell
from analyzers import e149_vehicle_hardcode_smell
from analyzers import e150_silent_teleport_smell
from analyzers import e151_adhoc_travel_smell
from analyzers import e152_silent_occupancy_change_smell
from analyzers import e153_inline_delay_modifier_smell
from analyzers import e154_derailment_bypass_smell
from analyzers import e155_direct_velocity_mutation_smell
from analyzers import e156_signal_bypass_smell
from analyzers import e157_adhoc_interlocking_smell
from analyzers import e158_inline_wear_smell
from analyzers import e159_maintenance_bypass_smell
from analyzers import e160_vehicle_interior_special_case_smell
from analyzers import e161_instrument_truth_leak_smell
from analyzers import e162_action_without_family_smell
from analyzers import e163_substrate_bypass_smell


ANALYZERS = (
    a1_reachability_orphaned,
    a2_ownership_boundary,
    a3_canon_drift,
    a4_schema_usage,
    a5_capability_misuse,
    a6_ui_parity_bypass,
    a7_legacy_contamination,
    a8_derived_freshness_smell,
    b1_duplicate_concept,
    b2_schema_shadowing,
    b3_capability_drift,
    b4_derived_artifact_contract,
    b5_cross_pack_entropy,
    b6_prompt_drift,
    b7_workspace_contamination,
    b8_blocker_recurrence,
    c1_security_boundary,
    c2_mode_flag_smell,
    c3_capability_bypass_smell,
    c4_terminology_misuse,
    c5_experience_profile_drift,
    c6_authority_bypass_smell,
    c7_lens_bypass_smell,
    c8_run_meta_input_smell,
    d1_constraint_drift,
    d2_seed_policy,
    e1_net_policy_drift,
    e2_truth_over_net_smell,
    e3_handshake_policy_bypass_smell,
    e4_authoritative_truth_leak,
    e5_cross_shard_write_smell,
    e6_shard_map_drift,
    e7_epistemic_leak_smell,
    e8_precision_leak_smell,
    e9_hidden_termination_smell,
    e10_nondeterministic_anti_cheat_smell,
    e11_ranked_policy_drift,
    e12_signature_bypass_smell,
    e13_player_special_case_smell,
    e14_control_bypass_smell,
    e15_collision_nondeterministic_smell,
    e16_movement_bypass_smell,
    e17_ownership_bypass_smell,
    e18_view_mode_bypass_smell,
    e19_watermark_missing_smell,
    e20_cosmetic_semantics_smell,
    e21_unauthorized_cosmetic_pack_smell,
    e22_memory_truth_leak_smell,
    e23_memory_nondeterminism_smell,
    e24_instrument_truth_leak_smell,
    e25_omniscient_map_smell,
    e26_diegetic_bypass_smell,
    e27_hidden_nondiegetic_window_smell,
    e28_precision_leak_on_refinement_smell,
    e29_hidden_state_leak_smell,
    e30_faction_orphan_smell,
    e31_territory_ownership_drift_smell,
    e32_cohort_leak_smell,
    e33_nondeterministic_cohort_mapping_smell,
    e34_order_bypass_smell,
    e35_role_escalation_smell,
    e36_render_truth_leak_smell,
    e37_hardcoded_representation_smell,
    e38_demography_leak_smell,
    e39_nondeterministic_rate_usage_smell,
    e40_physics_assumption_smell,
    e41_implicit_default_profile_smell,
    e42_unaccounted_violation_smell,
    e43_excessive_numeric_loss_smell,
    e44_wall_clock_time_usage_smell,
    e45_nondeterministic_checkpoint_smell,
    e46_transition_thrash_smell,
    e47_nondeterministic_arbitration_smell,
    e48_performance_nondeterminism_smell,
    e49_unbounded_micro_expansion_smell,
    e50_renderer_truth_leak_smell,
    e51_render_snapshot_misclassified_smell,
    e52_interaction_bypass_smell,
    e53_preview_info_leak_smell,
    e54_platform_leak_smell,
    e55_renderer_backend_truth_leak_smell,
    e56_raw_float_in_invariant_smell,
    e57_dimension_drift_smell,
    e58_hardcoded_periodic_table_smell,
    e59_material_mass_drift_smell,
    e60_hardcoded_blueprint_smell,
    e61_nondeterministic_graph_order_smell,
    e62_silent_shipment_smell,
    e63_nondeterministic_routing_smell,
    e64_silent_construction_smell,
    e65_missing_provenance_smell,
    e66_silent_failure_smell,
    e67_nondeterministic_hazard_smell,
    e68_micro_entity_leak_smell,
    e69_collapse_drift_smell,
    e70_uncommitted_macro_change_smell,
    e71_reenactment_leak_smell,
    e72_inspection_leak_smell,
    e73_unbounded_inspection_smell,
    e74_unbounded_work_smell,
    e75_thrash_smell,
    e76_hardcoded_interaction_smell,
    e77_surface_leak_smell,
    e78_tool_bypass_smell,
    e79_tool_truth_leak_smell,
    e80_task_nondeterminism_smell,
    e81_task_bypass_smell,
    e82_silent_batch_creation_smell,
    e83_port_truth_leak_smell,
    e84_graph_duplication_smell,
    e85_adhoc_scheduler_smell,
    e86_adhoc_state_machine_smell,
    e87_flow_bypass_smell,
    e88_routing_duplication_smell,
    e89_nondeterministic_routing_smell,
    e90_silent_flow_smell,
    e91_nondeterministic_flow_smell,
    e92_flow_bypass_ledger_smell,
    e93_adhoc_state_flag_smell,
    e94_duplicate_scheduler_smell,
    e95_hazard_logic_duplication_smell,
    e96_interior_occlusion_leak_smell,
    e97_duplicate_interior_graph_smell,
    e98_compartment_flow_duplication_smell,
    e99_instrument_truth_leak_smell,
    e100_interior_info_leak_smell,
    e101_alarm_truth_leak_smell,
    e102_pose_bypass_smell,
    e103_mount_bypass_smell,
    e104_direct_intent_bypass_smell,
    e105_legacy_reference_smell,
    e106_undeclared_subsystem_smell,
    e107_undeclared_schema_smell,
    e108_undeclared_registry_smell,
    e109_boundary_violation_analyzer,
    e110_tools_contamination_smell,
    e111_intent_bypass_smell,
    e112_legacy_import_smell,
    e113_deprecated_usage_smell,
    e114_adapter_missing_smell,
    e115_removed_still_referenced_smell,
    e116_macro_behavior_smell,
    e117_ir_nondeterminism_smell,
    e118_silent_downgrade_smell,
    e119_unlogged_refusal_smell,
    e120_direct_assembly_mutation_smell,
    e121_plan_bypass_smell,
    e122_silent_fidelity_downgrade_smell,
    e123_unbounded_cost_smell,
    e124_camera_bypass_smell,
    e125_type_branch_smell,
    e126_hidden_feature_flag_smell,
    e127_temp_modifier_smell,
    e128_effect_bypass_smell,
    e129_control_plane_bypass_smell,
    e130_hidden_privilege_escalation_smell,
    e131_silent_downgrade_smell,
    e132_missing_decision_log_smell,
    e133_spec_hardcode_smell,
    e134_spec_bypass_smell,
    e135_hidden_auto_formalize_smell,
    e136_inference_truth_mutation_smell,
    e137_structural_bypass_smell,
    e138_inline_strength_check_smell,
    e139_inline_friction_smell,
    e140_inline_temperature_smell,
    e141_weather_hack_smell,
    e142_mobility_special_case_smell,
    e143_direct_position_mutation_smell,
    e144_adhoc_speed_limit_smell,
    e145_geometry_mutation_bypass_smell,
    e146_hardcoded_track_spec_smell,
    e147_mobility_graph_duplication_smell,
    e148_switch_bypass_smell,
    e149_vehicle_hardcode_smell,
    e150_silent_teleport_smell,
    e151_adhoc_travel_smell,
    e152_silent_occupancy_change_smell,
    e153_inline_delay_modifier_smell,
    e154_derailment_bypass_smell,
    e155_direct_velocity_mutation_smell,
    e156_signal_bypass_smell,
    e157_adhoc_interlocking_smell,
    e158_inline_wear_smell,
    e159_maintenance_bypass_smell,
    e160_vehicle_interior_special_case_smell,
    e161_instrument_truth_leak_smell,
    e162_action_without_family_smell,
    e163_substrate_bypass_smell,
)


def run_analyzers(graph, repo_root, changed_files=None):
    findings = []
    for analyzer in ANALYZERS:
        findings.extend(analyzer.run(graph, repo_root, changed_files=changed_files))
    return findings
