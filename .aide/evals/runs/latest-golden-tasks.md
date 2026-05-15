# Latest Golden Tasks

- result: PASS
- task_count: 130
- pass_count: 130
- warn_count: 0
- fail_count: 0
- provider_or_model_calls: none
- network_calls: none
- raw_prompt_storage: false
- raw_response_storage: false
- token_quality_statement: Token reduction remains valid only if golden tasks pass.

## Tasks

### adapter-managed-section-determinism

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: AGENTS.md
- notes: Checks managed section replacement on an isolated fixture repo.

### branch_role_detection_golden

- result: PASS
- checks_run: 15
- passed_checks: 15
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/branch-roles.md, .aide/git/workflow-detection.json, .aide/policies/branch-roles.yaml
- notes: Checks deterministic branch-role classification and conservative unknown handling.

### changelog_json_shape_golden

- result: PASS
- checks_run: 20
- passed_checks: 20
- approx_tokens_if_applicable: n/a
- related_paths: .aide/changelog/changelog.preview.json, .aide/changelog/release-notes.preview.json
- notes: Checks changelog and release-note preview JSON shape.

### changelog_preview_golden

- result: PASS
- checks_run: 9
- passed_checks: 9
- approx_tokens_if_applicable: n/a
- related_paths: .aide/changelog/CHANGELOG.preview.md, .aide/changelog/RELEASE_NOTES.preview.md, .aide/changelog/config.yaml, .aide/changelog/templates/changelog.md.template, .aide/changelog/templates/release-notes.md.template, .aide/policies/changelog.yaml, .aide/policies/commit-messages.yaml
- notes: Checks deterministic changelog preview grouping and malformed commit reporting.

### commit_message_standard_golden

- result: PASS
- checks_run: 14
- passed_checks: 14
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/commit-template.md, .aide/hooks/commit-msg, .aide/policies/commit-messages.yaml, .aide/reports/aide-commit-message-standard.md
- notes: Checks changelog-ready commit message validation anchors.

### compact-task-packet-required-sections

- result: PASS
- checks_run: 17
- passed_checks: 17
- approx_tokens_if_applicable: 936
- related_paths: .aide/context/latest-task-packet.md, .aide/policies/token-budget.yaml, .aide/prompts/compact-task.md
- notes: Checks the compact task packet shape and forbidden prompt discipline.

### context-packet-no-full-repo-dump

- result: PASS
- checks_run: 17
- passed_checks: 17
- approx_tokens_if_applicable: 463
- related_paths: .aide/context/context-index.json, .aide/context/latest-context-packet.md, .aide/context/repo-map.json, .aide/context/test-map.json
- notes: Checks context refs instead of whole-repo dumps.

### docs_consistency_report_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/docs-consistency.yaml, .aide/reports/docs-consistency-report.md
- notes: Checks docs consistency warning surfaces.

### drop_candidate_not_delete_approval_golden

- result: PASS
- checks_run: 7
- passed_checks: 7
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/salvage-map.yaml, .aide/refactors/current-move-map.json, .aide/refactors/current-salvage-map.json
- notes: Checks Q42 fates never become deletion approval.

### export_pack_commit_policy_inclusion_golden

- result: PASS
- checks_run: 8
- passed_checks: 8
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/git/commit-template.md, .aide/hooks/commit-msg, .aide/policies/commit-messages.yaml
- notes: Checks portable commit discipline and changelog support are exported or locally available after import.

### export_pack_excludes_source_branch_state_golden

- result: PASS
- checks_run: 294
- passed_checks: 294
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/policies/export-import.yaml
- notes: Checks source-specific Git detection, helper plans, branch policy, and generated previews are not exported as target truth.

### export_pack_git_policy_inclusion_golden

- result: PASS
- checks_run: 15
- passed_checks: 15
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/git/helper-policy.yaml, .aide/policies/branch-roles.yaml, .aide/policies/git-workflow.yaml
- notes: Checks portable Git workflow and helper governance are exported or locally available after import.

### export_pack_task_recovery_inclusion_golden

- result: PASS
- checks_run: 8
- passed_checks: 8
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/policies/recovery.yaml, .aide/policies/task-resumption.yaml, .aide/policies/work-units.yaml
- notes: Checks portable task resumption, WorkUnit, and recovery governance are exported or locally available after import.

### file_classification_policy_golden

- result: PASS
- checks_run: 10
- passed_checks: 10
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/file-classification.yaml, .aide/scripts/aide_lite.py, README.md
- notes: Checks deterministic classification anchors and known AIDE file classes.

### file_quality_ledger_schema_golden

- result: PASS
- checks_run: 33
- passed_checks: 33
- approx_tokens_if_applicable: n/a
- related_paths: .aide/quality/file-quality-ledger.schema.json, .aide/quality/file-quality-record.schema.json, .aide/reports/file-quality-ledger.schema.json
- notes: Checks file quality ledger schema and latest/generated ledger shape.

### file_quality_policy_golden

- result: PASS
- checks_run: 48
- passed_checks: 48
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/docs-consistency.yaml, .aide/policies/file-quality.yaml, .aide/policies/module-quality.yaml, .aide/policies/reuse-modularity.yaml
- notes: Checks Q38 file-quality policy anchors and no-call advisory posture.

### fixture_import_governance_commands_golden

- result: PASS
- checks_run: 9
- passed_checks: 9
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/hooks/commit-msg, .aide/scripts/aide_lite.py
- notes: Checks safe fixture import receives governance files and can run portable commit/task/Git commands.

### git_helper_policy_golden

- result: PASS
- checks_run: 26
- passed_checks: 26
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/helper-commands.md, .aide/git/helper-policy.yaml, .aide/git/latest-helper-plan.json, .aide/git/latest-helper-plan.md
- notes: Checks Q29 helper policy anchors and generated helper-plan artifacts.

### git_land_plan_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/helper-commands.md, .aide/git/latest-helper-plan.json
- notes: Checks land dry-run planning and no remote mutation anchors.

### git_live_repo_no_mutation_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/helper-commands.md, .aide/git/helper-policy.yaml, .aide/git/latest-helper-plan.json
- notes: Checks live-repo helper plans remain no-mutation by default.

### git_promote_plan_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/helper-commands.md, .aide/git/helper-policy.yaml, .aide/policies/promotion-rules.yaml
- notes: Checks promotion helper review gates and dry-run command documentation.

### git_prune_guard_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/helper-commands.md, .aide/git/helper-policy.yaml, .aide/policies/prune-policy.yaml
- notes: Checks prune containment and protected-role guards.

### git_workflow_policy_golden

- result: PASS
- checks_run: 16
- passed_checks: 16
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/project-profiles.yaml, .aide/policies/branch-roles.yaml, .aide/policies/git-workflow.yaml, .aide/policies/promotion-rules.yaml, .aide/policies/prune-policy.yaml, .aide/policies/sync-policy.yaml
- notes: Checks Q28 Git workflow policy anchors and project profiles.

### github_ci_advisory_golden

- result: PASS
- checks_run: 12
- passed_checks: 12
- approx_tokens_if_applicable: n/a
- related_paths: .aide/github/ci-advisory.json, .aide/github/ci-advisory.md, .aide/policies/ci-gates.yaml
- notes: Checks Q35 CI gate advisory without workflow installation.

### github_export_inclusion_golden

- result: PASS
- checks_run: 21
- passed_checks: 21
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/policies/branch-protection.yaml, .aide/policies/ci-gates.yaml, .aide/policies/export-import.yaml, .aide/policies/github-protection.yaml
- notes: Checks Q35 portable policy export and generated advisory exclusion.

### github_protection_policy_golden

- result: PASS
- checks_run: 15
- passed_checks: 15
- approx_tokens_if_applicable: n/a
- related_paths: .aide/github/branch-protection-plan.json, .aide/policies/branch-protection.yaml, .aide/policies/github-protection.yaml
- notes: Checks Q35 GitHub branch-protection advisory remains report-only.

### github_release_asset_schema_golden

- result: PASS
- checks_run: 13
- passed_checks: 13
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/github-release-asset.schema.json
- notes: Checks GitHub release asset schema shape.

### github_release_assets_have_checksums_golden

- result: PASS
- checks_run: 26
- passed_checks: 26
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/dist/SHA256SUMS.txt, .aide/release/dist/aide-lite-pack-v0.checksums.json, .aide/release/github-release-assets.json
- notes: Checks release draft asset list includes checksums and validates hashes.

### github_release_checklist_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/release-checklist.yaml, .aide/release/github-release-checklist.json, .aide/release/github-release-checklist.schema.json
- notes: Checks GitHub release checklist policy and manual review coverage.

### github_release_draft_policy_golden

- result: PASS
- checks_run: 10
- passed_checks: 10
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/github-release-draft.yaml, .aide/policies/release-publication-boundary.yaml
- notes: Checks Q48 release draft policy anchors and publication boundary.

### github_release_draft_schema_golden

- result: PASS
- checks_run: 11
- passed_checks: 11
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/github-release-draft.schema.json
- notes: Checks GitHub release draft schema shape.

### github_release_no_publish_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/github-release-draft.json, .aide/release/github-release-publication-boundary.md, .aide/release/github-release-upload-plan.json
- notes: Checks Q48 generated outputs stay local-only and unpublished.

### github_release_upload_plan_golden

- result: PASS
- checks_run: 1
- passed_checks: 1
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/github-release-upload-plan.json, .aide/release/github-release-upload-plan.schema.json
- notes: Checks GitHub release upload plan schema and no-upload posture.

### github_report_only_golden

- result: PASS
- checks_run: 11
- passed_checks: 11
- approx_tokens_if_applicable: n/a
- related_paths: .aide/github/github-advisory.json, .aide/github/github-advisory.md, .aide/github/latest-github-status.md
- notes: Checks Q35 report-only behavior and no live GitHub/CI mutation.

### install_conflict_report_schema_golden

- result: PASS
- checks_run: 15
- passed_checks: 15
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/conflict-record.schema.json, .aide/install/conflict-report.schema.json, .aide/install/latest-conflict-report.json
- notes: Checks install conflict report schema and no-apply conflict output.

### install_no_apply_golden

- result: PASS
- checks_run: 3954
- passed_checks: 3954
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/latest-install-dry-run.json, .aide/install/latest-install-plan.json
- notes: Checks Q43 install data never enables apply, overwrite, or automatic migration.

### install_no_source_state_leak_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/latest-install-plan.json, .aide/policies/install-preservation.yaml
- notes: Checks source-generated, local, and secret-like state is never planned as target install truth.

### install_ownership_ledger_schema_golden

- result: PASS
- checks_run: 14
- passed_checks: 14
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/latest-ownership-ledger.example.json, .aide/install/ownership-ledger.schema.json, .aide/install/ownership-record.schema.json
- notes: Checks ownership ledger schema and example no-apply ledger shape.

### install_plan_schema_golden

- result: PASS
- checks_run: 8330
- passed_checks: 8330
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/install-operation.schema.json, .aide/install/install-plan.schema.json, .aide/install/latest-install-plan.json
- notes: Checks install plan schema and generated no-apply plan shape.

### install_policy_golden

- result: PASS
- checks_run: 66
- passed_checks: 66
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/install-plan.schema.json, .aide/policies/install.yaml
- notes: Checks Q43 install policy anchors and no-apply install posture.

### install_preservation_policy_golden

- result: PASS
- checks_run: 67
- passed_checks: 67
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/preservation-report.schema.json, .aide/policies/install-preservation.yaml
- notes: Checks preservation rules for target memory, queue, evidence, local state, and manual content.

### install_preserves_target_state_golden

- result: PASS
- checks_run: 7
- passed_checks: 7
- approx_tokens_if_applicable: n/a
- related_paths: .aide/install/latest-install-plan.json, .aide/install/latest-preservation-report.md, .aide/policies/install-preservation.yaml
- notes: Checks Q43 preserves target-specific state instead of treating it as install truth.

### intent_compile_destructive_prompt_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/prompt-normalization.yaml, .aide/policies/risk-classes.yaml
- notes: Checks destructive raw prompts cannot execute directly.

### intent_compile_git_prompt_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/git-workflow.yaml, .aide/policies/intent.yaml, .aide/policies/promotion-rules.yaml
- notes: Checks Git promotion prompts require branch policy and review evidence.

### intent_compile_install_prompt_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/export-import.yaml, .aide/policies/intent.yaml, .aide/policies/prompt-normalization.yaml
- notes: Checks target install prompts become preflight/preservation WorkUnits.

### intent_compile_overbroad_prompt_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/prompt-normalization.yaml, .aide/policies/workunit-sizing.yaml
- notes: Checks overbroad prompts become split recommendations.

### intent_compile_vague_prompt_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/intake/intent-examples.yaml, .aide/policies/intent.yaml
- notes: Checks that vague prompts do not trigger product work.

### intent_packet_schema_golden

- result: PASS
- checks_run: 85
- passed_checks: 85
- approx_tokens_if_applicable: n/a
- related_paths: .aide/intake/intent-packet.schema.json, .aide/intake/workunit-draft.schema.json
- notes: Checks intent packet and WorkUnit draft shape plus raw prompt storage boundaries.

### malformed_commit_reporting_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/changelog/malformed-commits.md
- notes: Checks malformed and legacy commit reporting without history rewrite.

### migration_ledger_policy_golden

- result: PASS
- checks_run: 106
- passed_checks: 106
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/migration-ledger.yaml, .aide/refactors/migration-ledger-entry.schema.json, .aide/refactors/migration-ledger.schema.json
- notes: Checks Q42 migration ledger policy and draft event shape.

### migration_ledger_schema_golden

- result: PASS
- checks_run: 13
- passed_checks: 13
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/migration-ledger.schema.json
- notes: Checks migration-ledger schema and example dry-run event support.

### migration_policy_golden

- result: PASS
- checks_run: 8
- passed_checks: 8
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/migration.yaml
- notes: Checks Q39 migration stages and no mandatory migration boundary.

### move_map_policy_golden

- result: PASS
- checks_run: 79
- passed_checks: 79
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/move-map.yaml, .aide/refactors/move-map-entry.schema.json, .aide/refactors/move-map.schema.json
- notes: Checks Q42 move-map policy anchors and candidate-only map shape.

### move_map_schema_golden

- result: PASS
- checks_run: 11
- passed_checks: 11
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/move-map.schema.json
- notes: Checks move-map schema exists and remains no-apply.

### path_alias_policy_golden

- result: PASS
- checks_run: 79
- passed_checks: 79
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/path-aliases.yaml, .aide/refactors/path-alias-entry.schema.json, .aide/refactors/path-aliases.schema.json, .aide/refactors/path-aliases.template.yaml
- notes: Checks Q42 path-alias policy anchors and no-apply alias shape.

### path_alias_schema_golden

- result: PASS
- checks_run: 12
- passed_checks: 12
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/path-aliases.schema.json
- notes: Checks path-alias schema exists and remains no-apply.

### promotion_rules_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/promotion-rules.md, .aide/policies/promotion-rules.yaml
- notes: Checks task-to-dev and dev-to-main gate anchors.

### prune_policy_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/prune-policy.md, .aide/policies/prune-policy.yaml
- notes: Checks prune guards require containment and remain dry-run/report-only.

### quality_ledger_generation_golden

- result: PASS
- checks_run: 28
- passed_checks: 28
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repo/file-inventory.json, .aide/reports/file-quality-ledger.json
- notes: Checks deterministic quality ledger generation from Q37 outputs.

### quality_no_delete_recommendation_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/file-quality.yaml, .aide/reports/file-quality-ledger.json
- notes: Checks Q38 warning outputs never become deletion advice.

### refactor_map_no_apply_golden

- result: PASS
- checks_run: 63
- passed_checks: 63
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/current-move-map.json, .aide/refactors/current-salvage-map.json, .aide/refactors/map-validation-report.json, .aide/refactors/path-aliases.yaml, .aide/refactors/reference-rewrite-plan.json
- notes: Checks Q42 map outputs and generated bundle remain no-apply/no-mutation.

### refactor_no_apply_golden

- result: PASS
- checks_run: 52
- passed_checks: 52
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/refactor-application.yaml, .aide/refactors/latest-refactor-plan.example.json, .aide/refactors/latest-refactor-readiness.json
- notes: Checks Q39 has no apply, move, delete, rewrite, or deletion-approval behavior.

### refactor_plan_schema_golden

- result: PASS
- checks_run: 54
- passed_checks: 54
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/latest-refactor-plan.example.json, .aide/refactors/refactor-operation.schema.json, .aide/refactors/refactor-plan.schema.json
- notes: Checks refactor plan schema and no-apply example plan shape.

### refactor_policy_golden

- result: PASS
- checks_run: 54
- passed_checks: 54
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/refactor-application.yaml, .aide/policies/refactor-safety.yaml, .aide/policies/refactor.yaml
- notes: Checks Q39 refactor policy anchors and dry-run only posture.

### reference_rewrite_plan_golden

- result: PASS
- checks_run: 513
- passed_checks: 513
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/reference-rewrite.yaml, .aide/refactors/reference-rewrite-entry.schema.json, .aide/refactors/reference-rewrite-plan.schema.json
- notes: Checks Q42 reference rewrite planning remains candidate-only.

### release_archive_generation_golden

- result: PASS
- checks_run: 8
- passed_checks: 8
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/dist/aide-lite-pack-v0.tar.gz, .aide/release/dist/aide-lite-pack-v0.zip, .aide/release/dist/install.md, .aide/release/dist/manifest.yaml
- notes: Checks local archive generation outputs exist and validate.

### release_asset_schema_golden

- result: PASS
- checks_run: 13
- passed_checks: 13
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/release-asset.schema.json
- notes: Checks release asset schema shape.

### release_bundle_policy_golden

- result: PASS
- checks_run: 54
- passed_checks: 54
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/release-artifacts.yaml, .aide/policies/release-bundle.yaml, .aide/policies/release-validation.yaml
- notes: Checks Q47 release policy anchors and local-only no-publish posture.

### release_checksum_validation_golden

- result: PASS
- checks_run: 3
- passed_checks: 3
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/dist/SHA256SUMS.txt, .aide/release/dist/aide-lite-pack-v0.checksums.json
- notes: Checks release checksum JSON and SHA256SUMS validation.

### release_fixture_extraction_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/dist/aide-lite-pack-v0.tar.gz, .aide/release/dist/aide-lite-pack-v0.zip
- notes: Checks archive extraction fixture validation.

### release_forbidden_paths_excluded_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/export-import.yaml, .aide/policies/release-artifacts.yaml, .aide/release/dist/aide-lite-pack-v0.tar.gz, .aide/release/dist/aide-lite-pack-v0.zip
- notes: Checks release archives exclude forbidden paths and generated release outputs are not target truth.

### release_manifest_schema_golden

- result: PASS
- checks_run: 11
- passed_checks: 11
- approx_tokens_if_applicable: n/a
- related_paths: .aide/release/release-manifest.schema.json
- notes: Checks release manifest schema shape.

### release_no_publish_golden

- result: PASS
- checks_run: 9
- passed_checks: 9
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/release-bundle.yaml, .aide/release/latest-release-bundle.json, .aide/scripts/aide_lite.py
- notes: Checks Q47 remains local-only and non-publishing.

### release_notes_preview_golden

- result: PASS
- checks_run: 7
- passed_checks: 7
- approx_tokens_if_applicable: n/a
- related_paths: .aide/changelog/RELEASE_NOTES.preview.md, .aide/changelog/release-notes.preview.json
- notes: Checks release-note preview extraction and preview-only caveat.

### repair_blocks_local_state_and_secrets_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/repair-classes.yaml, .aide/policies/repair-safety.yaml, .aide/repair/latest-repair-plan.json
- notes: Checks local state and secret-like repair findings are block/manual-review only.

### repair_classes_golden

- result: PASS
- checks_run: 62
- passed_checks: 62
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/repair-classes.yaml
- notes: Checks repair class vocabulary and safety gate metadata.

### repair_doctor_schema_golden

- result: PASS
- checks_run: 18
- passed_checks: 18
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repair/doctor-report.schema.json, .aide/repair/latest-doctor-repair-report.json
- notes: Checks doctor repair report schema and advisory-only report shape.

### repair_dry_run_schema_golden

- result: PASS
- checks_run: 19
- passed_checks: 19
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repair/latest-repair-dry-run.json, .aide/repair/repair-dry-run.schema.json
- notes: Checks repair dry-run schema and no-apply dry-run shape.

### repair_no_apply_golden

- result: PASS
- checks_run: 355
- passed_checks: 355
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repair/latest-repair-dry-run.json, .aide/repair/latest-repair-plan.json
- notes: Checks Q44 repair data never enables apply, overwrite, delete, or automatic migration.

### repair_plan_schema_golden

- result: PASS
- checks_run: 272
- passed_checks: 272
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repair/latest-repair-plan.json, .aide/repair/repair-operation.schema.json, .aide/repair/repair-plan.schema.json
- notes: Checks repair plan schema and generated no-apply plan shape.

### repair_policy_golden

- result: PASS
- checks_run: 62
- passed_checks: 62
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/repair.yaml, .aide/repair/repair-plan.schema.json
- notes: Checks Q44 repair policy anchors and preservation-first no-apply posture.

### repair_preserves_target_state_golden

- result: PASS
- checks_run: 18
- passed_checks: 18
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/repair-safety.yaml, .aide/repair/latest-repair-plan.json
- notes: Checks repair plans preserve target-specific state by default.

### repo_dependency_map_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/dependency-map.yaml, .aide/repo/dependency-map.json
- notes: Checks deterministic dependency map shape and Python import detection.

### repo_doc_link_map_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/doc-link-map.yaml, .aide/repo/doc-link-map.json
- notes: Checks doc link map shape and conservative stale-candidate language.

### repo_explain_file_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repo/file-inventory.json, .aide/scripts/aide_lite.py
- notes: Checks explain-file data for a stable AIDE Lite file.

### repo_intelligence_no_local_state_golden

- result: PASS
- checks_run: 3
- passed_checks: 3
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repo/file-inventory.json, .gitignore
- notes: Checks local state exclusion and local-path flagging.

### repo_inventory_schema_golden

- result: PASS
- checks_run: 21
- passed_checks: 21
- approx_tokens_if_applicable: n/a
- related_paths: .aide/repo/file-inventory.json, .aide/repo/file-inventory.schema.json
- notes: Checks Q37 inventory schema and required file inventory fields.

### repo_ownership_map_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/ownership-map.yaml, .aide/repo/ownership-map.json
- notes: Checks deterministic owner map includes key AIDE surfaces.

### reuse_modularity_report_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/reuse-modularity.yaml, .aide/reports/reuse-modularity-report.md
- notes: Checks reuse/modularity candidate-only reporting.

### review-packet-evidence-only

- result: PASS
- checks_run: 20
- passed_checks: 20
- approx_tokens_if_applicable: 1655
- related_paths: .aide/context/latest-review-packet.md, .aide/prompts/evidence-review.md, .aide/verification/review-packet.template.md
- notes: Checks review packet evidence-only shape.

### rollback_no_apply_golden

- result: PASS
- checks_run: 443
- passed_checks: 443
- approx_tokens_if_applicable: n/a
- related_paths: .aide/rollback/latest-rollback-dry-run.json, .aide/rollback/latest-rollback-plan.json
- notes: Checks rollback plans and dry-runs never enable apply, overwrite, delete, or managed-section removal.

### rollback_plan_schema_golden

- result: PASS
- checks_run: 385
- passed_checks: 385
- approx_tokens_if_applicable: n/a
- related_paths: .aide/rollback/latest-rollback-plan.json, .aide/rollback/rollback-operation.schema.json, .aide/rollback/rollback-plan.schema.json
- notes: Checks rollback plan schema and generated no-apply plan shape.

### rollback_policy_golden

- result: PASS
- checks_run: 40
- passed_checks: 40
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/rollback-safety.yaml, .aide/policies/rollback.yaml
- notes: Checks rollback policy anchors and no-apply preservation posture.

### root_exception_schema_golden

- result: PASS
- checks_run: 11
- passed_checks: 11
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/root-exception.schema.json, .aide/roots/root-exceptions.json
- notes: Checks root exception records include retirement conditions.

### root_fate_no_delete_approval_golden

- result: PASS
- checks_run: 7
- passed_checks: 7
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/root-fates.yaml, .aide/roots/latest-root-classification.json, .aide/roots/latest-root-recycling-plan.json
- notes: Checks root fate vocabulary never becomes deletion approval.

### root_file_classification_schema_golden

- result: PASS
- checks_run: 20
- passed_checks: 20
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/root-file-classification.schema.json, .aide/roots/latest-root-classification.json
- notes: Checks root file classification output shape and no-apply fates.

### root_inventory_schema_golden

- result: PASS
- checks_run: 18
- passed_checks: 18
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/root-inventory.schema.json, .aide/roots/latest-root-inventory.json
- notes: Checks root inventory schema and generated inventory shape.

### root_record_schema_golden

- result: PASS
- checks_run: 13
- passed_checks: 13
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/root-record.schema.json
- notes: Checks root record schema shape.

### root_recycling_plan_schema_golden

- result: PASS
- checks_run: 40
- passed_checks: 40
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/root-recycling-plan.schema.json, .aide/roots/latest-root-recycling-plan.json
- notes: Checks root recycling plan output shape and no-apply posture.

### root_recycling_policy_golden

- result: PASS
- checks_run: 48
- passed_checks: 48
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/root-fates.yaml, .aide/policies/root-inventory.yaml, .aide/policies/root-recycling.yaml, .aide/policies/root-risk.yaml
- notes: Checks Q40 root recycling policy anchors and no-apply posture.

### roots_no_apply_golden

- result: PASS
- checks_run: 40
- passed_checks: 40
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/root-recycling.yaml, .aide/roots/latest-root-classification.json, .aide/roots/latest-root-recycling-plan.json
- notes: Checks root inventory, classification, and plan outputs remain no-apply.

### salvage_map_policy_golden

- result: PASS
- checks_run: 317
- passed_checks: 317
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/salvage-map.yaml, .aide/refactors/salvage-map-entry.schema.json, .aide/refactors/salvage-map.schema.json
- notes: Checks Q42 salvage-map policy anchors and preservation candidate shape.

### salvage_map_schema_golden

- result: PASS
- checks_run: 11
- passed_checks: 11
- approx_tokens_if_applicable: n/a
- related_paths: .aide/refactors/salvage-map.schema.json
- notes: Checks salvage-map schema exists and remains no-apply.

### sync_policy_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/git/sync-policy.md, .aide/policies/sync-policy.yaml
- notes: Checks multi-machine sync policy anchors remain report-only.

### task_resumption_standard_golden

- result: PASS
- checks_run: 15
- passed_checks: 15
- approx_tokens_if_applicable: n/a
- related_paths: .aide/context/latest-task-packet.md, .aide/policies/task-resumption.yaml, .aide/queue/index.yaml, .aide/reports/aide-task-resumption-standard.md
- notes: Checks repeated and out-of-order task recovery policy anchors.

### test_coverage_map_golden

- result: PASS
- checks_run: 4
- passed_checks: 4
- approx_tokens_if_applicable: n/a
- related_paths: .aide/quality/test-coverage-map.schema.json, .aide/reports/test-coverage-map.md
- notes: Checks heuristic test coverage map shape.

### token-ledger-budget-check

- result: PASS
- checks_run: 14
- passed_checks: 14
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/token-ledger.yaml, .aide/reports/token-ledger.jsonl, .aide/reports/token-savings-summary.md
- notes: Checks estimated token metadata without raw prompt or response storage.

### tool_absorption_policy_golden

- result: PASS
- checks_run: 55
- passed_checks: 55
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/tool-absorption.yaml, .aide/policies/tool-capabilities.yaml, .aide/policies/tool-fates.yaml, .aide/policies/tool-inventory.yaml, .aide/policies/tool-risk.yaml, .aide/policies/tool-wrapping.yaml
- notes: Checks Q41 tool absorption policy anchors and preservation posture.

### tool_adapter_map_schema_golden

- result: PASS
- checks_run: 44811
- passed_checks: 44811
- approx_tokens_if_applicable: n/a
- related_paths: .aide/tools/latest-tool-adapter-map.json, .aide/tools/tool-adapter-map.schema.json
- notes: Checks tool adapter-map schema and advisory mapping output.

### tool_fate_no_delete_approval_golden

- result: PASS
- checks_run: 8
- passed_checks: 8
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/tool-fates.yaml, .aide/tools/latest-tool-classification.json, .aide/tools/latest-tool-wrap-plan.json
- notes: Checks tool fate vocabulary never becomes deletion or execution approval.

### tool_inventory_schema_golden

- result: PASS
- checks_run: 23
- passed_checks: 23
- approx_tokens_if_applicable: n/a
- related_paths: .aide/tools/latest-tool-inventory.json, .aide/tools/tool-inventory.schema.json
- notes: Checks tool inventory schema and generated inventory shape.

### tool_record_schema_golden

- result: PASS
- checks_run: 13
- passed_checks: 13
- approx_tokens_if_applicable: n/a
- related_paths: .aide/tools/tool-record.schema.json
- notes: Checks tool record schema shape.

### tool_wrap_plan_schema_golden

- result: PASS
- checks_run: 44815
- passed_checks: 44815
- approx_tokens_if_applicable: n/a
- related_paths: .aide/tools/latest-tool-wrap-plan.json, .aide/tools/tool-wrap-plan.schema.json
- notes: Checks tool wrap-plan schema and no-execution output shape.

### tools_no_execution_golden

- result: PASS
- checks_run: 44836
- passed_checks: 44836
- approx_tokens_if_applicable: n/a
- related_paths: .aide/tools/latest-tool-adapter-map.json, .aide/tools/latest-tool-classification.json, .aide/tools/latest-tool-inventory.json, .aide/tools/latest-tool-wrap-plan.json
- notes: Checks Q41 tool outputs never enable unknown execution, apply, rename, deletion, or migration.

### uninstall_no_apply_golden

- result: PASS
- checks_run: 75258
- passed_checks: 75258
- approx_tokens_if_applicable: n/a
- related_paths: .aide/uninstall/latest-uninstall-dry-run.json, .aide/uninstall/latest-uninstall-plan.json
- notes: Checks uninstall plans and dry-runs never enable apply, delete, or managed-section removal.

### uninstall_no_blanket_aide_delete_golden

- result: PASS
- checks_run: 92027
- passed_checks: 92027
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/uninstall-safety.yaml, .aide/uninstall/latest-uninstall-plan.json
- notes: Checks uninstall never plans blanket .aide deletion.

### uninstall_plan_schema_golden

- result: PASS
- checks_run: 92031
- passed_checks: 92031
- approx_tokens_if_applicable: n/a
- related_paths: .aide/uninstall/latest-uninstall-plan.json, .aide/uninstall/uninstall-operation.schema.json, .aide/uninstall/uninstall-plan.schema.json
- notes: Checks uninstall plan schema and generated no-apply plan shape.

### uninstall_policy_golden

- result: PASS
- checks_run: 40
- passed_checks: 40
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/uninstall-safety.yaml, .aide/policies/uninstall.yaml
- notes: Checks uninstall policy anchors and no-blanket-delete posture.

### uninstall_preserves_target_state_golden

- result: PASS
- checks_run: 4495
- passed_checks: 4495
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/uninstall-safety.yaml, .aide/uninstall/latest-uninstall-plan.json
- notes: Checks uninstall preserves target-specific memory, queue, evidence, manual content, tools, local state, and unknowns.

### upgrade_compatibility_policy_golden

- result: PASS
- checks_run: 65
- passed_checks: 65
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/upgrade-compatibility.yaml, .aide/upgrade/upgrade-compatibility-report.schema.json
- notes: Checks compatibility dimensions and future-gated migration levels.

### upgrade_dry_run_schema_golden

- result: PASS
- checks_run: 21
- passed_checks: 21
- approx_tokens_if_applicable: n/a
- related_paths: .aide/upgrade/latest-upgrade-dry-run.json, .aide/upgrade/upgrade-dry-run.schema.json
- notes: Checks upgrade dry-run schema and no-apply dry-run shape.

### upgrade_mandatory_migration_gate_golden

- result: PASS
- checks_run: 27
- passed_checks: 27
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/upgrade-migrations.yaml, .aide/upgrade/latest-upgrade-migration-report.md, .aide/upgrade/upgrade-migration-report.schema.json
- notes: Checks mandatory migrations are future-gated, non-automatic, and no-apply.

### upgrade_no_apply_golden

- result: PASS
- checks_run: 5892
- passed_checks: 5892
- approx_tokens_if_applicable: n/a
- related_paths: .aide/upgrade/latest-upgrade-dry-run.json, .aide/upgrade/latest-upgrade-plan.json
- notes: Checks Q45 upgrade data never enables apply, overwrite, delete, or automatic migration.

### upgrade_no_source_state_leak_golden

- result: PASS
- checks_run: 13
- passed_checks: 13
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/upgrade-preservation.yaml, .aide/upgrade/latest-upgrade-plan.json
- notes: Checks source-generated, local, and secret-like state is never planned as upgrade truth.

### upgrade_plan_schema_golden

- result: PASS
- checks_run: 13296
- passed_checks: 13296
- approx_tokens_if_applicable: n/a
- related_paths: .aide/upgrade/latest-upgrade-plan.json, .aide/upgrade/upgrade-operation.schema.json, .aide/upgrade/upgrade-plan.schema.json
- notes: Checks upgrade plan schema and generated no-apply plan shape.

### upgrade_policy_golden

- result: PASS
- checks_run: 63
- passed_checks: 63
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/upgrade.yaml, .aide/upgrade/upgrade-plan.schema.json
- notes: Checks Q45 upgrade policy anchors and preservation-first no-apply posture.

### upgrade_preserves_target_state_golden

- result: PASS
- checks_run: 9
- passed_checks: 9
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/upgrade-preservation.yaml, .aide/upgrade/latest-upgrade-plan.json
- notes: Checks upgrade plans preserve target-specific state by default.

### verifier-detects-bad-evidence

- result: PASS
- checks_run: 3
- passed_checks: 3
- approx_tokens_if_applicable: n/a
- related_paths: .aide/evals/golden-tasks/verifier-detects-bad-evidence/fixtures/missing-sections.md, .aide/verification/evidence-packet.template.md
- notes: Passes when the verifier refuses to accept malformed evidence silently.

### workunit_idempotency_golden

- result: PASS
- checks_run: 17
- passed_checks: 17
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/recovery.yaml, .aide/policies/work-units.yaml, .aide/reports/aide-workunit-recovery-standard.md
- notes: Checks WorkUnit idempotency and no-op behavior.

### workunit_sizing_policy_golden

- result: PASS
- checks_run: 12
- passed_checks: 12
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/workunit-sizing.yaml
- notes: Checks WorkUnit sizing policy anchors and split gates.

## Limitations

- Deterministic local checks only.
- No model/provider/network calls.
- No external benchmark or arbitrary code semantic proof.
