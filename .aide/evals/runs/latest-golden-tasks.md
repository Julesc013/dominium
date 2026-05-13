# Latest Golden Tasks

- result: PASS
- task_count: 25
- pass_count: 25
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

### changelog_preview_golden

- result: PASS
- checks_run: 5
- passed_checks: 5
- approx_tokens_if_applicable: n/a
- related_paths: .aide/changelog/CHANGELOG.preview.md, .aide/changelog/RELEASE_NOTES.preview.md, .aide/policies/commit-messages.yaml
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
- approx_tokens_if_applicable: 1060
- related_paths: .aide/context/latest-task-packet.md, .aide/policies/token-budget.yaml, .aide/prompts/compact-task.md
- notes: Checks the compact task packet shape and forbidden prompt discipline.

### context-packet-no-full-repo-dump

- result: PASS
- checks_run: 17
- passed_checks: 17
- approx_tokens_if_applicable: 475
- related_paths: .aide/context/context-index.json, .aide/context/latest-context-packet.md, .aide/context/repo-map.json, .aide/context/test-map.json
- notes: Checks context refs instead of whole-repo dumps.

### export_pack_commit_policy_inclusion_golden

- result: PASS
- checks_run: 1
- passed_checks: 1
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/git/commit-template.md, .aide/hooks/commit-msg, .aide/policies/commit-messages.yaml
- notes: Checks portable commit discipline and changelog support are exported from source-pack repos.

### export_pack_excludes_source_branch_state_golden

- result: PASS
- checks_run: 1
- passed_checks: 1
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/policies/export-import.yaml
- notes: Checks source-specific Git detection, helper plans, branch policy, and generated previews are not exported as target truth.

### export_pack_git_policy_inclusion_golden

- result: PASS
- checks_run: 1
- passed_checks: 1
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/git/helper-policy.yaml, .aide/policies/branch-roles.yaml, .aide/policies/git-workflow.yaml
- notes: Checks portable Git workflow and helper governance are exported from source-pack repos.

### export_pack_task_recovery_inclusion_golden

- result: PASS
- checks_run: 1
- passed_checks: 1
- approx_tokens_if_applicable: n/a
- related_paths: .aide/export/aide-lite-pack-v0/manifest.yaml, .aide/policies/recovery.yaml, .aide/policies/task-resumption.yaml, .aide/policies/work-units.yaml
- notes: Checks portable task resumption, WorkUnit, and recovery governance are exported from source-pack repos.

### fixture_import_governance_commands_golden

- result: PASS
- checks_run: 1
- passed_checks: 1
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

### review-packet-evidence-only

- result: PASS
- checks_run: 20
- passed_checks: 20
- approx_tokens_if_applicable: 1141
- related_paths: .aide/context/latest-review-packet.md, .aide/prompts/evidence-review.md, .aide/verification/review-packet.template.md
- notes: Checks review packet evidence-only shape.

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

### token-ledger-budget-check

- result: PASS
- checks_run: 14
- passed_checks: 14
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/token-ledger.yaml, .aide/reports/token-ledger.jsonl, .aide/reports/token-savings-summary.md
- notes: Checks estimated token metadata without raw prompt or response storage.

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

## Limitations

- Deterministic local checks only.
- No model/provider/network calls.
- No external benchmark or arbitrary code semantic proof.
