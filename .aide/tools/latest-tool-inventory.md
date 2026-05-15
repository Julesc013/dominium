# Tool Inventory

- generated_by: aide-lite
- source_commit: 52eeb5a1f481231d55ad0938a8c9b3b54e2aa83f
- tool_count: 2995
- no_apply: true
- execution_allowed: false
- tool_deletion: false
- tool_rename: false
- tool_migration: false

## Capability Counts

- audit: 1040
- build: 225
- context: 204
- docs: 465
- format: 42
- generate: 126
- install: 170
- lint: 3
- migrate: 6
- package: 206
- release: 158
- repo_policy: 251
- security: 18
- test: 234
- unknown: 854
- validate: 206

## Tools

- `.aide/adapters/templates/continue-checks.template.md`: capabilities=validate risk=medium fate=wrap
- `.aide/cache/latest-cache-keys.json`: capabilities=test risk=medium fate=wrap
- `.aide/cache/latest-cache-keys.md`: capabilities=test risk=medium fate=wrap
- `.aide/changelog/RELEASE_NOTES.preview.md`: capabilities=release risk=release fate=wrap
- `.aide/changelog/latest-changelog-report.md`: capabilities=audit,repo_policy,test risk=medium fate=wrap
- `.aide/changelog/release-notes.preview.json`: capabilities=release risk=release fate=wrap
- `.aide/changelog/templates/release-notes.md.template`: capabilities=release risk=release fate=wrap
- `.aide/context/latest-context-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/latest-review-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/latest-task-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/test-map.json`: capabilities=context,test risk=medium fate=wrap
- `.aide/evals/runs/latest-golden-tasks.json`: capabilities=test risk=medium fate=wrap
- `.aide/evals/runs/latest-golden-tasks.md`: capabilities=test risk=medium fate=wrap
- `.aide/gateway/latest-gateway-status.json`: capabilities=test risk=medium fate=wrap
- `.aide/gateway/latest-gateway-status.md`: capabilities=test risk=medium fate=wrap
- `.aide/git/latest-helper-plan.json`: capabilities=test risk=medium fate=wrap
- `.aide/git/latest-helper-plan.md`: capabilities=test risk=medium fate=wrap
- `.aide/git/sync-policy.md`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/hooks/commit-msg`: capabilities=unknown risk=unknown fate=unknown
- `.aide/import-policy.template.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/import-report.template.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/install/install-dry-run.schema.json`: capabilities=install risk=medium fate=wrap
- `.aide/install/install-observation.schema.json`: capabilities=install risk=medium fate=wrap
- `.aide/install/install-operation.schema.json`: capabilities=install risk=medium fate=wrap
- `.aide/install/install-plan.schema.json`: capabilities=install risk=medium fate=wrap
- `.aide/install/install-verification.schema.json`: capabilities=install risk=medium fate=wrap
- `.aide/install/latest-conflict-report.json`: capabilities=audit,install,repo_policy,test risk=medium fate=wrap
- `.aide/install/latest-conflict-report.md`: capabilities=audit,install,repo_policy,test risk=medium fate=wrap
- `.aide/install/latest-install-dry-run.json`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-install-dry-run.md`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-install-observation.json`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-install-observation.md`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-install-plan.json`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-install-plan.md`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-ownership-ledger.example.json`: capabilities=install,test risk=medium fate=wrap
- `.aide/install/latest-preservation-report.md`: capabilities=audit,install,repo_policy,test risk=medium fate=wrap
- `.aide/install/latest-verification-plan.md`: capabilities=install,test risk=medium fate=wrap
- `.aide/intake/latest-intent-packet.json`: capabilities=context,test risk=medium fate=wrap
- `.aide/intake/latest-intent-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/intake/latest-workunit-draft.json`: capabilities=test risk=medium fate=wrap
- `.aide/intake/latest-workunit-draft.md`: capabilities=test risk=medium fate=wrap
- `.aide/policies/doctor.yaml`: capabilities=validate risk=medium fate=wrap
- `.aide/policies/export-import.yaml`: capabilities=unknown risk=unknown fate=unknown
- `.aide/policies/github-release-draft.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/install-conflicts.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/install-migrations.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/install-ownership.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/install-preservation.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/install-verification.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/install.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/release-artifacts.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/release-bundle.yaml`: capabilities=package,release risk=release fate=wrap
- `.aide/policies/release-checklist.yaml`: capabilities=release,validate risk=release fate=wrap
- `.aide/policies/release-provenance.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/release-publication-boundary.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/release-upload-plan.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/release-validation.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/release-versioning.yaml`: capabilities=release risk=release fate=wrap
- `.aide/policies/rollback-classes.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/rollback-safety.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/rollback-verification.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/rollback.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/sync-policy.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/policies/test-map.yaml`: capabilities=test risk=medium fate=wrap
- `.aide/policies/uninstall-classes.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/uninstall-safety.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/uninstall-verification.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/uninstall.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/upgrade-compatibility.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/upgrade-conflicts.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/upgrade-migrations.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/upgrade-preservation.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/upgrade-verification.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/policies/upgrade.yaml`: capabilities=install risk=medium fate=wrap
- `.aide/providers/latest-provider-status.json`: capabilities=test risk=medium fate=wrap
- `.aide/providers/latest-provider-status.md`: capabilities=test risk=medium fate=wrap
- `.aide/quality/test-coverage-map.schema.json`: capabilities=test risk=medium fate=wrap
- `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/install-upgrade-risk-report.md`: capabilities=audit,install,repo_policy risk=medium fate=wrap
- `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/release-bundle-readiness.md`: capabilities=package,release risk=release fate=wrap
- `.aide/queue/DOMINIUM-AIDE-PILOT-01/import-report.md`: capabilities=audit,repo_policy risk=low fate=wrap

## Warnings

- unknown_tool_candidates: .aide/hooks/commit-msg, .aide/policies/export-import.yaml, .aide/tools/tool-adapter-map.schema.json, .aide/tools/tool-capability.schema.json, .aide/tools/tool-evidence.schema.json, .aide/tools/tool-inventory.schema.json, .aide/tools/tool-record.schema.json, .aide/tools/tool-retirement.schema.json, .aide/tools/tool-risk.schema.json, .aide/tools/tool-wrap-plan.schema.json, .github/workflows/ci.yml, archive/legacy/setup_core_setup/setup/core/import/dsk_import_legacy.cpp
- high_risk_tool_candidates: .aide/changelog/RELEASE_NOTES.preview.md, .aide/changelog/release-notes.preview.json, .aide/changelog/templates/release-notes.md.template, .aide/policies/github-release-draft.yaml, .aide/policies/release-artifacts.yaml, .aide/policies/release-bundle.yaml, .aide/policies/release-checklist.yaml, .aide/policies/release-provenance.yaml, .aide/policies/release-publication-boundary.yaml, .aide/policies/release-upload-plan.yaml, .aide/policies/release-validation.yaml, .aide/policies/release-versioning.yaml

## Next

- Q42 Move Map / Salvage Map / Path Alias v0.
