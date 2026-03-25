# Disaster Suite Baseline

- disaster_suite_version = `0`
- stability_class = `stable`
- result = `complete`
- required_commit_tag = `DISASTER-REGRESSION-UPDATE`

## Scenarios

- `artifact_corruption.corrupted_lock_file` -> refusal `refusal.format.schema_invalid` remediation `restore_pack_lock`
- `artifact_corruption.corrupted_pack_blob` -> refusal `refusal.pack.schema_invalid` remediation `restore_pack_blob`
- `artifact_corruption.corrupted_profile_bundle` -> refusal `refusal.format.schema_invalid` remediation `restore_profile_bundle`
- `artifact_corruption.corrupted_release_manifest` -> refusal `refusal.release_manifest.manifest_hash_mismatch` remediation `regenerate_release_manifest`
- `artifact_corruption.corrupted_save_snapshot` -> refusal `refusal.format.schema_invalid` remediation `restore_save_snapshot`
- `compatibility_mismatches.contract_bundle_mismatch` -> refusal `refusal.contract.mismatch` remediation `run_explicit_contract_migration`
- `compatibility_mismatches.protocol_mismatch_no_common_range` -> refusal `refusal.update.protocol_incompatible` remediation `select_compatible_release`
- `compatibility_mismatches.schema_format_version_too_new` -> refusal `refusal.migration.not_allowed` remediation `use_newer_engine_or_migration`
- `missing_components.missing_binary_referenced_by_install` -> refusal `refusal.install.missing_binary` remediation `restore_binary_from_release`
- `missing_components.missing_required_pack` -> refusal `refuse.bundle_profile.required_pack_missing` remediation `restore_required_pack`
- `missing_components.missing_store_artifact_referenced_by_instance_save` -> refusal `refusal.format.schema_invalid` remediation `restore_store_artifact`
- `policy_conflicts.overlay_conflict_in_strict_policy` -> refusal `refusal.pack.conflict_in_strict` remediation `resolve_overlay_conflict`
- `policy_conflicts.provides_ambiguity_in_strict_policy` -> refusal `refusal.provides.ambiguous` remediation `declare_explicit_provider`
- `trust_failures.invalid_signature` -> refusal `refusal.trust.signature_invalid` remediation `replace_invalid_signature`
- `trust_failures.unknown_trust_root` -> refusal `refusal.trust.root_not_trusted` remediation `import_trust_root`
- `trust_failures.unsigned_in_strict_mode` -> refusal `refusal.trust.signature_missing` remediation `sign_artifact_or_relax_policy`
- `update_edge_cases.rollback_to_prior_state` -> refusal `none` remediation `rollback_transaction_available`
- `update_edge_cases.yanked_component_selected_under_latest_compatible` -> refusal `none` remediation `pin_non_yanked_release`

## Readiness

- Ω-5 ecosystem verify: `ready`
- Ω-6 update simulation: `ready`
