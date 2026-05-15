# Stable Install Audit

Status: needs_review

- Q50 mode: `UPGRADE_EXISTING_AIDE`.
- Source bundle: recorded by Q49/Q50 as validated with warnings; sibling `../aide` currently has release dist manifest, SHA256SUMS, zip, and export manifest.
- Files synced: portable `.aide` control-plane files only, per Q50 evidence.
- Preserved: target memory, queue, reports, context, golden tasks, doctrine refs, AGENTS manual content, legacy tools, product/source roots, local ignored state.
- Skipped/excluded: source AIDE memory, queue/history, generated source context/reports, `.aide.local`, secrets, raw prompts/responses.
- Current lifecycle status: install/repair/upgrade/rollback/uninstall observe/plan/dry-run/validate commands run no-apply and record conflicts/preservations instead of writes.
- Current caveat: target-local release commands fail because Dominium does not currently contain a local release bundle; this is not a blocker for target operation.
