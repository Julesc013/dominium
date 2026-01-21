# Release Readiness Checklist (Setup + Launcher)

Each checkbox maps an acceptance criterion to code, tests, and a verification command.

## A1) Setup system readiness

- [x] Manifest validate + dump
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/manifest/dsu_manifest.c
  Tests: dsu_manifest_test, dsu_cli_test (goldens)
  Commits: 24e31e7
  Verify: dominium-setup manifest validate --in assets/setup/manifests/dominium_full.dsumanifest
          dominium-setup manifest dump --in assets/setup/manifests/dominium_full.dsumanifest --out out.json --format json
          ctest --preset debug -R dsu_manifest_test

- [x] Resolve
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/resolve/dsu_resolve.c
  Tests: dsu_resolve_test, dsu_cli_test
  Commits: 24e31e7
  Verify: dominium-setup export-invocation --manifest assets/setup/manifests/dominium_full.dsumanifest --op install --scope user --out install.dsuinv
          dominium-setup resolve --manifest assets/setup/manifests/dominium_full.dsumanifest --invocation install.dsuinv --json
          ctest --preset debug -R dsu_resolve_test

- [x] Plan
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/plan/dsu_plan.c
  Tests: dsu_cli_test, test_plan_determinism_repeat_run
  Commits: 9e4415b, 24e31e7
  Verify: dominium-setup export-invocation --manifest assets/setup/manifests/dominium_full.dsumanifest --op install --scope user --out out.dsuinv
          dominium-setup plan --manifest assets/setup/manifests/dominium_full.dsumanifest --invocation out.dsuinv --out out.dsuplan
          ctest --preset debug -R test_plan_determinism_repeat_run

- [x] Apply (install/upgrade/repair/uninstall)
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/txn/dsu_txn.c
  Tests: test_install_fresh_portable, test_upgrade_in_place, test_upgrade_side_by_side,
         test_repair_restores_missing_files, test_uninstall_preserves_user_data, test_uninstall_removes_owned_files
  Commits: 9e4415b
  Verify: ctest --preset debug -R test_install_fresh_portable
          ctest --preset debug -R test_upgrade_in_place
          ctest --preset debug -R test_repair_restores_missing_files

- [x] Verify
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/txn/dsu_txn.c
  Tests: test_verify_detects_modified_file, dsu_txn_test
  Commits: 9e4415b
  Verify: dominium-setup verify --state <state> --format json
          ctest --preset debug -R test_verify_detects_modified_file

- [x] Rollback (journal)
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/txn/dsu_txn.c
  Tests: test_rollback_on_commit_failure, dsu_txn_test
  Commits: 9e4415b
  Verify: dominium-setup rollback --journal <journal> --dry-run
          ctest --preset debug -R test_rollback_on_commit_failure

- [x] Reports and forensic exports
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/report/dsu_report.c
  Tests: dsu_cli_test (report + export-log goldens)
  Commits: 24e31e7
  Verify: dominium-setup report --state <state> --out report --format json
          dominium-setup export-log --log audit.dsu.log --out audit.json --format json
          ctest --preset debug -R dsu_cli_test

- [x] Deterministic mode yields byte-identical plan files + JSON outputs (with deterministic test seed for instance id)
  Code: source/dominium/setup/cli/dominium_setup_main.c, source/dominium/setup/core/src/plan/dsu_plan.c,
        source/dominium/setup/core/src/state/dsu_state_s5.c, source/dominium/setup/core/src/txn/dsu_txn.c
  Tests: test_plan_determinism_repeat_run, dsu_cli_test, dsu_packaging_validation_test
  Commits: 9e4415b
  Verify: ctest --preset debug -R test_plan_determinism_repeat_run
          ctest --preset debug -R dsu_cli_test
          ctest --preset debug -R dsu_packaging_validation_test

- [x] Platform iface implemented + idempotent
  Code: source/dominium/setup/core/src/platform_iface/dsu_platform_iface.c
  Tests: dsu_platform_iface_test
  Commits: 9e4415b
  Verify: ctest --preset debug -R dsu_platform_iface_test

- [x] Platform register/unregister flows callable + tested (mocked where needed)
  Code: source/dominium/setup/adapters, source/dominium/setup/core/src/platform_iface
  Tests: test_platform_iface_idempotent_register_unregister, dsu_adapter_smoke_test
  Commits: 9e4415b, 24e31e7
  Verify: ctest --preset debug -R test_platform_iface_idempotent_register_unregister

## A2) Native launcher set readiness

- [x] Launcher builds and runs on Tier-1 OSes (per build matrix)
  Code: CMakePresets.json, source/dominium/launcher/CMakeLists.txt
  Tests: dominium_launcher_control_plane_tests, dominium_launcher_ui_smoke_tests, dominium_launcher_tui_smoke_tests
  Commits: d0146b8
  Verify: cmake --build --preset debug
          ctest --preset debug -R dominium_launcher_control_plane_tests

- [x] Launcher reads installed-state manifest; refuses on missing/corrupt state with recovery guidance
  Code: source/dominium/launcher/dom_launcher_cli.cpp
  Tests: dominium_launcher_state_smoke_tests
  Commits: d0146b8
  Verify: ctest --preset debug -R dominium_launcher_state_smoke_tests
          dominium-launcher --smoke-test --state <installed_state.dsustate>

- [x] Launcher smoke tests (headless where possible): parse state, enumerate components/packs, validate paths, basic UI boot
  Code: source/dominium/launcher/dom_launcher_cli.cpp, source/dominium/launcher/launcher_tui.cpp
  Tests: dominium_launcher_state_smoke_tests, dominium_launcher_ui_smoke_tests, dominium_launcher_tui_smoke_tests
  Commits: d0146b8
  Verify: ctest --preset debug -R dominium_launcher_state_smoke_tests
          ctest --preset debug -R dominium_launcher_ui_smoke_tests

## A3) Packaging readiness

- [x] Canonical artifact layout produced by packaging pipeline
  Code: scripts/packaging/pipeline.py, scripts/packaging/stage_dist.cmake
  Tests: dsu_packaging_validation_test
  Commits: a44e0e2
  Verify: ctest --preset debug -R dsu_packaging_validation_test

- [x] Windows artifacts installable (MSI/bootstrap)
  Code: scripts/packaging/windows, scripts/packaging/pipeline.py
  Tests: dsu_packaging_validation_test (dry-run), windows packaging scripts (manual)
  Commits: a44e0e2
  Verify: scripts/setup/build_packages.bat build\\debug 0.1.0

- [x] macOS artifacts installable (PKG/DMG)
  Code: scripts/packaging/macos, scripts/packaging/pipeline.py
  Tests: dsu_packaging_validation_test (dry-run), macos packaging scripts (manual)
  Commits: a44e0e2
  Verify: scripts/setup/build_packages.sh build/debug 0.1.0

- [x] Linux artifacts installable (tar/deb/rpm)
  Code: scripts/packaging/linux, scripts/packaging/pipeline.py
  Tests: dsu_packaging_validation_test (dry-run), linux packaging scripts (manual)
  Commits: a44e0e2
  Verify: scripts/setup/build_packages.sh build/debug 0.1.0

- [x] Steam depot mapping (mock ok)
  Code: scripts/packaging/pipeline.py
  Tests: dsu_packaging_validation_test
  Commits: a44e0e2
  Verify: python scripts/packaging/pipeline.py steam --artifact dist/artifacts/dominium-0.1.0 --out dist/steam --version 0.1.0 --appid 0 --depotid 0

## A4) Documentation readiness

- [x] Setup docs complete + consistent (arch, schema, txn/journal, installed state, audit log, CLI, adapters, packaging, recovery, security, reproducible builds)
  Code: docs/setup/SETUP_CORE_ARCHITECTURE.md, docs/setup/MANIFEST_SCHEMA.md, docs/setup/TRANSACTION_ENGINE.md,
        docs/setup/JOURNAL_FORMAT.md, docs/setup/INSTALLED_STATE_SCHEMA.md, docs/setup/AUDIT_LOG_FORMAT.md,
        docs/setup/CLI_REFERENCE.md, docs/setup/PLATFORM_ADAPTERS.md, docs/setup/PACKAGING_PIPELINES.md,
        docs/setup/TROUBLESHOOTING.md, docs/setup/SECURITY_MODEL.md, docs/setup/REPRODUCIBLE_BUILDS.md
  Tests: docs validation pass (manual review)
  Commits: b89f63a, a44e0e2
  Verify: docs/release/BUILD_AND_PACKAGE.md, docs/release/RECOVERY_PLAYBOOK.md (added during release)

- [x] Launcher docs complete + consistent (installed-state contract, error handling, smoke tests, recovery workflow)
  Code: docs/specs/launcher/ARCHITECTURE.md, docs/specs/launcher/RECOVERY_AND_SAFE_MODE.md, docs/specs/launcher/TESTING.md
  Tests: docs validation pass (manual review)
  Commits: b89f63a
  Verify: docs/launcher/CLI.md, docs/release/RECOVERY_PLAYBOOK.md (launcher section)
