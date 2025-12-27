cmake_minimum_required(VERSION 3.16)

add_subdirectory(core)
add_subdirectory(adapters)

add_executable(dominium-setup
    cli/dominium_setup_main.c
    cli/setup_ui_gui.cpp
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/gen/ui_setup_ui_actions_gen.cpp
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/user/ui_setup_ui_actions_user.cpp
)

target_include_directories(dominium-setup PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/core/include
    ${PROJECT_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/gen
    ${CMAKE_SOURCE_DIR}/tools/setup/ui/user
)

target_link_libraries(dominium-setup
    PRIVATE
        dsu_core
        domino_core
)

set_target_properties(dominium-setup PROPERTIES
    OUTPUT_NAME "tool_setup"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dist_set_role(dominium-setup tools)

dominium_bundle_runtime(dominium-setup)

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

if(WIN32)
    add_subdirectory(installers/windows/msi/cmake)
    add_subdirectory(installers/windows/exe/cmake)
endif()
