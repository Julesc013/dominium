# Disaster Suite Run

- Result: `PASS`
- Cases Match Expected: `True`
- Case Count: `18`
- Matched Case Count: `18`
- Mismatched Case Count: `0`
- Silent Success Cases: `none`
- Missing Remediation Cases: `none`

## Cases

### artifact_corruption.corrupted_lock_file
- Result: `refused`
- Refusal Code: `refusal.format.schema_invalid`
- Remediation: `Restore the artifact file so it contains a valid JSON object.`
- Log Keys: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_pack_lock, entrypoint.compat.load.pack_lock, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_pack_lock`

### artifact_corruption.corrupted_pack_blob
- Result: `refused`
- Refusal Code: `refusal.pack.schema_invalid`
- Remediation: `Restore the corrupted pack payload from a verified baseline pack source before retrying verification.`
- Log Keys: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_pack_manifest, entrypoint.pack.verify, outcome.refused, refusal.refusal.pack.schema_invalid, remediation.restore_pack_blob`

### artifact_corruption.corrupted_profile_bundle
- Result: `refused`
- Refusal Code: `refusal.format.schema_invalid`
- Remediation: `Restore the artifact file so it contains a valid JSON object.`
- Log Keys: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_profile_bundle, entrypoint.compat.load.profile_bundle, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_profile_bundle`

### artifact_corruption.corrupted_release_manifest
- Result: `refused`
- Refusal Code: `refusal.release_manifest.manifest_hash_mismatch`
- Remediation: `Rebuild and re-sign the release manifest from the deterministic dist tree before retrying release verification.`
- Log Keys: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_release_manifest_hash, entrypoint.release.verify_manifest, outcome.refused, refusal.refusal.release_manifest.manifest_hash_mismatch, remediation.regenerate_release_manifest`

### artifact_corruption.corrupted_save_snapshot
- Result: `refused`
- Refusal Code: `refusal.format.schema_invalid`
- Remediation: `Restore the artifact file so it contains a valid JSON object.`
- Log Keys: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_save_snapshot, entrypoint.compat.load.save_file, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_save_snapshot`

### compatibility_mismatches.contract_bundle_mismatch
- Result: `refused`
- Refusal Code: `refusal.contract.mismatch`
- Remediation: `Run the explicit CompatX migration tool for this universe lineage or use a universe created under matching semantic contracts.`
- Log Keys: `category.compatibility_mismatches, logcat.compatibility.contract, precondition.mismatch_session_contract_hash, entrypoint.universe.enforce_contract_bundle, outcome.refused, refusal.refusal.contract.mismatch, remediation.run_explicit_contract_migration`

### compatibility_mismatches.protocol_mismatch_no_common_range
- Result: `refused`
- Refusal Code: `refusal.update.protocol_incompatible`
- Remediation: `Select a release index whose supported protocol ranges overlap the current install manifest.`
- Log Keys: `category.compatibility_mismatches, logcat.compatibility.protocol, precondition.replace_protocol_range, entrypoint.update.resolve_protocol_mismatch, outcome.refused, refusal.refusal.update.protocol_incompatible, remediation.select_compatible_release`

### compatibility_mismatches.schema_format_version_too_new
- Result: `refused`
- Refusal Code: `refusal.migration.not_allowed`
- Remediation: `Use a newer build, open the artifact read-only if policy allows it, or install a deterministic migration path.`
- Log Keys: `category.compatibility_mismatches, logcat.compatibility.format, precondition.bump_format_version, entrypoint.compat.load.future_version, outcome.refused, refusal.refusal.migration.not_allowed, remediation.use_newer_engine_or_migration`

### missing_components.missing_binary_referenced_by_install
- Result: `refused`
- Refusal Code: `refusal.install.missing_binary`
- Remediation: `Restore the missing product binary from the baseline dist tree or rebuild the install bundle.`
- Log Keys: `category.missing_components, logcat.component.presence, precondition.remove_product_binary, entrypoint.install.validate_manifest, outcome.refused, refusal.refusal.install.missing_binary, remediation.restore_binary_from_release`

### missing_components.missing_required_pack
- Result: `refused`
- Refusal Code: `refuse.bundle_profile.required_pack_missing`
- Remediation: `Install the required pack into the deterministic pack repo or update the bundle profile explicitly.`
- Log Keys: `category.missing_components, logcat.component.presence, precondition.declare_missing_required_pack, entrypoint.pack.verify.bundle_selection, outcome.refused, refusal.refuse.bundle_profile.required_pack_missing, remediation.restore_required_pack`

### missing_components.missing_store_artifact_referenced_by_instance_save
- Result: `refused`
- Refusal Code: `refusal.format.schema_invalid`
- Remediation: `Restore the artifact file so it contains a valid JSON object.`
- Log Keys: `category.missing_components, logcat.component.presence, precondition.remove_store_save_artifact, entrypoint.compat.load.store_artifact, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_store_artifact`

### policy_conflicts.overlay_conflict_in_strict_policy
- Result: `refused`
- Refusal Code: `refusal.pack.conflict_in_strict`
- Remediation: `Adjust the conflicting overlay layers or choose an explicit non-conflicting precedence model before packing.`
- Log Keys: `category.policy_conflicts, logcat.policy.conflict, precondition.write_conflicting_overlay_layers, entrypoint.overlay.strict_conflict, outcome.refused, refusal.refusal.pack.conflict_in_strict, remediation.resolve_overlay_conflict`

### policy_conflicts.provides_ambiguity_in_strict_policy
- Result: `refused`
- Refusal Code: `refusal.provides.ambiguous`
- Remediation: `Declare an explicit provides resolution or reduce the provider set to a single deterministic choice.`
- Log Keys: `category.policy_conflicts, logcat.policy.conflict, precondition.declare_ambiguous_providers, entrypoint.provides.strict_ambiguity, outcome.refused, refusal.refusal.provides.ambiguous, remediation.declare_explicit_provider`

### trust_failures.invalid_signature
- Result: `refused`
- Refusal Code: `refusal.trust.signature_invalid`
- Remediation: `Regenerate or replace the invalid signature records, or switch to a policy that accepts unsigned artifacts only if signatures are intentionally omitted.`
- Log Keys: `category.trust_failures, logcat.trust.enforcement, precondition.tamper_signature_bytes, entrypoint.trust.verify.invalid_signature, outcome.refused, refusal.refusal.trust.signature_invalid, remediation.replace_invalid_signature`

### trust_failures.unknown_trust_root
- Result: `refused`
- Refusal Code: `refusal.trust.root_not_trusted`
- Remediation: `Import the signer public key into the local trust root registry or choose a trust policy that only warns on untrusted roots.`
- Log Keys: `category.trust_failures, logcat.trust.enforcement, precondition.clear_trust_roots, entrypoint.trust.verify.unknown_root, outcome.refused, refusal.refusal.trust.root_not_trusted, remediation.import_trust_root`

### trust_failures.unsigned_in_strict_mode
- Result: `refused`
- Refusal Code: `refusal.trust.signature_missing`
- Remediation: `Provide detached or inline signatures for the artifact, or select a trust policy that explicitly allows unsigned artifacts.`
- Log Keys: `category.trust_failures, logcat.trust.enforcement, precondition.omit_signatures, entrypoint.trust.verify.unsigned_strict, outcome.refused, refusal.refusal.trust.signature_missing, remediation.sign_artifact_or_relax_policy`

### update_edge_cases.rollback_to_prior_state
- Result: `complete`
- Refusal Code: `none`
- Remediation: `Use the recorded deterministic install transaction log to restore the prior release state.`
- Log Keys: `category.update_edge_cases, logcat.update.policy, precondition.seed_install_transaction_log, entrypoint.update.select_rollback_transaction, outcome.complete, remediation.rollback_transaction_available`

### update_edge_cases.yanked_component_selected_under_latest_compatible
- Result: `complete`
- Refusal Code: `none`
- Remediation: `Pin a non-yanked component descriptor or publish a replacement release before updating.`
- Log Keys: `category.update_edge_cases, logcat.update.policy, precondition.mark_target_component_yanked, entrypoint.update.resolve_yanked_latest_compatible, outcome.complete, remediation.pin_non_yanked_release`
