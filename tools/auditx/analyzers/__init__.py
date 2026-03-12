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
from analyzers import e164_direct_message_smell
from analyzers import e165_knowledge_bypass_smell
from analyzers import e166_signal_routing_bypass_smell
from analyzers import e167_nondeterministic_queue_order_smell
from analyzers import e168_direct_knowledge_mutation_smell
from analyzers import e169_broadcast_bypass_smell
from analyzers import e170_adhoc_loss_smell
from analyzers import e171_silent_corruption_smell
from analyzers import e172_truth_based_trust_smell
from analyzers import e173_unlogged_trust_change_smell
from analyzers import e174_direct_schedule_mutation_smell
from analyzers import e175_institutional_bypass_smell
from analyzers import e176_affordance_gap_smell
from analyzers import e177_inline_protection_smell
from analyzers import e178_missing_failsafe_smell
from analyzers import e179_inline_response_curve_smell
from analyzers import e180_model_bypass_smell
from analyzers import e181_coupled_channel_hack_smell
from analyzers import e182_bundle_bypass_smell
from analyzers import e183_electric_special_case_smell
from analyzers import e184_breaker_bypass_smell
from analyzers import e185_inline_power_loss_smell
from analyzers import e186_direct_flow_mutation_smell
from analyzers import e187_inline_trip_smell
from analyzers import e188_fault_bypass_smell
from analyzers import e189_unlogged_trip_smell
from analyzers import e190_omniscient_electrical_ui_leak_smell
from analyzers import e191_direct_breaker_toggle_smell
from analyzers import e192_infinite_cascade_smell
from analyzers import e193_unbudgeted_solve_smell
from analyzers import e194_silent_degrade_smell
from analyzers import e195_heat_loss_bypass_smell
from analyzers import e196_thermal_bypass_smell
from analyzers import e197_inline_phase_change_smell
from analyzers import e198_inline_cure_smell
from analyzers import e199_inline_cooling_smell
from analyzers import e200_direct_temperature_ambient_smell
from analyzers import e201_inline_fire_logic_smell
from analyzers import e202_unbounded_spread_smell
from analyzers import e203_unbudgeted_therm_solve_smell
from analyzers import e204_silent_therm_degrade_smell
from analyzers import e205_energy_bypass_smell
from analyzers import e206_momentum_bypass_smell
from analyzers import e207_magic_silent_violation_smell
from analyzers import e208_direct_velocity_write_smell
from analyzers import e209_inline_acceleration_smell
from analyzers import e210_direct_field_write_smell
from analyzers import e211_unregistered_field_smell
from analyzers import e212_direct_energy_write_smell
from analyzers import e213_missing_ledger_entry_smell
from analyzers import e214_inline_degradation_smell
from analyzers import e215_entropy_bypass_smell
from analyzers import e216_missing_tier_contract_smell
from analyzers import e217_undeclared_coupling_smell
from analyzers import e218_missing_explain_contract_smell
from analyzers import e219_inline_pressure_smell
from analyzers import e220_adhoc_valve_smell
from analyzers import e221_inline_burst_logic_smell
from analyzers import e222_direct_interior_mass_write_smell
from analyzers import e223_unbudgeted_fluid_solve_smell
from analyzers import e224_silent_leak_smell
from analyzers import e225_infinite_leak_loop_smell
from analyzers import e226_cost_model_missing_smell
from analyzers import e227_inline_field_modifier_smell
from analyzers import e228_cross_shard_field_access_smell
from analyzers import e229_wallclock_use_smell
from analyzers import e230_future_receipt_reference_smell
from analyzers import e231_undeclared_temporal_domain_smell
from analyzers import e232_direct_time_write_smell
from analyzers import e233_implicit_civil_time_smell
from analyzers import e234_implicit_clock_sync_smell
from analyzers import e235_direct_domain_time_write_smell
from analyzers import e236_implicit_float_usage_smell
from analyzers import e237_missing_tolerance_smell
from analyzers import e238_direct_division_without_round_smell
from analyzers import e239_canonical_artifact_compaction_smell
from analyzers import e240_unclassified_artifact_smell
from analyzers import e241_missing_compaction_marker_smell
from analyzers import e242_inline_fuel_burn_smell
from analyzers import e243_unregistered_combustion_smell
from analyzers import e244_inline_yield_logic_smell
from analyzers import e245_recipe_bypass_smell
from analyzers import e248_silent_reaction_smell
from analyzers import e249_unbudgeted_reaction_loop_smell
from analyzers import e250_direct_smoke_visual_hack_smell
from analyzers import e251_unregistered_pollutant_smell
from analyzers import e252_direct_concentration_write_smell
from analyzers import e253_unbounded_cell_loop_smell
from analyzers import e254_direct_exposure_write_smell
from analyzers import e255_omniscient_pollution_ui_leak_smell
from analyzers import e256_unbudgeted_dispersion_smell
from analyzers import e257_silent_exposure_smell
from analyzers import e258_implicit_system_collapse_smell
from analyzers import e259_hidden_system_state_smell
from analyzers import e260_missing_interface_descriptor_smell
from analyzers import e261_missing_invariant_template_smell
from analyzers import e262_macro_model_signature_mismatch_smell
from analyzers import e263_capsule_bypass_smell
from analyzers import e264_undeclared_macro_model_smell
from analyzers import e265_silent_forced_expand_smell
from analyzers import e266_unlogged_tier_change_smell
from analyzers import e267_template_bypass_smell
from analyzers import e268_unversioned_template_smell
from analyzers import e269_direct_spec_bypass_smell
from analyzers import e270_unlogged_certificate_issue_smell
from analyzers import e271_hidden_failure_logic_smell
from analyzers import e272_unlogged_shutdown_smell
from analyzers import e273_missing_system_explain_contract_smell
from analyzers import e274_omniscient_explain_leak_smell
from analyzers import e275_unbounded_expand_smell
from analyzers import e276_silent_collapse_smell
from analyzers import e277_invariant_check_skipped_smell
from analyzers import e278_custom_compilation_smell
from analyzers import e279_missing_equivalence_proof_smell
from analyzers import e280_output_depends_on_undeclared_field_smell
from analyzers import e281_unregistered_workflow_smell
from analyzers import e282_process_step_without_cost_smell
from analyzers import e283_inline_yield_smell
from analyzers import e284_defect_flag_bypass_smell
from analyzers import e285_implicit_qc_logic_smell
from analyzers import e286_nondeterministic_sampling_smell
from analyzers import e287_hidden_unlock_smell
from analyzers import e288_undeclared_maturity_transition_smell
from analyzers import e289_silent_capsule_execution_smell
from analyzers import e290_capsule_used_out_of_domain_smell
from analyzers import e291_silent_drift_smell
from analyzers import e292_capsule_used_while_invalid_smell
from analyzers import e293_magic_unlock_smell
from analyzers import e294_undeclared_inference_smell
from analyzers import e295_direct_binary_write_smell
from analyzers import e296_signing_bypass_smell
from analyzers import e297_silent_process_execution_smell
from analyzers import e298_unbudgeted_process_loop_smell
from analyzers import e299_capsule_used_while_invalid_smell
from analyzers import e300_orphan_feature_smell
from analyzers import e301_missing_reference_evaluator_smell
from analyzers import e302_omniscient_readout_smell
from analyzers import e303_missing_instrumentation_surface_smell
from analyzers import e304_silent_override_smell
from analyzers import e305_unmetered_loop_smell
from analyzers import e306_silent_throttle_smell
from analyzers import e307_electrical_bias_in_logic_smell
from analyzers import e308_unmetered_logic_compute_smell
from analyzers import e309_omniscient_logic_debug_smell
from analyzers import e310_direct_signal_mutation_smell
from analyzers import e311_carrier_bias_smell
from analyzers import e312_hardcoded_logic_behavior_smell
from analyzers import e313_missing_state_vector_smell
from analyzers import e314_adhoc_wiring_smell
from analyzers import e315_unvalidated_network_eval_smell
from analyzers import e316_unmetered_logic_eval_smell
from analyzers import e317_commit_phase_bypass_smell
from analyzers import e318_implicit_timing_assumption_smell
from analyzers import e319_silent_compiled_invalidation_smell
from analyzers import e320_missing_logic_equivalence_proof_smell
from analyzers import e321_truth_leak_via_debug_smell
from analyzers import e322_unbounded_trace_smell
from analyzers import e323_random_failure_smell
from analyzers import e324_silent_noise_smell
from analyzers import e325_security_bypass_smell
from analyzers import e326_nondeterministic_arbitration_smell
from analyzers import e327_protocol_security_bypass_smell
from analyzers import e328_protocol_bypass_smell
from analyzers import e329_unbounded_logic_loop_smell
from analyzers import e330_silent_logic_throttle_smell
from analyzers import e331_raw_xyz_distance_smell
from analyzers import e332_hardcoded_dimension_smell
from analyzers import e333_projection_truth_leak_smell
from analyzers import e334_adhoc_spatial_key_smell
from analyzers import e335_nondeterministic_local_index_smell
from analyzers import e336_raw_global_coord_smell
from analyzers import e337_render_writes_truth_smell
from analyzers import e338_raw_sqrt_usage_smell
from analyzers import e339_hardcoded_distance_smell
from analyzers import e340_raw_field_grid_smell
from analyzers import e341_field_sample_bypass_smell
from analyzers import e342_map_truth_leak_smell
from analyzers import e343_uninstrumented_map_access_smell
from analyzers import e344_nondeterministic_path_smell
from analyzers import e345_adhoc_heuristic_smell
from analyzers import e346_direct_geometry_write_smell
from analyzers import e347_unlogged_terrain_edit_smell
from analyzers import e348_unnamed_rng_worldgen_smell
from analyzers import e349_adhoc_worldgen_smell
from analyzers import e350_silent_identity_change_smell
from analyzers import e351_nondeterministic_merge_smell
from analyzers import e352_nondeterministic_distance_smell
from analyzers import e353_hardcoded_pack_path_smell
from analyzers import e354_missing_pack_lock_smell
from analyzers import e355_catalog_dependency_smell
from analyzers import e356_eager_galaxy_instantiation_smell
from analyzers import e357_direct_system_spawn_smell
from analyzers import e358_nondeterministic_query_smell
from analyzers import e359_nondeterministic_orbit_smell
from analyzers import e360_unbounded_generation_smell
from analyzers import e361_hardcoded_earth_gen_smell
from analyzers import e362_eager_tile_generation_smell
from analyzers import e363_large_data_in_pin_pack_smell
from analyzers import e364_identity_override_smell
from analyzers import e365_hardcoded_dem_reference_smell
from analyzers import e366_nondeterministic_noise_smell
from analyzers import e367_asset_dependency_smell
from analyzers import e368_direct_position_write_smell
from analyzers import e369_ui_truth_leak_smell
from analyzers import e370_uninstrumented_inspect_smell
from analyzers import e371_random_river_smell
from analyzers import e372_recursion_without_bound_smell
from analyzers import e373_float_trig_smell
from analyzers import e374_nondeterministic_climate_smell
from analyzers import e375_nondeterministic_tide_smell
from analyzers import e376_truth_read_in_renderer_smell
from analyzers import e377_nondeterministic_starfield_smell
from analyzers import e378_renderer_truth_leak_smell
from analyzers import e379_unbounded_shadow_sampling_smell
from analyzers import e380_nondeterministic_collision_smell
from analyzers import e381_nondeterministic_wind_smell
from analyzers import e382_water_sim_leak_smell
from analyzers import e383_nondeterministic_view_smell
from analyzers import e384_truth_leak_smell
from analyzers import e385_unbounded_update_loop_smell
from analyzers import e386_behavior_without_contract_smell
from analyzers import e387_silent_semantic_change_smell
from analyzers import e388_missing_migration_plan_smell
from analyzers import e389_missing_contract_bundle_smell
from analyzers import e390_contract_mismatch_not_refused_smell
from analyzers import e393_silent_conflict_resolution_smell
from analyzers import e402_wallclock_tick_smell
from analyzers import e403_intent_without_authority_smell
from analyzers import e404_wallclock_timeout_smell
from analyzers import e405_ungated_authority_spawn_smell
from analyzers import e413_missing_interop_test_smell
from analyzers import e414_missing_pack_compat_smell
from analyzers import e415_pack_loaded_without_compat_validation_smell
from analyzers import e416_pack_loaded_without_verification_smell
from analyzers import e417_nondeterministic_pack_order_smell
from analyzers import e418_missing_format_version_smell
from analyzers import e419_silent_migration_smell
from analyzers import e420_ad_hoc_entry_point_smell
from analyzers import e421_xstack_runtime_dependency_smell
from analyzers import e422_ad_hoc_command_smell
from analyzers import e423_unstructured_error_smell
from analyzers import e424_printf_log_smell
from analyzers import e425_wallclock_in_sim_smell
from analyzers import e426_tui_truth_leak_smell
from analyzers import e427_wallclock_refresh_smell
from analyzers import e428_ad_hoc_ipc_protocol_smell
from analyzers import e429_unnegotiated_attach_smell
from analyzers import e430_nondeterministic_supervisor_smell
from analyzers import e431_wallclock_polling_smell
from analyzers import e432_nondeterministic_bundle_ordering_smell
from analyzers import e433_secrets_in_bundle_smell
from analyzers import e434_path_dependent_install_smell
from analyzers import e435_binary_without_descriptor_smell
from analyzers import e436_instance_without_lock_smell
from analyzers import e437_save_locked_to_instance_smell
from analyzers import e438_save_without_contract_pin_smell
from analyzers import e439_silent_save_upgrade_smell
from analyzers import e440_manifest_missing_smell
from analyzers import e441_artifact_hash_mismatch_smell
from analyzers import e442_silent_provider_selection_smell
from analyzers import e443_pack_id_collision_smell
from analyzers import e444_nondeterministic_bundle_smell
from analyzers import e445_smoke_suite_missing_smell
from analyzers import e447_platform_dependent_behavior_smell
from analyzers import e448_non_canonical_serialization_smell
from analyzers import e449_missing_stability_marker_smell
from analyzers import e450_stable_changed_without_contract_bump_smell
from analyzers import e451_provisional_without_replacement_smell
from analyzers import e452_mixed_tick_width_smell


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
    e164_direct_message_smell,
    e165_knowledge_bypass_smell,
    e166_signal_routing_bypass_smell,
    e167_nondeterministic_queue_order_smell,
    e168_direct_knowledge_mutation_smell,
    e169_broadcast_bypass_smell,
    e170_adhoc_loss_smell,
    e171_silent_corruption_smell,
    e172_truth_based_trust_smell,
    e173_unlogged_trust_change_smell,
    e174_direct_schedule_mutation_smell,
    e175_institutional_bypass_smell,
    e176_affordance_gap_smell,
    e177_inline_protection_smell,
    e178_missing_failsafe_smell,
    e179_inline_response_curve_smell,
    e180_model_bypass_smell,
    e181_coupled_channel_hack_smell,
    e182_bundle_bypass_smell,
    e183_electric_special_case_smell,
    e184_breaker_bypass_smell,
    e185_inline_power_loss_smell,
    e186_direct_flow_mutation_smell,
    e187_inline_trip_smell,
    e188_fault_bypass_smell,
    e189_unlogged_trip_smell,
    e190_omniscient_electrical_ui_leak_smell,
    e191_direct_breaker_toggle_smell,
    e192_infinite_cascade_smell,
    e193_unbudgeted_solve_smell,
    e194_silent_degrade_smell,
    e195_heat_loss_bypass_smell,
    e196_thermal_bypass_smell,
    e197_inline_phase_change_smell,
    e198_inline_cure_smell,
    e199_inline_cooling_smell,
    e200_direct_temperature_ambient_smell,
    e201_inline_fire_logic_smell,
    e202_unbounded_spread_smell,
    e203_unbudgeted_therm_solve_smell,
    e204_silent_therm_degrade_smell,
    e205_energy_bypass_smell,
    e206_momentum_bypass_smell,
    e207_magic_silent_violation_smell,
    e208_direct_velocity_write_smell,
    e209_inline_acceleration_smell,
    e210_direct_field_write_smell,
    e211_unregistered_field_smell,
    e212_direct_energy_write_smell,
    e213_missing_ledger_entry_smell,
    e214_inline_degradation_smell,
    e215_entropy_bypass_smell,
    e216_missing_tier_contract_smell,
    e217_undeclared_coupling_smell,
    e218_missing_explain_contract_smell,
    e219_inline_pressure_smell,
    e220_adhoc_valve_smell,
    e221_inline_burst_logic_smell,
    e222_direct_interior_mass_write_smell,
    e223_unbudgeted_fluid_solve_smell,
    e224_silent_leak_smell,
    e225_infinite_leak_loop_smell,
    e226_cost_model_missing_smell,
    e227_inline_field_modifier_smell,
    e228_cross_shard_field_access_smell,
    e229_wallclock_use_smell,
    e230_future_receipt_reference_smell,
    e231_undeclared_temporal_domain_smell,
    e232_direct_time_write_smell,
    e233_implicit_civil_time_smell,
    e234_implicit_clock_sync_smell,
    e235_direct_domain_time_write_smell,
    e236_implicit_float_usage_smell,
    e237_missing_tolerance_smell,
    e238_direct_division_without_round_smell,
    e239_canonical_artifact_compaction_smell,
    e240_unclassified_artifact_smell,
    e241_missing_compaction_marker_smell,
    e242_inline_fuel_burn_smell,
    e243_unregistered_combustion_smell,
    e244_inline_yield_logic_smell,
    e245_recipe_bypass_smell,
    e248_silent_reaction_smell,
    e249_unbudgeted_reaction_loop_smell,
    e250_direct_smoke_visual_hack_smell,
    e251_unregistered_pollutant_smell,
    e252_direct_concentration_write_smell,
    e253_unbounded_cell_loop_smell,
    e254_direct_exposure_write_smell,
    e255_omniscient_pollution_ui_leak_smell,
    e256_unbudgeted_dispersion_smell,
    e257_silent_exposure_smell,
    e258_implicit_system_collapse_smell,
    e259_hidden_system_state_smell,
    e260_missing_interface_descriptor_smell,
    e261_missing_invariant_template_smell,
    e262_macro_model_signature_mismatch_smell,
    e263_capsule_bypass_smell,
    e264_undeclared_macro_model_smell,
    e265_silent_forced_expand_smell,
    e266_unlogged_tier_change_smell,
    e267_template_bypass_smell,
    e268_unversioned_template_smell,
    e269_direct_spec_bypass_smell,
    e270_unlogged_certificate_issue_smell,
    e271_hidden_failure_logic_smell,
    e272_unlogged_shutdown_smell,
    e273_missing_system_explain_contract_smell,
    e274_omniscient_explain_leak_smell,
    e275_unbounded_expand_smell,
    e276_silent_collapse_smell,
    e277_invariant_check_skipped_smell,
    e278_custom_compilation_smell,
    e279_missing_equivalence_proof_smell,
    e280_output_depends_on_undeclared_field_smell,
    e281_unregistered_workflow_smell,
    e282_process_step_without_cost_smell,
    e283_inline_yield_smell,
    e284_defect_flag_bypass_smell,
    e285_implicit_qc_logic_smell,
    e286_nondeterministic_sampling_smell,
    e287_hidden_unlock_smell,
    e288_undeclared_maturity_transition_smell,
    e289_silent_capsule_execution_smell,
    e290_capsule_used_out_of_domain_smell,
    e291_silent_drift_smell,
    e292_capsule_used_while_invalid_smell,
    e293_magic_unlock_smell,
    e294_undeclared_inference_smell,
    e295_direct_binary_write_smell,
    e296_signing_bypass_smell,
    e297_silent_process_execution_smell,
    e298_unbudgeted_process_loop_smell,
    e299_capsule_used_while_invalid_smell,
    e300_orphan_feature_smell,
    e301_missing_reference_evaluator_smell,
    e302_omniscient_readout_smell,
    e303_missing_instrumentation_surface_smell,
    e304_silent_override_smell,
    e305_unmetered_loop_smell,
    e306_silent_throttle_smell,
    e307_electrical_bias_in_logic_smell,
    e308_unmetered_logic_compute_smell,
    e309_omniscient_logic_debug_smell,
    e310_direct_signal_mutation_smell,
    e311_carrier_bias_smell,
    e312_hardcoded_logic_behavior_smell,
    e313_missing_state_vector_smell,
    e314_adhoc_wiring_smell,
    e315_unvalidated_network_eval_smell,
    e316_unmetered_logic_eval_smell,
    e317_commit_phase_bypass_smell,
    e318_implicit_timing_assumption_smell,
    e319_silent_compiled_invalidation_smell,
    e320_missing_logic_equivalence_proof_smell,
    e321_truth_leak_via_debug_smell,
    e322_unbounded_trace_smell,
    e323_random_failure_smell,
    e324_silent_noise_smell,
    e325_security_bypass_smell,
    e326_nondeterministic_arbitration_smell,
    e327_protocol_security_bypass_smell,
    e328_protocol_bypass_smell,
    e329_unbounded_logic_loop_smell,
    e330_silent_logic_throttle_smell,
    e331_raw_xyz_distance_smell,
    e332_hardcoded_dimension_smell,
    e333_projection_truth_leak_smell,
    e334_adhoc_spatial_key_smell,
    e335_nondeterministic_local_index_smell,
    e336_raw_global_coord_smell,
    e337_render_writes_truth_smell,
    e338_raw_sqrt_usage_smell,
    e339_hardcoded_distance_smell,
    e340_raw_field_grid_smell,
    e341_field_sample_bypass_smell,
    e342_map_truth_leak_smell,
    e343_uninstrumented_map_access_smell,
    e344_nondeterministic_path_smell,
    e345_adhoc_heuristic_smell,
    e346_direct_geometry_write_smell,
    e347_unlogged_terrain_edit_smell,
    e348_unnamed_rng_worldgen_smell,
    e349_adhoc_worldgen_smell,
    e350_silent_identity_change_smell,
    e351_nondeterministic_merge_smell,
    e352_nondeterministic_distance_smell,
    e353_hardcoded_pack_path_smell,
    e354_missing_pack_lock_smell,
    e355_catalog_dependency_smell,
    e356_eager_galaxy_instantiation_smell,
    e357_direct_system_spawn_smell,
    e358_nondeterministic_query_smell,
    e359_nondeterministic_orbit_smell,
    e360_unbounded_generation_smell,
    e361_hardcoded_earth_gen_smell,
    e362_eager_tile_generation_smell,
    e363_large_data_in_pin_pack_smell,
    e364_identity_override_smell,
    e365_hardcoded_dem_reference_smell,
    e366_nondeterministic_noise_smell,
    e367_asset_dependency_smell,
    e368_direct_position_write_smell,
    e369_ui_truth_leak_smell,
    e370_uninstrumented_inspect_smell,
    e371_random_river_smell,
    e372_recursion_without_bound_smell,
    e373_float_trig_smell,
    e374_nondeterministic_climate_smell,
    e375_nondeterministic_tide_smell,
    e376_truth_read_in_renderer_smell,
    e377_nondeterministic_starfield_smell,
    e378_renderer_truth_leak_smell,
    e379_unbounded_shadow_sampling_smell,
    e380_nondeterministic_collision_smell,
    e381_nondeterministic_wind_smell,
    e382_water_sim_leak_smell,
    e383_nondeterministic_view_smell,
    e384_truth_leak_smell,
    e385_unbounded_update_loop_smell,
    e386_behavior_without_contract_smell,
    e387_silent_semantic_change_smell,
    e388_missing_migration_plan_smell,
    e389_missing_contract_bundle_smell,
    e390_contract_mismatch_not_refused_smell,
    e393_silent_conflict_resolution_smell,
    e402_wallclock_tick_smell,
    e403_intent_without_authority_smell,
    e404_wallclock_timeout_smell,
    e405_ungated_authority_spawn_smell,
    e413_missing_interop_test_smell,
    e414_missing_pack_compat_smell,
    e415_pack_loaded_without_compat_validation_smell,
    e416_pack_loaded_without_verification_smell,
    e417_nondeterministic_pack_order_smell,
    e418_missing_format_version_smell,
    e419_silent_migration_smell,
    e420_ad_hoc_entry_point_smell,
    e421_xstack_runtime_dependency_smell,
    e422_ad_hoc_command_smell,
    e423_unstructured_error_smell,
    e424_printf_log_smell,
    e425_wallclock_in_sim_smell,
    e426_tui_truth_leak_smell,
    e427_wallclock_refresh_smell,
    e428_ad_hoc_ipc_protocol_smell,
    e429_unnegotiated_attach_smell,
    e430_nondeterministic_supervisor_smell,
    e431_wallclock_polling_smell,
    e432_nondeterministic_bundle_ordering_smell,
    e433_secrets_in_bundle_smell,
    e434_path_dependent_install_smell,
    e435_binary_without_descriptor_smell,
    e436_instance_without_lock_smell,
    e437_save_locked_to_instance_smell,
    e438_save_without_contract_pin_smell,
    e439_silent_save_upgrade_smell,
    e440_manifest_missing_smell,
    e441_artifact_hash_mismatch_smell,
    e442_silent_provider_selection_smell,
    e443_pack_id_collision_smell,
    e444_nondeterministic_bundle_smell,
    e445_smoke_suite_missing_smell,
    e447_platform_dependent_behavior_smell,
    e448_non_canonical_serialization_smell,
    e449_missing_stability_marker_smell,
    e450_stable_changed_without_contract_bump_smell,
    e451_provisional_without_replacement_smell,
    e452_mixed_tick_width_smell,
)


def run_analyzers(graph, repo_root, changed_files=None):
    findings = []
    for analyzer in ANALYZERS:
        findings.extend(analyzer.run(graph, repo_root, changed_files=changed_files))
    return findings
