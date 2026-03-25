# Disaster Suite Model v0.0.0

- disaster_suite_version = `0`
- stability_class = `stable`
- baseline_seed = `DOMINIUM_MVP_BASELINE_SEED_0`
- worldgen_lock_id = `worldgen_lock.v0_0_0`

A) Artifact Corruption

## Corrupted Lock File

- Case ID: `artifact_corruption.corrupted_lock_file`
- Entrypoint: `compat.load.pack_lock`
- Command: `load_versioned_artifact(pack_lock)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.format.schema_invalid`
- Expected Remediation Key: `restore_pack_lock`
- Expected Remediation Hint: `Restore the artifact file so it contains a valid JSON object.`
- Expected Logs: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_pack_lock, entrypoint.compat.load.pack_lock, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_pack_lock`

## Corrupted Pack Blob

- Case ID: `artifact_corruption.corrupted_pack_blob`
- Entrypoint: `pack.verify`
- Command: `verify_pack_set(repo_root=<fixture_pack_repo>)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.pack.schema_invalid`
- Expected Remediation Key: `restore_pack_blob`
- Expected Remediation Hint: `Restore the corrupted pack payload from a verified baseline pack source before retrying verification.`
- Expected Logs: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_pack_manifest, entrypoint.pack.verify, outcome.refused, refusal.refusal.pack.schema_invalid, remediation.restore_pack_blob`

## Corrupted Profile Bundle

- Case ID: `artifact_corruption.corrupted_profile_bundle`
- Entrypoint: `compat.load.profile_bundle`
- Command: `load_versioned_artifact(profile_bundle)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.format.schema_invalid`
- Expected Remediation Key: `restore_profile_bundle`
- Expected Remediation Hint: `Restore the artifact file so it contains a valid JSON object.`
- Expected Logs: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_profile_bundle, entrypoint.compat.load.profile_bundle, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_profile_bundle`

## Corrupted Release Manifest

- Case ID: `artifact_corruption.corrupted_release_manifest`
- Entrypoint: `release.verify_manifest`
- Command: `verify_release_manifest(dist_root=<fixture_dist>)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.release_manifest.manifest_hash_mismatch`
- Expected Remediation Key: `regenerate_release_manifest`
- Expected Remediation Hint: `Rebuild and re-sign the release manifest from the deterministic dist tree before retrying release verification.`
- Expected Logs: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_release_manifest_hash, entrypoint.release.verify_manifest, outcome.refused, refusal.refusal.release_manifest.manifest_hash_mismatch, remediation.regenerate_release_manifest`

## Corrupted Save Snapshot

- Case ID: `artifact_corruption.corrupted_save_snapshot`
- Entrypoint: `compat.load.save_file`
- Command: `load_versioned_artifact(save_file)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.format.schema_invalid`
- Expected Remediation Key: `restore_save_snapshot`
- Expected Remediation Hint: `Restore the artifact file so it contains a valid JSON object.`
- Expected Logs: `category.artifact_corruption, logcat.artifact.integrity, precondition.corrupt_save_snapshot, entrypoint.compat.load.save_file, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_save_snapshot`

B) Missing Components

## Missing Binary Referenced By Install

- Case ID: `missing_components.missing_binary_referenced_by_install`
- Entrypoint: `install.validate_manifest`
- Command: `validate_install_manifest(install_manifest)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.install.missing_binary`
- Expected Remediation Key: `restore_binary_from_release`
- Expected Remediation Hint: `Restore the missing product binary from the baseline dist tree or rebuild the install bundle.`
- Expected Logs: `category.missing_components, logcat.component.presence, precondition.remove_product_binary, entrypoint.install.validate_manifest, outcome.refused, refusal.refusal.install.missing_binary, remediation.restore_binary_from_release`

## Missing Required Pack

- Case ID: `missing_components.missing_required_pack`
- Entrypoint: `pack.verify.bundle_selection`
- Command: `verify_pack_set(bundle_id='bundle.omega4.missing_required')`
- Expected Result: `refused`
- Expected Refusal Code: `refuse.bundle_profile.required_pack_missing`
- Expected Remediation Key: `restore_required_pack`
- Expected Remediation Hint: `Install the required pack into the deterministic pack repo or update the bundle profile explicitly.`
- Expected Logs: `category.missing_components, logcat.component.presence, precondition.declare_missing_required_pack, entrypoint.pack.verify.bundle_selection, outcome.refused, refusal.refuse.bundle_profile.required_pack_missing, remediation.restore_required_pack`

## Missing Store Artifact Referenced By Instance/Save

- Case ID: `missing_components.missing_store_artifact_referenced_by_instance_save`
- Entrypoint: `compat.load.store_artifact`
- Command: `load_versioned_artifact(save_file_missing_from_store)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.format.schema_invalid`
- Expected Remediation Key: `restore_store_artifact`
- Expected Remediation Hint: `Restore the artifact file so it contains a valid JSON object.`
- Expected Logs: `category.missing_components, logcat.component.presence, precondition.remove_store_save_artifact, entrypoint.compat.load.store_artifact, outcome.refused, refusal.refusal.format.schema_invalid, remediation.restore_store_artifact`

C) Compatibility Mismatches

## Contract Bundle Mismatch

- Case ID: `compatibility_mismatches.contract_bundle_mismatch`
- Entrypoint: `universe.enforce_contract_bundle`
- Command: `enforce_session_contract_bundle(replay_mode=false)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.contract.mismatch`
- Expected Remediation Key: `run_explicit_contract_migration`
- Expected Remediation Hint: `Run the explicit CompatX migration tool for this universe lineage or use a universe created under matching semantic contracts.`
- Expected Logs: `category.compatibility_mismatches, logcat.compatibility.contract, precondition.mismatch_session_contract_hash, entrypoint.universe.enforce_contract_bundle, outcome.refused, refusal.refusal.contract.mismatch, remediation.run_explicit_contract_migration`

## Protocol Mismatch With No Common Range

- Case ID: `compatibility_mismatches.protocol_mismatch_no_common_range`
- Entrypoint: `update.resolve_protocol_mismatch`
- Command: `resolve_update_plan(protocol_mismatch)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.update.protocol_incompatible`
- Expected Remediation Key: `select_compatible_release`
- Expected Remediation Hint: `Select a release index whose supported protocol ranges overlap the current install manifest.`
- Expected Logs: `category.compatibility_mismatches, logcat.compatibility.protocol, precondition.replace_protocol_range, entrypoint.update.resolve_protocol_mismatch, outcome.refused, refusal.refusal.update.protocol_incompatible, remediation.select_compatible_release`

## Schema Or Format Version Too New

- Case ID: `compatibility_mismatches.schema_format_version_too_new`
- Entrypoint: `compat.load.future_version`
- Command: `load_versioned_artifact(profile_bundle_future_version)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.migration.not_allowed`
- Expected Remediation Key: `use_newer_engine_or_migration`
- Expected Remediation Hint: `Use a newer build, open the artifact read-only if policy allows it, or install a deterministic migration path.`
- Expected Logs: `category.compatibility_mismatches, logcat.compatibility.format, precondition.bump_format_version, entrypoint.compat.load.future_version, outcome.refused, refusal.refusal.migration.not_allowed, remediation.use_newer_engine_or_migration`

D) Trust Failures

## Invalid Signature

- Case ID: `trust_failures.invalid_signature`
- Entrypoint: `trust.verify.invalid_signature`
- Command: `verify_artifact_trust(strict_ranked, signatures=[invalid])`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.trust.signature_invalid`
- Expected Remediation Key: `replace_invalid_signature`
- Expected Remediation Hint: `Regenerate or replace the invalid signature records, or switch to a policy that accepts unsigned artifacts only if signatures are intentionally omitted.`
- Expected Logs: `category.trust_failures, logcat.trust.enforcement, precondition.tamper_signature_bytes, entrypoint.trust.verify.invalid_signature, outcome.refused, refusal.refusal.trust.signature_invalid, remediation.replace_invalid_signature`

## Unknown Trust Root

- Case ID: `trust_failures.unknown_trust_root`
- Entrypoint: `trust.verify.unknown_root`
- Command: `verify_artifact_trust(strict_ranked, trusted_roots=[])`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.trust.root_not_trusted`
- Expected Remediation Key: `import_trust_root`
- Expected Remediation Hint: `Import the signer public key into the local trust root registry or choose a trust policy that only warns on untrusted roots.`
- Expected Logs: `category.trust_failures, logcat.trust.enforcement, precondition.clear_trust_roots, entrypoint.trust.verify.unknown_root, outcome.refused, refusal.refusal.trust.root_not_trusted, remediation.import_trust_root`

## Unsigned In Strict Mode

- Case ID: `trust_failures.unsigned_in_strict_mode`
- Entrypoint: `trust.verify.unsigned_strict`
- Command: `verify_artifact_trust(strict_ranked, signatures=[])`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.trust.signature_missing`
- Expected Remediation Key: `sign_artifact_or_relax_policy`
- Expected Remediation Hint: `Provide detached or inline signatures for the artifact, or select a trust policy that explicitly allows unsigned artifacts.`
- Expected Logs: `category.trust_failures, logcat.trust.enforcement, precondition.omit_signatures, entrypoint.trust.verify.unsigned_strict, outcome.refused, refusal.refusal.trust.signature_missing, remediation.sign_artifact_or_relax_policy`

E) Update Edge Cases

## Rollback To Prior State

- Case ID: `update_edge_cases.rollback_to_prior_state`
- Entrypoint: `update.select_rollback_transaction`
- Command: `select_rollback_transaction(log, to_release_id='release.prior')`
- Expected Result: `complete`
- Expected Refusal Code: `none`
- Expected Remediation Key: `rollback_transaction_available`
- Expected Remediation Hint: `Use the recorded deterministic install transaction log to restore the prior release state.`
- Expected Logs: `category.update_edge_cases, logcat.update.policy, precondition.seed_install_transaction_log, entrypoint.update.select_rollback_transaction, outcome.complete, remediation.rollback_transaction_available`

## Yanked Component Selected Under Latest_Compatible

- Case ID: `update_edge_cases.yanked_component_selected_under_latest_compatible`
- Entrypoint: `update.resolve_yanked_latest_compatible`
- Command: `resolve_update_plan(latest_compatible_with_yanked_target)`
- Expected Result: `complete`
- Expected Refusal Code: `none`
- Expected Remediation Key: `pin_non_yanked_release`
- Expected Remediation Hint: `Pin a non-yanked component descriptor or publish a replacement release before updating.`
- Expected Logs: `category.update_edge_cases, logcat.update.policy, precondition.mark_target_component_yanked, entrypoint.update.resolve_yanked_latest_compatible, outcome.complete, remediation.pin_non_yanked_release`

F) Policy Conflicts

## Overlay Conflict In Strict Policy

- Case ID: `policy_conflicts.overlay_conflict_in_strict_policy`
- Entrypoint: `overlay.strict_conflict`
- Command: `verify_pack_set(mod_policy.strict, overlay.conflict.refuse)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.pack.conflict_in_strict`
- Expected Remediation Key: `resolve_overlay_conflict`
- Expected Remediation Hint: `Adjust the conflicting overlay layers or choose an explicit non-conflicting precedence model before packing.`
- Expected Logs: `category.policy_conflicts, logcat.policy.conflict, precondition.write_conflicting_overlay_layers, entrypoint.overlay.strict_conflict, outcome.refused, refusal.refusal.pack.conflict_in_strict, remediation.resolve_overlay_conflict`

## Provides Ambiguity In Strict Policy

- Case ID: `policy_conflicts.provides_ambiguity_in_strict_policy`
- Entrypoint: `provides.strict_ambiguity`
- Command: `resolve_providers(strict_refuse_ambiguous)`
- Expected Result: `refused`
- Expected Refusal Code: `refusal.provides.ambiguous`
- Expected Remediation Key: `declare_explicit_provider`
- Expected Remediation Hint: `Declare an explicit provides resolution or reduce the provider set to a single deterministic choice.`
- Expected Logs: `category.policy_conflicts, logcat.policy.conflict, precondition.declare_ambiguous_providers, entrypoint.provides.strict_ambiguity, outcome.refused, refusal.refusal.provides.ambiguous, remediation.declare_explicit_provider`
