# Tool Inventory

- generated_by: aide-lite
- source_commit: 80dc7bfb58a1cdc887ee1fed8a83fb22ff3028e0
- tool_count: 2831
- no_apply: true
- execution_allowed: false
- tool_deletion: false
- tool_rename: false
- tool_migration: false

## Capability Counts

- audit: 1020
- build: 225
- context: 200
- docs: 464
- format: 42
- generate: 125
- install: 76
- lint: 3
- migrate: 6
- package: 203
- release: 133
- repo_policy: 224
- security: 18
- test: 158
- unknown: 846
- validate: 198

## Tools

- `.aide/adapters/templates/continue-checks.template.md`: capabilities=validate risk=medium fate=wrap
- `.aide/cache/latest-cache-keys.json`: capabilities=test risk=medium fate=wrap
- `.aide/cache/latest-cache-keys.md`: capabilities=test risk=medium fate=wrap
- `.aide/changelog/RELEASE_NOTES.preview.md`: capabilities=release risk=release fate=wrap
- `.aide/context/latest-context-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/latest-review-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/latest-task-packet.md`: capabilities=context,test risk=medium fate=wrap
- `.aide/context/test-map.json`: capabilities=context,test risk=medium fate=wrap
- `.aide/evals/runs/latest-golden-tasks.json`: capabilities=test risk=medium fate=wrap
- `.aide/evals/runs/latest-golden-tasks.md`: capabilities=test risk=medium fate=wrap
- `.aide/git/latest-helper-plan.json`: capabilities=test risk=medium fate=wrap
- `.aide/git/latest-helper-plan.md`: capabilities=test risk=medium fate=wrap
- `.aide/git/sync-policy.md`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/hooks/commit-msg`: capabilities=unknown risk=unknown fate=unknown
- `.aide/import-policy.template.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/import-report.template.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/policies/export-import.yaml`: capabilities=unknown risk=unknown fate=unknown
- `.aide/policies/sync-policy.yaml`: capabilities=repo_policy risk=medium fate=wrap
- `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/install-upgrade-risk-report.md`: capabilities=audit,install,repo_policy risk=medium fate=wrap
- `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/release-bundle-readiness.md`: capabilities=package,release risk=release fate=wrap
- `.aide/queue/DOMINIUM-AIDE-PILOT-01/import-report.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/queue/DOMINIUM-AIDE-SYNC-01/evidence/sync-report.md`: capabilities=audit,repo_policy risk=low fate=wrap
- `.aide/repo/generated-map.json`: capabilities=generate,repo_policy risk=medium fate=wrap
- `.aide/repo/latest-repo-intelligence.md`: capabilities=repo_policy,test risk=medium fate=wrap
- `.aide/repo/test-map.json`: capabilities=repo_policy,test risk=medium fate=wrap
- `.aide/reports/dominium-fresh-install-preflight.md`: capabilities=audit,install,repo_policy risk=medium fate=wrap
- `.aide/reports/dominium-release-bundle-readiness.md`: capabilities=audit,package,release,repo_policy risk=release fate=wrap
- `.aide/routing/latest-route-decision.json`: capabilities=test risk=medium fate=wrap
- `.aide/routing/latest-route-decision.md`: capabilities=test risk=medium fate=wrap
- `.aide/scripts/aide_lite.py`: capabilities=context,repo_policy,test,validate risk=medium fate=keep
- `.aide/verification/latest-verification-report.md`: capabilities=audit,repo_policy,test risk=medium fate=wrap
- `.github/workflows/ci.yml`: capabilities=unknown risk=unknown fate=unknown
- `CMakeLists.txt`: capabilities=build risk=medium fate=wrap
- `apps/client/CMakeLists.txt`: capabilities=build risk=medium fate=wrap
- `apps/client/presentation/frame_graph_builder.cpp`: capabilities=build risk=medium fate=wrap
- `apps/client/presentation/frame_graph_builder.h`: capabilities=build risk=medium fate=wrap
- `apps/launcher/CMakeLists.txt`: capabilities=build risk=medium fate=wrap
- `apps/server/CMakeLists.txt`: capabilities=build risk=medium fate=wrap
- `apps/server/persistence/dom_checkpoint_policy.h`: capabilities=repo_policy,validate risk=medium fate=wrap
- `apps/server/persistence/dom_checkpointing.cpp`: capabilities=validate risk=medium fate=wrap
- `apps/server/persistence/dom_checkpointing.h`: capabilities=validate risk=medium fate=wrap
- `apps/server/persistence/integrity_checkpoints.cpp`: capabilities=validate risk=medium fate=wrap
- `apps/server/persistence/integrity_checkpoints.h`: capabilities=validate risk=medium fate=wrap
- `apps/setup/CMakeLists.txt`: capabilities=build risk=medium fate=wrap
- `apps/setup/packages/scripts/build_all.bat`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/build_codex_verify.bat`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/check_layers.py`: capabilities=context,package,validate risk=medium fate=wrap
- `apps/setup/packages/scripts/ci/check_launcher_core_invariants.py`: capabilities=context,package,validate risk=medium fate=wrap
- `apps/setup/packages/scripts/ci/launcher_cli_smoke_matrix.py`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/ci/setup_build.bat`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/ci/setup_build.sh`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/ci/setup_test.bat`: capabilities=context,package,test risk=medium fate=wrap
- `apps/setup/packages/scripts/ci/setup_test.sh`: capabilities=context,package,test risk=medium fate=wrap
- `apps/setup/packages/scripts/commit_template.md`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/diagnostics/make_support_bundle.py`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/doc_ratio_check.py`: capabilities=context,package,validate risk=medium fate=wrap
- `apps/setup/packages/scripts/gen_base_demo_mod.py`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/gen_changelog.bat`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/gen_launcher_ui_schema_v1.py`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/gen_tools_demo.py`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/legacy/build_legacy_windows.bat`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/legacy/build_legacy_windows.sh`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/legacy/build_packages.bat`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/legacy/build_packages.sh`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/legacy/run_setup_tests.bat`: capabilities=context,package,test risk=medium fate=wrap
- `apps/setup/packages/scripts/legacy/run_setup_tests.sh`: capabilities=context,package,test risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/CMakeLists.txt`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/dsumanifest.py`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/CMakeLists.txt`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/build_run.sh`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/deb/DEBIAN/control.in`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/deb/DEBIAN/postinst`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/deb/DEBIAN/postrm`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/deb/DEBIAN/prerm`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/dominium-install.sh`: capabilities=context,install,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/dominium-installer.sh.in`: capabilities=context,install,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/rpm/dominium.spec.in`: capabilities=context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/linux/write_apprun.cmake`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/macos/CMakeLists.txt`: capabilities=build,context,package risk=medium fate=wrap
- `apps/setup/packages/scripts/packaging/macos/Dominium.app/Contents/Info.plist.in`: capabilities=context,package risk=low fate=wrap

## Warnings

- unknown_tool_candidates: .aide/hooks/commit-msg, .aide/policies/export-import.yaml, .github/workflows/ci.yml, archive/legacy/setup_core_setup/setup/core/import/dsk_import_legacy.cpp, contracts/schemas/net_resync_strategy_registry.schema.json, contracts/schemas/tools/SPEC_TOOL_CAPABILITIES.md, contracts/schemas/tools/SPEC_TOOL_INTENTS.md, contracts/schemas/tools/SPEC_TOOL_SCOPING.md, contracts/schemas/world/SPEC_WORLD_DATA_IMPORT.md, data/registries/net_resync_strategy_registry.json, engine/modules/caps/d_caps_export.c, game/domains/embodiment/tools/__init__.py
- high_risk_tool_candidates: .aide/changelog/RELEASE_NOTES.preview.md, .aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/release-bundle-readiness.md, .aide/reports/dominium-release-bundle-readiness.md, apps/setup/packages/scripts/packaging/stage_dist.cmake, apps/setup/packages/scripts/release/run_release_gate.bat, apps/setup/packages/scripts/release/run_release_gate.sh, apps/setup/packages/scripts/release/run_setup_release_gate.bat, apps/setup/packages/scripts/release/run_setup_release_gate.sh, apps/setup/packages/scripts/verify_release.bat, archive/legacy/_orphaned_stage2/tools_common/dom_tool_validate.cpp, archive/legacy/_orphaned_stage2/tools_common/dom_tool_validate.h, archive/legacy/_orphaned_stage2/tools_core/CMakeLists.txt

## Next

- Q42 Move Map / Salvage Map / Path Alias v0.
