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
)


def run_analyzers(graph, repo_root, changed_files=None):
    findings = []
    for analyzer in ANALYZERS:
        findings.extend(analyzer.run(graph, repo_root, changed_files=changed_files))
    return findings
