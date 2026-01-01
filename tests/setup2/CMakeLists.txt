cmake_minimum_required(VERSION 3.16)

add_executable(setup2_kernel_tests
    setup2_kernel_tests.cpp
)
target_include_directories(setup2_kernel_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_kernel_tests PRIVATE
    dsk_kernel
    dss_services
)
set_target_properties(setup2_kernel_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_tlv_roundtrip_known_fields
    COMMAND setup2_kernel_tests tlv_roundtrip_known_fields
)
add_test(NAME setup2_tlv_skip_unknown
    COMMAND setup2_kernel_tests tlv_skip_unknown
)
add_test(NAME setup2_manifest_validate_missing_required
    COMMAND setup2_kernel_tests manifest_validate_missing_required
)
add_test(NAME setup2_request_validate_missing_required
    COMMAND setup2_kernel_tests request_validate_missing_required
)
add_test(NAME setup2_kernel_emits_audit_on_failure
    COMMAND setup2_kernel_tests kernel_emits_audit_on_failure
)
add_test(NAME setup2_splat_selection_deterministic
    COMMAND setup2_kernel_tests splat_selection_deterministic
)
add_test(NAME setup2_state_auto_migration_missing_version
    COMMAND setup2_kernel_tests state_auto_migration_missing_version
)
add_test(NAME setup2_state_skip_unknown_fields
    COMMAND setup2_kernel_tests state_skip_unknown_fields
)

add_executable(setup2_splat_tests
    test_splat_selection.cpp
)
target_include_directories(setup2_splat_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_splat_tests PRIVATE
    dsk_kernel
    dss_services
)
set_target_properties(setup2_splat_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_splat_registry_sorted
    COMMAND setup2_splat_tests splat_registry_sorted
)
add_test(NAME setup2_splat_select_requested_id_success
    COMMAND setup2_splat_tests splat_select_requested_id_success
)
add_test(NAME setup2_splat_select_requested_id_not_found
    COMMAND setup2_splat_tests splat_select_requested_id_not_found
)
add_test(NAME setup2_splat_select_requested_id_removed
    COMMAND setup2_splat_tests splat_select_requested_id_removed
)
add_test(NAME setup2_splat_select_filters_by_platform
    COMMAND setup2_splat_tests splat_select_filters_by_platform
)
add_test(NAME setup2_splat_select_filters_by_scope
    COMMAND setup2_splat_tests splat_select_filters_by_scope
)
add_test(NAME setup2_splat_select_filters_by_ui_mode
    COMMAND setup2_splat_tests splat_select_filters_by_ui_mode
)
add_test(NAME setup2_splat_select_no_compatible_emits_rejections_and_audit
    COMMAND setup2_splat_tests splat_select_no_compatible_emits_rejections_and_audit
)
add_test(NAME setup2_splat_select_deterministic_choice_first_compatible
    COMMAND setup2_splat_tests splat_select_deterministic_choice_first_compatible
)
add_test(NAME setup2_splat_select_deprecated_emits_warning
    COMMAND setup2_splat_tests splat_select_deprecated_emits_warning
)

add_executable(setup2_services_fs_tests
    test_services_fs_sandbox.cpp
)
target_include_directories(setup2_services_fs_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_services_fs_tests PRIVATE
    dss_services
)
target_compile_definitions(setup2_services_fs_tests PRIVATE
    SETUP2_TESTS_SANDBOX_ROOT="${CMAKE_CURRENT_BINARY_DIR}/fs_sandbox"
)
set_target_properties(setup2_services_fs_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_services_fs_rejects_escape
    COMMAND setup2_services_fs_tests services_fs_rejects_escape ${CMAKE_CURRENT_BINARY_DIR}/fs_sandbox_escape
)
add_test(NAME setup2_services_fs_atomic_write
    COMMAND setup2_services_fs_tests services_fs_atomic_write ${CMAKE_CURRENT_BINARY_DIR}/fs_sandbox_atomic
)
add_test(NAME setup2_services_fs_canonicalize
    COMMAND setup2_services_fs_tests services_fs_canonicalize ${CMAKE_CURRENT_BINARY_DIR}/fs_sandbox_canon
)

add_executable(setup2_services_platform_fake_tests
    test_services_platform_fake.cpp
)
target_include_directories(setup2_services_platform_fake_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_services_platform_fake_tests PRIVATE
    dss_services
)
set_target_properties(setup2_services_platform_fake_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_services_platform_fake
    COMMAND setup2_services_platform_fake_tests services_platform_fake
)

add_executable(setup2_kernel_uses_services_platform_tests
    test_kernel_uses_services_platform.cpp
)
target_include_directories(setup2_kernel_uses_services_platform_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_kernel_uses_services_platform_tests PRIVATE
    dsk_kernel
    dss_services
)
set_target_properties(setup2_kernel_uses_services_platform_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_kernel_uses_services_platform
    COMMAND setup2_kernel_uses_services_platform_tests kernel_uses_services_platform
)

add_executable(setup2_plan_tests
    test_plan.cpp
)
target_include_directories(setup2_plan_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup2_plan_tests PRIVATE
    dsk_kernel
)
target_compile_definitions(setup2_plan_tests PRIVATE
    SETUP2_TESTS_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
set_target_properties(setup2_plan_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_resolve_default_components
    COMMAND setup2_plan_tests resolve_default_components
)
add_test(NAME setup2_resolve_explicit_components
    COMMAND setup2_plan_tests resolve_explicit_components
)
add_test(NAME setup2_resolve_dependency_closure
    COMMAND setup2_plan_tests resolve_dependency_closure
)
add_test(NAME setup2_resolve_conflict_refusal
    COMMAND setup2_plan_tests resolve_conflict_refusal
)
add_test(NAME setup2_resolve_platform_incompat_refusal
    COMMAND setup2_plan_tests resolve_platform_incompat_refusal
)
add_test(NAME setup2_plan_byte_identical_repeat
    COMMAND setup2_plan_tests plan_byte_identical_repeat
)
add_test(NAME setup2_plan_digest_stable
    COMMAND setup2_plan_tests plan_digest_stable
)
add_test(NAME setup2_plan_validate_rejects_corrupt_header
    COMMAND setup2_plan_tests plan_validate_rejects_corrupt_header
)
add_test(NAME setup2_plan_lists_canonically_sorted
    COMMAND setup2_plan_tests plan_lists_canonically_sorted
)
add_test(NAME setup2_plan_golden_default
    COMMAND setup2_plan_tests plan_golden_default
)
add_test(NAME setup2_plan_golden_custom
    COMMAND setup2_plan_tests plan_golden_custom
)

add_executable(setup2_import_tests
    test_import_legacy_state.cpp
)
target_include_directories(setup2_import_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup2_import_tests PRIVATE
    dsk_kernel
)
target_compile_definitions(setup2_import_tests PRIVATE
    SETUP2_TESTS_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
)
set_target_properties(setup2_import_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_import_legacy_state
    COMMAND setup2_import_tests
)

add_executable(setup2_apply_tests
    test_apply.cpp
)
target_include_directories(setup2_apply_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_apply_tests PRIVATE
    dsk_kernel
    dss_services
)
target_compile_definitions(setup2_apply_tests PRIVATE
    SETUP2_TESTS_SANDBOX_ROOT="${CMAKE_CURRENT_BINARY_DIR}/apply_sandbox"
)
set_target_properties(setup2_apply_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_apply_fresh_install_succeeds
    COMMAND setup2_apply_tests apply_fresh_install_succeeds
)
add_test(NAME setup2_fail_mid_commit_then_rollback_restores_pristine
    COMMAND setup2_apply_tests fail_mid_commit_then_rollback_restores_pristine
)
add_test(NAME setup2_fail_mid_commit_then_resume_completes
    COMMAND setup2_apply_tests fail_mid_commit_then_resume_completes
)
add_test(NAME setup2_crash_during_stage_then_resume
    COMMAND setup2_apply_tests crash_during_stage_then_resume
)
add_test(NAME setup2_no_in_place_mutation
    COMMAND setup2_apply_tests no_in_place_mutation
)
add_test(NAME setup2_deterministic_journals
    COMMAND setup2_apply_tests deterministic_journals
)

add_executable(setup2_cli_golden_tests
    test_cli_golden.cpp
)
set_target_properties(setup2_cli_golden_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup2_cli_golden_tests
    dominium-setup2
)
add_test(NAME setup2_cli_golden
    COMMAND setup2_cli_golden_tests
        $<TARGET_FILE:dominium-setup2>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_SOURCE_DIR}/tests/setup2/golden
        ${CMAKE_CURRENT_BINARY_DIR}/cli_golden
)
set_tests_properties(setup2_cli_golden PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

add_executable(setup2_gold_master_tests
    gold_master/setup2_gold_master_tests.cpp
)
target_include_directories(setup2_gold_master_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup2_gold_master_tests PRIVATE
    dsk_kernel
    dss_services
)
set_target_properties(setup2_gold_master_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup2_gold_master_tests
    dominium-setup2
)
add_test(NAME setup2_gold_master_roundtrip
    COMMAND setup2_gold_master_tests roundtrip
        $<TARGET_FILE:dominium-setup2>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_SOURCE_DIR}/artifacts/setup2/gold_master
        ${CMAKE_CURRENT_BINARY_DIR}/gold_master
)
add_test(NAME setup2_gold_master_digests_unchanged
    COMMAND setup2_gold_master_tests digests
        $<TARGET_FILE:dominium-setup2>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_SOURCE_DIR}/artifacts/setup2/gold_master
        ${CMAKE_CURRENT_BINARY_DIR}/gold_master
)

add_executable(setup2_adapter_steam_tests
    test_adapter_steam.cpp
)
target_include_directories(setup2_adapter_steam_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup2_adapter_steam_tests PRIVATE
    dsk_kernel
)
set_target_properties(setup2_adapter_steam_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup2_adapter_steam_tests
    dominium-setup2
    dominium-setup2-steam
)
add_test(NAME setup2_adapter_steam
    COMMAND setup2_adapter_steam_tests
        $<TARGET_FILE:dominium-setup2>
        $<TARGET_FILE:dominium-setup2-steam>
        ${CMAKE_CURRENT_BINARY_DIR}/adapter_steam
)

add_executable(setup2_adapter_macos_pkg_tests
    test_adapter_macos_pkg.cpp
)
set_target_properties(setup2_adapter_macos_pkg_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_adapter_macos_pkg
    COMMAND setup2_adapter_macos_pkg_tests
        ${CMAKE_SOURCE_DIR}
)

add_executable(setup2_adapter_linux_wrappers_tests
    test_adapter_linux_wrappers.cpp
)
set_target_properties(setup2_adapter_linux_wrappers_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_adapter_linux_wrappers
    COMMAND setup2_adapter_linux_wrappers_tests
        ${CMAKE_SOURCE_DIR}
)

add_executable(setup2_adapter_wrapper_tests
    test_adapter_wrapper_scripts.cpp
)
set_target_properties(setup2_adapter_wrapper_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_adapter_wrapper_scripts
    COMMAND setup2_adapter_wrapper_tests
        ${CMAKE_SOURCE_DIR}
)

add_executable(setup2_parity_tests
    parity/setup2_parity_tests.cpp
)
target_compile_definitions(setup2_parity_tests PRIVATE
    SETUP2_SOURCE_DIR="${CMAKE_SOURCE_DIR}"
)
set_target_properties(setup2_parity_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_parity_kernel_invariants_match_launcher
    COMMAND setup2_parity_tests kernel_invariants_match_launcher
)
add_test(NAME setup2_parity_capability_registry_semantics_match
    COMMAND setup2_parity_tests capability_registry_semantics_match
)
add_test(NAME setup2_parity_job_journal_semantics_match
    COMMAND setup2_parity_tests job_journal_semantics_match
)

add_executable(setup2_parity_lock_tests
    parity_lock/setup2_parity_lock_tests.cpp
)
target_include_directories(setup2_parity_lock_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup2_parity_lock_tests PRIVATE
    dsk_kernel
)
set_target_properties(setup2_parity_lock_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup2_parity_lock_tests
    dominium-setup2
    dominium-setup2-tui
)
if(TARGET dominium-setup2-steam)
    add_dependencies(setup2_parity_lock_tests dominium-setup2-steam)
    set(SETUP2_PARITY_STEAM_BIN $<TARGET_FILE:dominium-setup2-steam>)
else()
    set(SETUP2_PARITY_STEAM_BIN "none")
endif()
if(WIN32 AND TARGET dominium-setup2-win-exe)
    add_dependencies(setup2_parity_lock_tests dominium-setup2-win-exe)
    set(SETUP2_PARITY_WIN_EXE_BIN $<TARGET_FILE:dominium-setup2-win-exe>)
else()
    set(SETUP2_PARITY_WIN_EXE_BIN "none")
endif()

add_test(NAME setup2_parity_lock_request_equivalence_across_adapters
    COMMAND setup2_parity_lock_tests request_equivalence_across_adapters
        $<TARGET_FILE:dominium-setup2>
        $<TARGET_FILE:dominium-setup2-tui>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_CURRENT_BINARY_DIR}/parity_lock
        ${CMAKE_SOURCE_DIR}
        ${SETUP2_PARITY_STEAM_BIN}
        ${SETUP2_PARITY_WIN_EXE_BIN}
)
add_test(NAME setup2_parity_lock_plan_digest_equivalence_across_adapters
    COMMAND setup2_parity_lock_tests plan_digest_equivalence_across_adapters
        $<TARGET_FILE:dominium-setup2>
        $<TARGET_FILE:dominium-setup2-tui>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_CURRENT_BINARY_DIR}/parity_lock
        ${CMAKE_SOURCE_DIR}
        ${SETUP2_PARITY_STEAM_BIN}
        ${SETUP2_PARITY_WIN_EXE_BIN}
)
add_test(NAME setup2_parity_lock_refusal_code_equivalence
    COMMAND setup2_parity_lock_tests refusal_code_equivalence
        $<TARGET_FILE:dominium-setup2>
        $<TARGET_FILE:dominium-setup2-tui>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_CURRENT_BINARY_DIR}/parity_lock
        ${CMAKE_SOURCE_DIR}
        ${SETUP2_PARITY_STEAM_BIN}
        ${SETUP2_PARITY_WIN_EXE_BIN}
)

if(WIN32)
    add_executable(setup2_adapter_windows_tests
        test_adapter_windows_exe.cpp
    )
    target_include_directories(setup2_adapter_windows_tests PRIVATE
        ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    )
    target_link_libraries(setup2_adapter_windows_tests PRIVATE
        dsk_kernel
    )
    set_target_properties(setup2_adapter_windows_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_dependencies(setup2_adapter_windows_tests
        dominium-setup2
        dominium-setup2-win-exe
    )
    add_test(NAME setup2_adapter_windows_exe
        COMMAND setup2_adapter_windows_tests
            $<TARGET_FILE:dominium-setup2>
            $<TARGET_FILE:dominium-setup2-win-exe>
            ${CMAKE_CURRENT_BINARY_DIR}/adapter_windows
    )
endif()

add_executable(setup2_conformance_runner
    conformance/setup2_conformance_runner.cpp
)
target_include_directories(setup2_conformance_runner PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/src/plan
)
target_link_libraries(setup2_conformance_runner PRIVATE
    dsk_kernel
    dss_services
)
set_target_properties(setup2_conformance_runner PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_conformance
    COMMAND setup2_conformance_runner
        --sandbox-root ${CMAKE_CURRENT_BINARY_DIR}/conformance
        --fixtures-root ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        --deterministic 1
        --out-json ${CMAKE_CURRENT_BINARY_DIR}/conformance/conformance_summary.json
)

add_test(NAME setup2_conformance_golden
    COMMAND ${CMAKE_COMMAND} -E compare_files
        ${CMAKE_CURRENT_BINARY_DIR}/conformance/conformance_summary.json
        ${CMAKE_SOURCE_DIR}/tests/setup2/golden/conformance_summary.json
)
set_tests_properties(setup2_conformance_golden PROPERTIES
    DEPENDS setup2_conformance
)

add_executable(setup2_conformance_repeat_tests
    conformance/setup2_conformance_repeat_tests.cpp
)
set_target_properties(setup2_conformance_repeat_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup2_conformance_repeat_tests
    setup2_conformance_runner
)
add_test(NAME setup2_conformance_repeat
    COMMAND setup2_conformance_repeat_tests
        $<TARGET_FILE:setup2_conformance_runner>
        ${CMAKE_SOURCE_DIR}/tests/setup2/fixtures
        ${CMAKE_CURRENT_BINARY_DIR}/conformance_repeat
)
