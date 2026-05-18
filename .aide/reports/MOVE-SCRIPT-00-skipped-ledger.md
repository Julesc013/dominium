Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-SCRIPT-00 Skipped Ledger

Skipped items are deferred, not failed moves. MOVE-SCRIPT-00 is dry-run only.

| Reason | Count |
| --- | ---: |
| `active_python_package_requires_import_rewrite_or_shim_plan` | 142 |
| `identity_sensitive_without_clear_identity_safe_route` | 59 |
| `target_uses_forbidden_segment_source` | 13 |
| `authority_sensitive_docs_only_route_requires_review` | 7 |
| `normative_specs_reality_docs_require_authority_review` | 7 |
| `target_uses_forbidden_segment_compat` | 3 |

## First Skipped Items

| Source | Proposed Target | Reasons |
| --- | --- | --- |
| `compat/__init__.py` | `tools/validators/compatibility/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/capability_negotiation.py` | `tools/validators/compatibility/capability_negotiation.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/data_format_loader.py` | `tools/validators/compatibility/data_format_loader.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/descriptor/__init__.py` | `tools/validators/compatibility/descriptor/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/descriptor/descriptor_engine.py` | `tools/validators/compatibility/descriptor/descriptor_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/handshake/__init__.py` | `tools/validators/compatibility/handshake/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/handshake/handshake_engine.py` | `tools/validators/compatibility/handshake/handshake_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/migration_lifecycle.py` | `tools/validators/compatibility/migration_lifecycle.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/negotiation/__init__.py` | `tools/validators/compatibility/negotiation/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/negotiation/degrade_enforcer.py` | `tools/validators/compatibility/negotiation/degrade_enforcer.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/negotiation/negotiation_engine.py` | `tools/validators/compatibility/negotiation/negotiation_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/shims/__init__.py` | `tools/validators/compatibility/shims/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/shims/common.py` | `tools/validators/compatibility/shims/common.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/shims/flag_shims.py` | `tools/validators/compatibility/shims/flag_shims.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/shims/path_shims.py` | `tools/validators/compatibility/shims/path_shims.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/shims/tool_shims.py` | `tools/validators/compatibility/shims/tool_shims.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `compat/shims/validation_shims.py` | `tools/validators/compatibility/shims/validation_shims.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `control/__init__.py` | `runtime/shell/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/capability/__init__.py` | `runtime/capability/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `control/capability/capability_engine.py` | `runtime/capability/capability_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `control/control_plane_engine.py` | `runtime/shell/control_plane_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/effects/__init__.py` | `runtime/shell/effects/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/effects/effect_engine.py` | `runtime/shell/effects/effect_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/fidelity/__init__.py` | `runtime/shell/fidelity/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `control/fidelity/fidelity_engine.py` | `runtime/shell/fidelity/fidelity_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `control/ir/__init__.py` | `contracts/command/ir/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/ir/control_ir_compiler.py` | `contracts/command/ir/control_ir_compiler.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/ir/control_ir_multiplayer.py` | `contracts/command/ir/control_ir_multiplayer.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/ir/control_ir_programs.py` | `contracts/command/ir/control_ir_programs.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/ir/control_ir_verifier.py` | `contracts/command/ir/control_ir_verifier.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/negotiation/__init__.py` | `runtime/shell/negotiation/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/negotiation/negotiation_kernel.py` | `runtime/shell/negotiation/negotiation_kernel.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/planning/__init__.py` | `runtime/shell/planning/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/planning/plan_engine.py` | `runtime/shell/planning/plan_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/proof/__init__.py` | `engine/proof/proof/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/proof/control_proof_bundle.py` | `engine/proof/proof/control_proof_bundle.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `control/view/__init__.py` | `runtime/shell/view/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `control/view/view_engine.py` | `runtime/shell/view/view_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/__init__.py` | `engine/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/constraints/__init__.py` | `engine/execution/constraints/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/constraints/constraint_engine.py` | `engine/execution/constraints/constraint_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/flow/__init__.py` | `engine/execution/flow/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/flow/flow_engine.py` | `engine/execution/flow/flow_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/graph/__init__.py` | `engine/execution/graph/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/graph/network_graph_engine.py` | `engine/execution/graph/network_graph_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/graph/routing_engine.py` | `engine/execution/graph/routing_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/hazards/__init__.py` | `game/domain/hazards/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/hazards/hazard_engine.py` | `game/domain/hazards/hazard_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/schedule/__init__.py` | `engine/schedule/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/schedule/schedule_engine.py` | `engine/schedule/schedule_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/spatial/__init__.py` | `engine/math/spatial/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/spatial/spatial_engine.py` | `engine/math/spatial/spatial_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/state/__init__.py` | `engine/state/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `core/state/state_machine_engine.py` | `engine/state/state_machine_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `data/architecture/repository_structure_lock.json` | `archive/generated/architecture/repository_structure_lock.json` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/defaults/profiles/modern_2020.tlv` | `content/defaults/profiles/modern_2020.tlv` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/defaults/profiles/retro_1990s.tlv` | `content/defaults/profiles/retro_1990s.tlv` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/defaults/profiles/server_mmo.tlv` | `content/defaults/profiles/server_mmo.tlv` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/governance/governance_profile.json` | `contracts/governance/governance_profile.json` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/repo/repo_phased_migration_shims_validation_and_rollback.json` | `archive/generated/repo/repo_phased_migration_shims_validation_and_rollback.json` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/xstack/checkpoint_c_xstack_aide_closure.json` | `archive/generated/xstack/checkpoint_c_xstack_aide_closure.json` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/xstack/next_execution_order_post_xstack_aide.json` | `archive/generated/xstack/next_execution_order_post_xstack_aide.json` | `identity_sensitive_without_clear_identity_safe_route` |
| `data/xstack/xstack_to_aide_extraction_map.json` | `archive/generated/xstack/xstack_to_aide_extraction_map.json` | `identity_sensitive_without_clear_identity_safe_route` |
| `governance/__init__.py` | `tools/governance/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `governance/governance_profile.py` | `tools/governance/governance_profile.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `lib/__init__.py` | `tools/package/libraries/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/artifact/__init__.py` | `tools/package/libraries/artifact/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/artifact/artifact_validator.py` | `tools/package/libraries/artifact/artifact_validator.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `lib/bundle/__init__.py` | `tools/package/libraries/bundle/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `lib/bundle/bundle_manifest.py` | `tools/package/libraries/bundle/bundle_manifest.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `lib/export/__init__.py` | `tools/package/libraries/export/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/export/export_engine.py` | `tools/package/libraries/export/export_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/import/__init__.py` | `tools/package/libraries/import/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/import/import_engine.py` | `tools/package/libraries/import/import_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/install/__init__.py` | `tools/package/libraries/install/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/install/install_discovery_engine.py` | `tools/package/libraries/install/install_discovery_engine.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/install/install_validator.py` | `tools/package/libraries/install/install_validator.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |
| `lib/instance/__init__.py` | `tools/package/libraries/instance/__init__.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/instance/instance_clone.py` | `tools/package/libraries/instance/instance_clone.py` | `active_python_package_requires_import_rewrite_or_shim_plan` |
| `lib/instance/instance_validator.py` | `tools/package/libraries/instance/instance_validator.py` | `active_python_package_requires_import_rewrite_or_shim_plan, identity_sensitive_without_clear_identity_safe_route` |

Additional skipped items are recorded in the JSON report.
