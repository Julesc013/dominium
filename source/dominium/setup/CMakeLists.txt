cmake_minimum_required(VERSION 3.16)

if(NOT DEFINED SETUP2_DEFAULT)
    set(SETUP2_DEFAULT ON)
endif()
if(NOT DEFINED SETUP_LEGACY_BUILD)
    set(SETUP_LEGACY_BUILD ON)
endif()
if(NOT DEFINED SETUP_LEGACY_DEPRECATED_WARN)
    set(SETUP_LEGACY_DEPRECATED_WARN ON)
endif()

option(DOMINIUM_BUILD_SETUP2 "Build setup2 kernel/services/frontends" ${SETUP2_DEFAULT})
option(DOMINIUM_BUILD_SETUP_LEGACY "Build legacy setup stack" ${SETUP_LEGACY_BUILD})

if(DOMINIUM_BUILD_SETUP_LEGACY AND SETUP_LEGACY_DEPRECATED_WARN)
    message(WARNING "Legacy setup build enabled; use dominium-setup-legacy explicitly (disable with -DSETUP_LEGACY_BUILD=OFF).")
endif()

if(DOMINIUM_BUILD_SETUP_LEGACY)
    add_subdirectory(core)
endif()
if(DOMINIUM_BUILD_SETUP2 OR DOMINIUM_BUILD_SETUP_LEGACY)
    add_subdirectory(services)
endif()
if(DOMINIUM_BUILD_SETUP_LEGACY)
    add_subdirectory(adapters)
endif()

if(DOMINIUM_BUILD_SETUP2)

# Setup2 layering:
#   Layer 0: dsk_kernel (pure orchestration, no OS headers or side effects)
#   Layer 1: dss_services (runtime side effects behind service contracts)
#   Layer 2: dominium-setup2 (frontend, links only kernel + services)

add_library(dsk_kernel STATIC
    kernel/src/api/dsk_api.cpp
    kernel/src/tlv/dsk_tlv_schema_registry.cpp
    kernel/src/tlv/dsk_tlv_bridge.cpp
    kernel/src/digest/dsk_digest.cpp
    kernel/src/errors/dsk_error.cpp
    kernel/src/audit/dsk_audit.cpp
    kernel/src/import/dsk_import_legacy.cpp
    kernel/src/splat/dsk_splat_caps.cpp
    kernel/src/splat/dsk_splat_registry.cpp
    kernel/src/splat/dsk_splat_select.cpp
    kernel/src/contracts/dsk_contract_manifest.cpp
    kernel/src/contracts/dsk_contract_request.cpp
    kernel/src/contracts/dsk_contract_state.cpp
    kernel/src/contracts/dsk_contract_audit.cpp
    kernel/src/plan/dsk_resolve.cpp
    kernel/src/plan/dsk_plan_build.cpp
    kernel/src/plan/dsk_plan_validate.cpp
    kernel/src/plan/dsk_plan_digest.cpp
    kernel/src/plan/dsk_plan_dump_json.cpp
    kernel/src/jobs/dsk_jobs_build.cpp
    kernel/src/jobs/dsk_jobs_checkpoint.cpp
    kernel/src/jobs/dsk_jobs_common.cpp
    kernel/src/jobs/dsk_jobs_execute.cpp
    kernel/src/jobs/dsk_jobs_resume.cpp
    kernel/src/jobs/dsk_jobs_rollback.cpp
)

target_include_directories(dsk_kernel PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/kernel/include
)

target_include_directories(dsk_kernel PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
)

target_include_directories(dsk_kernel PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/services/include
    ${CMAKE_CURRENT_SOURCE_DIR}/kernel/src/plan
)

target_compile_definitions(dsk_kernel PRIVATE
    DSK_FORBID_OS_HEADERS=1
)

set_target_properties(dsk_kernel PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

target_link_libraries(dss_services
    PRIVATE dsk_kernel
)

target_link_libraries(dsk_kernel
    PUBLIC
        core_tlv
        core_audit
        core_installed_state
        core_err
        core_log
        core_caps
        core_solver
        core_tlv_schema
)

set(SETUP2_CLI_SOURCES
    frontends/cli/dominium_setup2_main.cpp
)

add_executable(dominium-setup2
    ${SETUP2_CLI_SOURCES}
)

add_executable(dominium-setup
    ${SETUP2_CLI_SOURCES}
)

add_executable(dominium-setup2-tui
    frontends/tui/dominium_setup2_tui_main.cpp
)

add_library(setup2_frontend_common STATIC
    frontends/common/args_parse.cpp
    frontends/common/json_writer.cpp
    frontends/common/request_builder.cpp
)

target_include_directories(setup2_frontend_common PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/kernel/include
    ${CMAKE_CURRENT_SOURCE_DIR}/services/include
    ${CMAKE_CURRENT_SOURCE_DIR}/frontends/common
    ${PROJECT_SOURCE_DIR}/include
)

set_target_properties(setup2_frontend_common PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

foreach(setup2_cli_target IN ITEMS dominium-setup2 dominium-setup)
    target_include_directories(${setup2_cli_target} PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/kernel/include
        ${CMAKE_CURRENT_SOURCE_DIR}/services/include
        ${CMAKE_CURRENT_SOURCE_DIR}/frontends/common
        ${PROJECT_SOURCE_DIR}/include
    )
    target_link_libraries(${setup2_cli_target}
        PRIVATE
            dsk_kernel
            dss_services
            setup2_frontend_common
    )
    set_target_properties(${setup2_cli_target} PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
endforeach()

target_include_directories(dominium-setup2-tui PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/kernel/include
    ${CMAKE_CURRENT_SOURCE_DIR}/services/include
    ${CMAKE_CURRENT_SOURCE_DIR}/frontends/common
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dominium-setup2-tui
    PRIVATE
        dsk_kernel
        dss_services
        setup2_frontend_common
)

set_target_properties(dominium-setup2-tui PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dist_set_role(dominium-setup tools)
dist_set_role(dominium-setup2 tools)

dominium_bundle_runtime(dominium-setup)
dominium_bundle_runtime(dominium-setup2)

add_subdirectory(frontends/adapters)

if(WIN32)
    get_filename_component(DSK_COMPILER_DIR "${CMAKE_CXX_COMPILER}" DIRECTORY)
    set(DSK_WINPTHREAD_DLL "${DSK_COMPILER_DIR}/libwinpthread-1.dll")
    if(EXISTS "${DSK_WINPTHREAD_DLL}")
        add_custom_command(TARGET dominium-setup2 POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${DSK_WINPTHREAD_DLL}"
                $<TARGET_FILE_DIR:dominium-setup2>
        )
        add_custom_command(TARGET dominium-setup POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${DSK_WINPTHREAD_DLL}"
                $<TARGET_FILE_DIR:dominium-setup>
        )
        add_custom_command(TARGET dominium-setup2-tui POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${DSK_WINPTHREAD_DLL}"
                $<TARGET_FILE_DIR:dominium-setup2-tui>
        )
    endif()
endif()

endif() # DOMINIUM_BUILD_SETUP2

if(DOMINIUM_BUILD_SETUP_LEGACY)
add_library(setup_services_api INTERFACE)
target_include_directories(setup_services_api INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/core/include
    ${PROJECT_SOURCE_DIR}/include
)

add_library(setup_frontend_cli INTERFACE)
target_link_libraries(setup_frontend_cli INTERFACE
    setup_services_api
)

add_library(setup_frontend_gui STATIC
    cli/setup_ui_gui.cpp
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/gen/ui_setup_ui_actions_gen.cpp
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/user/ui_setup_ui_actions_user.cpp
)

target_include_directories(setup_frontend_gui PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/core/include
    ${PROJECT_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/gen
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/user
)

target_link_libraries(setup_frontend_gui
    PRIVATE
        setup_kernel
        setup_services_api
        dui_api
)

set_target_properties(setup_frontend_gui PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_executable(dominium-setup-legacy
    cli/dominium_setup_main.c
)

target_include_directories(dominium-setup-legacy PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/core/include
    ${PROJECT_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/gen
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/user
)

target_link_libraries(dominium-setup-legacy
    PRIVATE
        setup_kernel
        setup_services_impl_platform
        setup_frontend_gui
        setup_frontend_cli
        domino_core
)

set_target_properties(dominium-setup-legacy PROPERTIES
    OUTPUT_NAME "dominium-setup-legacy"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dist_set_role(dominium-setup-legacy tools)

dominium_bundle_runtime(dominium-setup-legacy)

set(SETUP_UI_ROOT ${CMAKE_SOURCE_DIR}/tools/setup/ui)
set(SETUP_UI_DOC ${SETUP_UI_ROOT}/doc/setup_ui_doc.tlv)
set(SETUP_UI_DOC_JSON ${SETUP_UI_ROOT}/doc/setup_ui_doc.json)
set(SETUP_UI_SCRIPT ${SETUP_UI_ROOT}/scripts/minecraft_setup_v1.ops.json)
set(SETUP_UI_GEN_DIR ${SETUP_UI_ROOT}/gen)
set(SETUP_UI_USER_DIR ${SETUP_UI_ROOT}/user)
set(SETUP_UI_REGISTRY ${SETUP_UI_ROOT}/registry/setup_actions_registry.json)
set(SETUP_UI_REPORTS_DIR ${SETUP_UI_ROOT}/reports)
set(SETUP_UI_REPORT_APPLY ${SETUP_UI_REPORTS_DIR}/setup_apply_report.json)
set(SETUP_UI_REPORT_FORMAT ${SETUP_UI_REPORTS_DIR}/setup_format_report.json)
set(SETUP_UI_REPORT_CODEGEN ${SETUP_UI_REPORTS_DIR}/setup_codegen_report.json)
set(SETUP_UI_REPORT_REGEN ${SETUP_UI_REPORTS_DIR}/regen_report.json)
set(SETUP_UI_GEN_CPP ${SETUP_UI_GEN_DIR}/ui_setup_ui_actions_gen.cpp)
set(SETUP_UI_GEN_H ${SETUP_UI_GEN_DIR}/ui_setup_ui_actions_gen.h)
set(SETUP_UI_USER_CPP ${SETUP_UI_USER_DIR}/ui_setup_ui_actions_user.cpp)
set(SETUP_UI_USER_H ${SETUP_UI_USER_DIR}/ui_setup_ui_actions_user.h)

add_custom_command(
    OUTPUT
        ${SETUP_UI_DOC}
        ${SETUP_UI_DOC_JSON}
        ${SETUP_UI_GEN_CPP}
        ${SETUP_UI_GEN_H}
        ${SETUP_UI_USER_CPP}
        ${SETUP_UI_USER_H}
        ${SETUP_UI_REGISTRY}
        ${SETUP_UI_REPORT_APPLY}
        ${SETUP_UI_REPORT_FORMAT}
        ${SETUP_UI_REPORT_CODEGEN}
        ${SETUP_UI_REPORT_REGEN}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${SETUP_UI_ROOT}/doc
    COMMAND ${CMAKE_COMMAND} -E make_directory ${SETUP_UI_GEN_DIR}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${SETUP_UI_USER_DIR}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${SETUP_UI_ROOT}/registry
    COMMAND ${CMAKE_COMMAND} -E make_directory ${SETUP_UI_REPORTS_DIR}
    COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-apply ${SETUP_UI_DOC} --script ${SETUP_UI_SCRIPT} --out ${SETUP_UI_DOC} --in-new --report ${SETUP_UI_REPORT_APPLY}
    COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-format ${SETUP_UI_DOC} --report ${SETUP_UI_REPORT_FORMAT}
    COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-codegen --in ${SETUP_UI_DOC} --out ${SETUP_UI_GEN_DIR} --registry ${SETUP_UI_REGISTRY} --docname setup_ui --report ${SETUP_UI_REPORT_CODEGEN}
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${SETUP_UI_REPORT_CODEGEN} ${SETUP_UI_REPORT_REGEN}
    DEPENDS ${SETUP_UI_SCRIPT}
    COMMENT "Regenerating setup UI from ops script"
    VERBATIM
)

add_custom_target(ui_regen_setup
    DEPENDS
        ${SETUP_UI_DOC}
        ${SETUP_UI_DOC_JSON}
        ${SETUP_UI_GEN_CPP}
        ${SETUP_UI_GEN_H}
        ${SETUP_UI_USER_CPP}
        ${SETUP_UI_USER_H}
        ${SETUP_UI_REGISTRY}
        ${SETUP_UI_REPORT_APPLY}
        ${SETUP_UI_REPORT_FORMAT}
        ${SETUP_UI_REPORT_CODEGEN}
        ${SETUP_UI_REPORT_REGEN}
)
add_dependencies(ui_regen_setup dominium-ui-editor)

add_subdirectory(tests)

add_subdirectory(installers/windows_legacy/cmake)

add_subdirectory(installers/macos_classic/cmake)

if(WIN32)
    add_subdirectory(installers/windows/msi/cmake)
    add_subdirectory(installers/windows/exe/cmake)
endif()

if(APPLE)
    add_subdirectory(installers/macos/cmake)
endif()

if(UNIX AND NOT APPLE)
    add_subdirectory(installers/linux/cmake)
endif()

endif() # DOMINIUM_BUILD_SETUP_LEGACY
