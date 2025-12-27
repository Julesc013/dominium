cmake_minimum_required(VERSION 3.16)

add_executable(dsu_core_smoke_test
    dsu_core_smoke_test.c
)

target_include_directories(dsu_core_smoke_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_core_smoke_test
    PRIVATE dsu_core
)

set_target_properties(dsu_core_smoke_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_core_smoke_test COMMAND dsu_core_smoke_test)

add_executable(dsu_invocation_parity_test
    dsu_invocation_parity_test.c
)

target_include_directories(dsu_invocation_parity_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_invocation_parity_test
    PRIVATE dsu_core
)

set_target_properties(dsu_invocation_parity_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_invocation_parity_test COMMAND dsu_invocation_parity_test ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(dsu_manifest_test
    dsu_manifest_test.c
)

target_include_directories(dsu_manifest_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_manifest_test
    PRIVATE dsu_core
)

set_target_properties(dsu_manifest_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_manifest_test COMMAND dsu_manifest_test)

add_executable(dsu_resolve_test
    dsu_resolve_test.c
)

target_include_directories(dsu_resolve_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_resolve_test
    PRIVATE dsu_core
)

set_target_properties(dsu_resolve_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_resolve_test COMMAND dsu_resolve_test)

add_executable(dsu_txn_test
    dsu_txn_test.c
)

target_include_directories(dsu_txn_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_txn_test
    PRIVATE dsu_core
)

set_target_properties(dsu_txn_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_txn_test COMMAND dsu_txn_test)

add_executable(dsu_cli_test
    dsu_cli_test.c
)

target_include_directories(dsu_cli_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_cli_test
    PRIVATE dsu_core
)

add_dependencies(dsu_cli_test
    dominium-setup
)

set_target_properties(dsu_cli_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_cli_test COMMAND dsu_cli_test $<TARGET_FILE:dominium-setup> ${CMAKE_CURRENT_SOURCE_DIR})
set_tests_properties(dsu_cli_test PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

add_executable(dsu_setup_matrix_test
    dsu_setup_matrix_test.c
)

target_include_directories(dsu_setup_matrix_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_setup_matrix_test
    PRIVATE dsu_core
)

add_dependencies(dsu_setup_matrix_test
    dominium-setup
    dominium-setup-steam
)

if(TARGET dominium-setup-linux)
    add_dependencies(dsu_setup_matrix_test
        dominium-setup-linux
    )
endif()

set_target_properties(dsu_setup_matrix_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(dsu_platform_iface_test
    dsu_platform_iface_test.c
)

target_include_directories(dsu_platform_iface_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_platform_iface_test
    PRIVATE dsu_core
)

set_target_properties(dsu_platform_iface_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

get_filename_component(_dom_repo_root "${CMAKE_CURRENT_SOURCE_DIR}/../../../../" ABSOLUTE)
set(_dom_setup_cli $<TARGET_FILE:dominium-setup>)
set(_dom_steam_cli $<TARGET_FILE:dominium-setup-steam>)
if(TARGET dominium-setup-linux)
    set(_dom_linux_cli $<TARGET_FILE:dominium-setup-linux>)
else()
    set(_dom_linux_cli NONE)
endif()

add_test(NAME test_install_fresh_portable COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_install_fresh_portable)
add_test(NAME test_install_fresh_user_scope COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_install_fresh_user_scope)
add_test(NAME test_upgrade_in_place COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_upgrade_in_place)
add_test(NAME test_upgrade_side_by_side COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_upgrade_side_by_side)
add_test(NAME test_repair_restores_missing_files COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_repair_restores_missing_files)
add_test(NAME test_uninstall_preserves_user_data COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_uninstall_preserves_user_data)
add_test(NAME test_uninstall_removes_owned_files COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_uninstall_removes_owned_files)
add_test(NAME test_verify_detects_modified_file COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_verify_detects_modified_file)
add_test(NAME test_rollback_on_commit_failure COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_rollback_on_commit_failure)
add_test(NAME test_plan_determinism_repeat_run COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_plan_determinism_repeat_run)
add_test(NAME test_steam_lifecycle_simulation_mock COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_steam_lifecycle_simulation_mock)
add_test(NAME test_linux_pkg_lifecycle_simulation_mock COMMAND dsu_setup_matrix_test ${_dom_setup_cli} ${_dom_steam_cli} ${_dom_linux_cli} ${_dom_repo_root} test_linux_pkg_lifecycle_simulation_mock)

add_test(NAME test_manifest_unknown_tlv_skip COMMAND dsu_manifest_test)
add_test(NAME test_resolve_conflict_detection COMMAND dsu_resolve_test)
add_test(NAME test_platform_iface_idempotent_register_unregister COMMAND dsu_platform_iface_test)

if(WIN32)
    add_executable(dsu_adapter_smoke_test
        dsu_adapter_smoke_test.c
    )

    target_include_directories(dsu_adapter_smoke_test PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
    )

    target_link_libraries(dsu_adapter_smoke_test
        PRIVATE dsu_core
    )

    add_dependencies(dsu_adapter_smoke_test
        dominium-setup-win
        dominium-setup-steam
    )

    set_target_properties(dsu_adapter_smoke_test PROPERTIES
        C_STANDARD 90
        C_STANDARD_REQUIRED ON
        C_EXTENSIONS OFF
    )

    add_test(NAME dsu_adapter_smoke_test COMMAND dsu_adapter_smoke_test)
endif()

find_program(DOMINIUM_PYTHON NAMES python3 python)
if(DOMINIUM_PYTHON)
    get_filename_component(_dom_repo_root "${CMAKE_CURRENT_SOURCE_DIR}/../../../../" ABSOLUTE)
    set(_dom_packaging_test "${_dom_repo_root}/scripts/packaging/tests/packaging_validation_test.py")
    set(_dom_manifest_template "${_dom_repo_root}/assets/setup/manifests/product.template.json")

    add_test(
        NAME dsu_packaging_validation_test
        COMMAND
            ${DOMINIUM_PYTHON}
            ${_dom_packaging_test}
            --build-dir ${CMAKE_BINARY_DIR}
            --version 0.1.0
            --manifest-template ${_dom_manifest_template}
    )

    set_tests_properties(dsu_packaging_validation_test PROPERTIES
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        ENVIRONMENT "SOURCE_DATE_EPOCH=946684800"
    )

    set(_dom_msi_test "${_dom_repo_root}/scripts/packaging/tests/msi_validation_test.py")

    add_test(
        NAME dsu_msi_validation_test
        COMMAND
            ${DOMINIUM_PYTHON}
            ${_dom_msi_test}
            --build-dir ${CMAKE_BINARY_DIR}
            --version ${DOM_PROJECT_SEMVER}
            --config $<CONFIG>
    )

    set_tests_properties(dsu_msi_validation_test PROPERTIES
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        ENVIRONMENT "SOURCE_DATE_EPOCH=946684800"
    )

endif()
