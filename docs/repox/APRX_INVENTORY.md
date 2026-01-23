# APRX Inventory (RepoX + TestX)

Status: discovery
Scope: RepoX/TestX enforcement surfaces and integration points for APR* work.

## RepoX canon surfaces (documents)
- docs/arch/REPO_OWNERSHIP_AND_PROJECTIONS.md - repo ownership and /ide projection rules.
- docs/arch/ARCH_REPO_LAYOUT.md and docs/arch/DIRECTORY_CONTEXT.md - canonical layout and ownership boundaries.
- docs/arch/ARCH_ENFORCEMENT.md and docs/arch/ARCH_BUILD_ENFORCEMENT.md - dependency law, include boundaries, CMake restrictions.
- docs/arch/IDE_AND_TOOLCHAIN_POLICY.md, docs/arch/PROJECTION_LIFECYCLE.md,
  docs/arch/GENERATED_CODE_POLICY.md, docs/arch/LEGACY_SUPPORT_STRATEGY.md,
  docs/arch/FUTURE_COMPATIBILITY_AND_ARCH.md - projection/toolchain governance.
- docs/ci/CI_ENFORCEMENT_MATRIX.md - enforcement IDs (ARCH, REND, DET, PERF, REPOX, HYGIENE, etc).
- docs/ci/BUILD_MATRIX.md - canonical build presets (CMakePresets.json).
- docs/build/TOOLCHAIN_MODEL.md, docs/build/SKU_MODEL.md, docs/build/OS_FLOOR_POLICY.md - toolchain/SKU metadata.
- docs/policies/IDE_CONTRIBUTION_RULES.md, docs/policies/DOCUMENTATION_STANDARDS.md,
  docs/policies/DETERMINISM_ENFORCEMENT.md - governance and policy anchors.

## RepoX enforcement mechanisms (current)
- Configure-time CMake checks: scripts/verify_cmake_no_global_includes.py (BUILD-GLOBAL-001),
  dom_assert_no_link(...) (ARCH-DEP-*), BaselineHeaderCheck.cmake (public headers).
- Custom targets: check_arch, check_docs_sanity, check_abi_boundaries, check_ui_shell_purity,
  check_ide_quarantine, doc_ratio_check, check_hygiene, check_comment_density,
  check_todo_blockers, check_magic_numbers, check_forbidden_enums, check_switch_on_taxonomy, check_all.
- RepoX scripts: scripts/verify_tree_sanity.bat, scripts/verify_ide_quarantine.py,
  scripts/verify_projection_regen_clean.py, scripts/verify_ui_shell_purity.py,
  scripts/verify_abi_boundaries.py, scripts/verify_docs_sanity.py.
- Arch/determinism scans: tools/ci/arch_checks.py (ARCH-*, DET-*, EPIS-*, PERF-*, SCALE-*),
  scripts/ci/check_execution_contracts.py (EXEC-AUDIT0-*), scripts/ci/* hygiene checks.
- CI entrypoints (.github/workflows/ci.yml):
  - repo-sanity: verify_ide_quarantine, verify_tree_sanity, verify_ui_shell_purity, verify_abi_boundaries.
  - projection-sanity: verify_projection_regen_clean for IDE presets.
  - docs-sanity: verify_docs_sanity.
  - build-test/build-test-canary: check_launcher_core_invariants.py, check_layers.py, cmake build + ctest,
    launcher_cli_smoke_matrix.py, support bundle determinism.
  - reproducible-build and portable-packages gates.
- Build number policy: .dominium_build_number read in root CMake; dom_update_build_number target (ALL)
  runs setup/packages/scripts/update_build_number.cmake to increment on build. No test-gated bump hook present.

## TestX canon surfaces (documents)
- docs/app/TESTX_INVENTORY.md and docs/app/TESTX_COMPLIANCE.md (app CLI contract + smoke checks).
- docs/app/CLI_CONTRACTS.md (required CLI flags, build-info keys, explicit renderer failure).
- docs/ci/DETERMINISM_TEST_MATRIX.md and docs/ci/REGRESSION_SUITES.md (determinism/perf suites).
- docs/ci/EXECUTION_ENFORCEMENT_CHECKS.md (execution contract checks).
- docs/specs/SPEC_SMOKE_TESTS.md (GUI smoke contract) and docs/specs/TOOL_TEST.md (tools test runner).

## TestX enforcement mechanisms (current)
- tests/app/app_cli_contracts.py (help/version/build-info/smoke; deterministic vs interactive rules;
  renderer explicit failure; UI mode expectations).
- tests/app/app_observability_tests.py (readonly output and mismatch refusal paths).
- tests/app/app_buildmeta_tests.py (artifact metadata JSON fields).
- tests/app build-time checks: build_include_sanity, build_abi_boundaries, build_arch_checks.
- Root CMake test: phase6_audit (tools/ci/phase6_audit_checks.py).
- Engine/game/server/tools tests registered via add_test in their CMakeLists.
- CI runs full ctest; additional regex runs in setup/packages/scripts/release and build-test jobs.
- No ctest labels found in CMake; test selection is via full ctest or -R regex in scripts/CI.

## Integration points for APR* work
- Products/backends: follow canonical target patterns in docs/arch/ARCH_BUILD_ENFORCEMENT.md and
  docs/arch/ARCH_REPO_LAYOUT.md; keep add_subdirectory structure.
- Tests: register via add_test in existing CMakeLists or tests/app; avoid new frameworks;
  align with CI's ctest and regex selections.
- RepoX gates: update scripts/verify_ui_shell_purity.py roots or verify_abi_boundaries.py public roots
  when adding new UI shells or public headers; keep docs/ links valid for verify_docs_sanity.py.
- CI/presets: integrate new products/backends into CMakePresets.json and docs/ci/BUILD_MATRIX.md
  when they become canonical.
