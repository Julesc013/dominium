Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: DIST
Replacement Target: DIST-2 artifact integrity verification and installer-free packaging hardening

# Distribution Content Audit

## Included Packs

- `store/packs/base/pack.base.procedural`
- `store/packs/official/pack.earth.procedural`
- `store/packs/official/pack.sol.pin_minimal`

## Layout Findings

- Unexpected top-level entries: `LICENSES, cache, content, contracts, descriptors, exports, logs, ops, release.manifest.json, semantic_contract_registry.json`
- Dev artifacts: `archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_adapter_compiler.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_aide_lite.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_cache_local_state.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_export_import.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_gateway_commands.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_golden_tasks.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_outcome_controller.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_provider_adapter.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q27_commit_recovery.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q28_git_workflow.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q29_git_helper.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q31_export_pack_governance.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q34_changelog_release.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q35_github_advisory.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q36_intent_compiler.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q37_repo_intelligence.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q38_file_quality.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q39_refactor_control.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q40_root_recycling.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q41_tool_absorption.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q42_move_map_aliases.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q43_install_plan.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q44_repair_doctor.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q45_upgrade_model.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q46_rollback_uninstall.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q47_release_bundle.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_q48_github_release_draft.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_review_pack.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_router_profile.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_token_ledger.pyc, archive/generated/aide/export/aide-lite-pack-v0/files/.aide/scripts/tests/test_verifier.pyc, release/packaging/setup/scripts/packaging/tests/exe_validation_test.pyc, release/packaging/setup/scripts/packaging/tests/macos_validation_test.pyc, release/packaging/setup/scripts/packaging/tests/msi_validation_test.pyc, release/packaging/setup/scripts/packaging/tests/packaging_validation_test.pyc`
- Missing required packs: `none`
- Unexpected extra packs: `none`

## Large Files

- `bin/client.exe`: 2562048 bytes
- `bin/launcher.exe`: 1774592 bytes
- `bin/server.exe`: 2337792 bytes
- `bin/setup.exe`: 1412096 bytes
- `bin/tools.exe`: 2465280 bytes
- `contracts/registry/architecture/module_registry.json`: 1874744 bytes
- `contracts/registry/architecture/module_registry.v1.json`: 1874968 bytes
- `tools/xstack/sessionx/process_runtime.pyc`: 1731238 bytes
