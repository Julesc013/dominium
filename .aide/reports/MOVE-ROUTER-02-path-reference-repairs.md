Status: DERIVED
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-02

# MOVE-ROUTER-02 Path Reference Repairs

## Summary

| Metric | Count |
| --- | ---: |
| `files_with_matches` | 1578 |
| `files_changed` | 1171 |
| `reference_replacements` | 33316 |
| `quarantine_references_preserved` | 3534 |
| `audit_evidence_files_restored` | 377 |
| `audit_evidence_replacements_reverted` | 5448 |

## Changed Files

- `AGENTS.md`
- `CONTRIBUTING.md`
- `apps/client/main_client.c`
- `apps/client/interaction/inspection_overlays.py`
- `apps/client/interaction/interaction_dispatch.py`
- `apps/client/interaction/preview_generator.py`
- `runtime/shell/client/client_shell.c`
- `apps/launcher/cli/launcher_cli_main.c`
- `apps/server/main_server.c`
- `apps/server/server_boot.py`
- `apps/setup/cli/setup_cli_main.c`
- `content/MANIFEST.md`
- `content/bundles/README.md`
- `archive/generated/agents/agent_context.json`
- `archive/generated/agents/task_intent_map.json`
- `archive/generated/analysis/duplicate_cluster_rankings.json`
- `archive/generated/analysis/implementation_scores.json`
- `archive/generated/architecture/architecture_graph.json`
- `archive/generated/architecture/architecture_graph.v1.json`
- `archive/generated/architecture/module_dependency_graph.json`
- `contracts/governance/deprecations.json`
- `archive/generated/performance/perf_report_win64.json`
- `archive/generated/release/dist_final_expected_artifacts.json`
- `archive/generated/repo/repo_authoritative_boundary_model_and_preferred_target.json`
- `archive/generated/repo/repo_coupling_drift_and_relayout_risk_analysis.json`
- `archive/generated/repo/repo_non_negotiables_and_current_reality.json`
- `archive/generated/repo/repo_phased_migration_shims_validation_and_rollback.json`
- `archive/generated/repo/repo_target_topology_options_and_comparison.json`
- `archive/generated/repo/repo_topology_paths_and_ownership_reality_map.json`
- `archive/generated/xstack/checkpoint_c_xstack_aide_closure.json`
- `archive/generated/xstack/gate_definitions.json`
- `archive/generated/xstack/next_execution_order_post_xstack_aide.json`
- `archive/generated/xstack/xstack_inventory_and_classification.json`
- `archive/generated/xstack/xstack_scope_freeze.json`
- `archive/generated/xstack/xstack_to_aide_extraction_map.json`
- `content/domains/reality/player_desire_map.json`
- `content/packs/core/constraints.worldgen.default_lab/pack.compat.json`
- `content/packs/core/pack.core.camera/pack.compat.json`
- `content/packs/core/pack.core.diegetic_instruments/pack.compat.json`
- `content/packs/core/pack.core.logic_base/pack.compat.json`
- `content/packs/core/pack.core.runtime/pack.compat.json`
- `content/packs/core/pack.server.governance/pack.compat.json`
- `content/packs/core/policy.activation.default_lab/pack.compat.json`
- `content/packs/core/policy.budget.default_lab/pack.compat.json`
- `content/packs/core/policy.fidelity.default_lab/pack.compat.json`
- `content/packs/derived/org.dominium.earth.tiles/pack.compat.json`
- `content/packs/derived/org.dominium.sol.ephemeris/pack.compat.json`
- `content/packs/domain/astronomy.milky_way/pack.compat.json`
- `content/packs/domain/astronomy.sol/pack.compat.json`
- `content/packs/domain/pack.domain.navigation/pack.compat.json`
- `content/packs/domain/planet.earth/pack.compat.json`
- `content/packs/experience/pack.experience.lab_galaxy/pack.compat.json`
- `content/packs/experience/profile.lab.developer/pack.compat.json`
- `content/packs/experience/profile.observer.exploration/pack.compat.json`
- `content/packs/experience/profile.player.default/pack.compat.json`
- `content/packs/experience/profile.spectator.default/pack.compat.json`
- `content/packs/law/law.admin.lab/pack.compat.json`
- `content/packs/law/law.lab.unrestricted/pack.compat.json`
- `content/packs/law/law.observer.truth/pack.compat.json`
- `content/packs/law/law.player.diegetic_default/pack.compat.json`
- `content/packs/law/law.spectator.limited/pack.compat.json`
- `content/packs/law/pack.law.observe_only/pack.compat.json`
- `content/packs/official/pack.sol.pin_minimal/pack.compat.json`
- `content/packs/org.dominium.earth.srtm/pack.compat.json`
- `content/packs/org.dominium.sol.spice/pack.compat.json`
- `content/packs/physics/physics.default.realistic/pack.compat.json`
- `content/packs/representation/pack.representation.base/pack.compat.json`
- `content/packs/specs/specs.default.realistic.m1/pack.compat.json`
- `content/packs/system_templates/base/pack.compat.json`
- `content/packs/tool/pack.tool.admin_security/pack.compat.json`
- `content/packs/tool/pack.tool.control_debug/pack.compat.json`
- `content/packs/tool/pack.tool.inspector/pack.compat.json`
- `content/packs/tool/pack.tool.log_viewer/pack.compat.json`
- `content/packs/tool/pack.tool.navigation/pack.compat.json`
- `content/packs/tool/pack.tool.time_control/pack.compat.json`
- `content/packs/tool/workspace.observer.truth/pack.compat.json`
- `content/packs/tool/workspace.player.diegetic_default/pack.compat.json`
- `content/packs/tool/workspace.spectator.limited/pack.compat.json`
- `content/profiles/bundles/bundle.mvp_default.json`
- `contracts/abi/reality/SPEC_CAPABILITY_SURFACES.md`
- `contracts/audit/convergence_steps/product_boot_matrix.json`
- `contracts/audit/ultra_repo_audit_build_run_test_matrix.json`
- `contracts/baselines/universe/baseline_instance.manifest.json`
- `contracts/lock/README.md`
- `contracts/package/locks/pack_lock.mvp_default.json`
- `contracts/package/modding/mod_policy_engine.py`
- `contracts/planning/later_wave_prerequisite_matrix.json`
- `contracts/planning/live_operations_prerequisite_matrix.json`
- `contracts/planning/readiness/series_readiness_matrix.json`
- `contracts/planning/snapshot_intake_policy.json`
- `contracts/reality/capability_surface_taxonomy.json`
- `contracts/registry/architecture/module_registry.json`
- `contracts/registry/architecture/module_registry.v1.json`
- `contracts/registry/architecture/single_engine_registry.json`
- `contracts/registry/blueprint_registry.json`
- `contracts/registry/deprecation_registry.json`
- `contracts/registry/derived_artifacts.json`
- `contracts/registry/extension_interpretation_registry.json`
- `contracts/registry/field_type_registry.json`
- `contracts/registry/planning/extend_not_replace_registry.json`
- `contracts/registry/planning/gate_registry.json`
- `contracts/registry/planning/later_wave_boundary_reconciliation_registry.json`
- `contracts/registry/planning/later_wave_execution_gates_registry.json`
- `contracts/registry/planning/readiness/prompt_status_registry.json`
- `contracts/registry/planning/trust_aware_refusal_and_containment_reconciliation_registry.json`
- `contracts/registry/planning/zeta_blocker_reconciliation_registry.json`
- `contracts/registry/planning/zeta_execution_gates_registry.json`
- `contracts/registry/process_registry.json`
- `contracts/registry/reality/cross_domain_bridge_registry.json`
- `contracts/registry/reality/formalization_chain_registry.json`
- `contracts/registry/reality/representation_ladder_registry.json`
- `contracts/registry/release/archive_and_mirror_registry.json`
- `contracts/registry/release/artifact_naming_changelog_target_registry.json`
- `contracts/registry/release/build_graph_lock_registry.json`
- `contracts/registry/release/canary_and_deterministic_downgrade_registry.json`
- `contracts/registry/release/live_cutover_receipt_pipeline_anchorization_registry.json`
- `contracts/registry/release/live_cutover_receipts_and_provenance_registry.json`
- `contracts/registry/release/live_trust_rotation_and_revocation_prerequisites_registry.json`
- `contracts/registry/release/manual_automation_parity_and_rehearsal_registry.json`
- `contracts/registry/release/operator_transaction_and_downgrade_registry.json`
- `contracts/registry/release/operator_transaction_receipts_and_provenance_registry.json`
- `contracts/registry/release/preset_and_toolchain_registry.json`
- `contracts/registry/release/publication_and_trust_execution_operationalization_registry.json`
- `contracts/registry/release/publication_trust_licensing_gates_registry.json`
- `contracts/registry/release/release_contract_profile_registry.json`
- `contracts/registry/release/release_index_resolution_registry.json`
- `contracts/registry/release/release_ops_execution_envelope_registry.json`
- `contracts/registry/release/release_rehearsal_sandbox_and_rollback_registry.json`
- `contracts/registry/release/trust_execution_and_revocation_continuity_registry.json`
- `contracts/registry/release/versioning_constitution_registry.json`
- `contracts/registry/runtime/bounded_runtime_cutover_proof_rehearsal_registry.json`
- `contracts/registry/runtime/component_model_registry.json`
- `contracts/registry/runtime/distributed_authority_foundations_registry.json`
- `contracts/registry/runtime/distributed_replay_and_proof_anchor_verification_registry.json`
- `contracts/registry/runtime/domain_service_binding_registry.json`
- `contracts/registry/runtime/event_log_and_replay_registry.json`
- `contracts/registry/runtime/hotswap_boundaries_registry.json`
- `contracts/registry/runtime/lifecycle_manager_registry.json`
- `contracts/registry/runtime/multi_version_coexistence_registry.json`
- `contracts/registry/runtime/rollback_bearing_staged_transition_validation_registry.json`
- `contracts/registry/runtime/runtime_kernel_model_registry.json`
- `contracts/registry/runtime/runtime_service_model_registry.json`
- `contracts/registry/runtime/sandboxing_and_isolation_registry.json`
- `contracts/registry/runtime/state_externalization_registry.json`
- `contracts/registry/testx_groups.json`
- `contracts/registry/toolchain_matrix_registry.json`
- `contracts/registry/worldgen_lock_registry.json`
- `contracts/repo/canon_state.json`
- `contracts/repo/layout_exceptions.toml`
- `contracts/repo/repox/rulesets/core.json`
- `contracts/repo/repox/rulesets/data_first.json`
- `contracts/repo/repox/rulesets/derived_artifacts.json`
- `contracts/repo/repox/rulesets/packaging.json`
- `contracts/repo/repox/rulesets/security.json`
- `contracts/repo/repox/rulesets/ui_parity.json`
- `contracts/restructure/xi4b_review_manifest.json`
- `contracts/restructure/xi4z_decision_manifest.json`
- `contracts/restructure/xi5_readiness_contract.json`
- `contracts/restructure/xi5_readiness_contract_v2.json`
- `contracts/restructure/xi5_readiness_contract_v3.json`
- `contracts/restructure/xi5_readiness_contract_v4.json`
- `contracts/restructure/xi5x2_source_pocket_policy.json`
- `contracts/schema/planning/reality/schema_registry_inventory.json`
- `contracts/schema/deprecation_entry.schema.json`
- `contracts/schema/domain_registry.schema.json`
- `contracts/schema/law/SPEC_LAW_TARGETS.md`
- `contracts/schema/reality/capability_surface.schema.json`
- `contracts/schema/reality/domain_contract.schema.json`
- `contracts/schema/validation_result.schema.json`
- `contracts/templates/domain_contract_template.md`
- `contracts/xstack/aide_adapter_contract.json`
- `contracts/xstack/aide_capability_profile_shape.json`
- `contracts/xstack/aide_evidence_and_review_contract.json`
- `contracts/xstack/aide_policy_and_permission_shape.json`
- `contracts/xstack/aide_portable_task_contract.json`
- `contracts/xstack/codex_repo_operating_contract.json`
- `docs/ARCHITECTURE.md`
- `docs/SCHEMA_EVOLUTION.md`
- `docs/SURVIVAL_SLICE.md`
- `docs/XSTACK.md`
- `docs/agents/AGENT_SAFETY_POLICY.md`
- `docs/runtime/shell/CLI_REFERENCE.md`
- `docs/runtime/shell/COMMANDS_AND_REFUSALS.md`
- `docs/runtime/shell/IPC_DISCOVERY.md`
- `docs/runtime/shell/TUI_FRAMEWORK.md`
- `docs/architecture/ADAPTER_PATTERN.md`
- `docs/architecture/BOUNDARY_ENFORCEMENT.md`
- `docs/architecture/COLLAPSE_EXPAND_SOLVERS.md`
- `docs/architecture/CONTROL_LAYERS.md`
- `docs/architecture/DEPRECATION_AND_QUARANTINE.md`
- `docs/architecture/DEPRECATION_LIFECYCLE.md`
- `docs/architecture/INSTALL_MODEL.md`
- `docs/architecture/INVARIANT_REGISTRY.md`
- `docs/architecture/MODULE_BOUNDARIES_v1.md`
- `docs/architecture/SCHEMA_CHANGE_NOTES.md`
- `docs/architecture/SYSTEM_TOPOLOGY_MAP.md`
- `docs/architecture/TERMINOLOGY_GLOSSARY.md`
- `docs/architecture/astronomy_catalogs.md`
- `docs/architecture/camera_and_navigation.md`
- `docs/architecture/pack_system.md`
- ... 971 more

## Audit Evidence Preservation

Mechanical path substitutions under `docs/audit/**` were reversed because those
files are audit evidence rather than active current path authority.

## Quarantine References

Quarantine-target references were preserved for explicit review and are not wired into active runtime/build paths by this repair pass.
