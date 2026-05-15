# AIDE Rollback Plan

- plan_id: rollback-plan-current
- status: candidate
- operations: 20
- preserved_paths: 3811
- blocked_reasons: blocked_missing_ledger
- no_apply: true
- overwrite_allowed_default: false
- delete_allowed_default: false
- managed_section_removal_allowed_default: false

Rollback actions are future candidates only.
- blocked_missing_ledger: .aide/ownership-evidence (blocked_missing_ledger)
- preserve: .aide/repo/dependency-map.schema.json (preserve_target_specific)
- preserve: .aide/repo/doc-link-map.schema.json (preserve_target_specific)
- preserve: .aide/repo/file-inventory.schema.json (preserve_target_specific)
- preserve: .aide/repo/ownership-map.schema.json (preserve_target_specific)
- preserve: .aide/repo/repo-intelligence-summary.schema.json (preserve_target_specific)
- preserve: .aide/repo/test-map.schema.json (preserve_target_specific)
- preserve: .aide/reports/aide-commit-message-standard.md (preserve_target_specific)
- preserve: .aide/reports/aide-task-resumption-standard.md (preserve_target_specific)
- preserve: .aide/reports/aide-workunit-recovery-standard.md (preserve_target_specific)
- preserve: .aide/reports/file-quality-ledger.schema.json (preserve_target_specific)
- preserve: .aide/tools/README.md (preserve_target_specific)
- preserve: .aide/tools/tool-adapter-map.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-capability.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-evidence.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-inventory.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-record.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-retirement.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-risk.schema.json (preserve_target_specific)
- preserve: .aide/tools/tool-wrap-plan.schema.json (preserve_target_specific)
