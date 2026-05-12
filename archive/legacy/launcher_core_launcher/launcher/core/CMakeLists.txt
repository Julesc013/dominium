cmake_minimum_required(VERSION 3.16)

add_library(dominium_launcher_core STATIC
    launcher_context.cpp
    launcher_core.cpp
    log/launcher_log.cpp
    safety/launcher_safety.cpp
    tlv/launcher_tlv_migrations.cpp
    tlv/launcher_tlv_schema_registry.cpp
    selection/launcher_selection_summary.cpp
    run/launcher_run_summary.cpp
    launch/launcher_prelaunch.cpp
    launch/launcher_launch_attempt.cpp
    launch/launcher_handshake.cpp
    launch/launcher_exit_status.cpp
    tool/launcher_tools_registry.cpp
    profile/launcher_profile.cpp
    installed_state/launcher_installed_state.cpp
    instance/launcher_instance.cpp
    instance/launcher_instance_config.cpp
    instance/launcher_instance_payload_refs.cpp
    instance/launcher_instance_known_good.cpp
    instance/launcher_instance_launch_history.cpp
    instance/launcher_instance_tx.cpp
    instance/launcher_instance_artifact_ops.cpp
    instance/launcher_instance_ops.cpp
    pack/launcher_pack_manifest.cpp
    pack/launcher_pack_resolver.cpp
    pack/launcher_pack_ops.cpp
    artifact/launcher_artifact.cpp
    artifact/launcher_sha256.cpp
    artifact/launcher_artifact_store.cpp
    task/launcher_task.cpp
    job/launcher_job.cpp
    audit/launcher_audit.cpp
)

target_include_directories(dominium_launcher_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/include/dominium/_internal/dom_priv
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(dominium_launcher_core
    PRIVATE
        core_tlv
        core_audit
        core_installed_state
        core_util
        core_err
        core_log
        core_caps
        core_solver
        core_job
        core_tlv_schema
)

set_target_properties(dominium_launcher_core PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(launcher_kernel ALIAS dominium_launcher_core)

add_library(launcher_services_api INTERFACE)
target_include_directories(launcher_services_api INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(dominium_launcher_core_smoke
    tests/launcher_core_smoke.cpp
)

target_link_libraries(dominium_launcher_core_smoke PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_core_smoke PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_core_smoke PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_core_smoke PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_core_smoke PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_core_smoke COMMAND dominium_launcher_core_smoke)

add_executable(launcher_kernel_smoke
    tests/launcher_core_smoke.cpp
)

target_link_libraries(launcher_kernel_smoke PRIVATE
    launcher_kernel
    launcher_services_impl_null
)

target_include_directories(launcher_kernel_smoke PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(launcher_kernel_smoke PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(launcher_kernel_smoke PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(launcher_kernel_smoke PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME launcher_kernel_smoke COMMAND launcher_kernel_smoke)


add_executable(dominium_launcher_instance_system_tests
    tests/launcher_instance_system_tests.cpp
)

target_link_libraries(dominium_launcher_instance_system_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_instance_system_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_instance_system_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_instance_system_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_instance_system_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_instance_system_tests COMMAND dominium_launcher_instance_system_tests)

add_executable(dominium_launcher_artifact_store_tx_tests
    tests/launcher_artifact_store_tx_tests.cpp
)

target_link_libraries(dominium_launcher_artifact_store_tx_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_artifact_store_tx_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_artifact_store_tx_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_artifact_store_tx_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_artifact_store_tx_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_artifact_store_tx_tests COMMAND dominium_launcher_artifact_store_tx_tests)

add_executable(dominium_launcher_pack_ecosystem_tests
    tests/launcher_pack_ecosystem_tests.cpp
)

target_link_libraries(dominium_launcher_pack_ecosystem_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_pack_ecosystem_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_pack_ecosystem_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_pack_ecosystem_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_pack_ecosystem_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_pack_ecosystem_tests COMMAND dominium_launcher_pack_ecosystem_tests)

add_executable(dominium_launcher_prelaunch_recovery_tests
    tests/launcher_prelaunch_recovery_tests.cpp
)

target_link_libraries(dominium_launcher_prelaunch_recovery_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_prelaunch_recovery_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_prelaunch_recovery_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_prelaunch_recovery_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_prelaunch_recovery_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_prelaunch_recovery_tests COMMAND dominium_launcher_prelaunch_recovery_tests)

add_executable(dominium_launcher_tlv_migrations_tests
    tests/launcher_tlv_migrations_tests.cpp
)

target_link_libraries(dominium_launcher_tlv_migrations_tests PRIVATE
    dominium_launcher_core
)

target_include_directories(dominium_launcher_tlv_migrations_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_tlv_migrations_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_tlv_migrations_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_tlv_migrations_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_tlv_migrations_tests COMMAND dominium_launcher_tlv_migrations_tests)

add_executable(dominium_launcher_handshake_tests
    tests/launcher_handshake_tests.cpp
)

target_link_libraries(dominium_launcher_handshake_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_handshake_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_handshake_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_handshake_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_handshake_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_handshake_tests COMMAND dominium_launcher_handshake_tests)

add_executable(dominium_launcher_tools_registry_tests
    tests/launcher_tools_registry_tests.cpp
)

target_link_libraries(dominium_launcher_tools_registry_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
)

target_include_directories(dominium_launcher_tools_registry_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dominium_launcher_tools_registry_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_tools_registry_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_tools_registry_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_launcher_tools_registry_tests COMMAND dominium_launcher_tools_registry_tests)
