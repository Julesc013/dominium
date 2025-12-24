cmake_minimum_required(VERSION 3.16)

add_subdirectory(core)

add_executable(dominium-launcher
    dom_launcher_cli.cpp
    dom_launcher_app.cpp
    dom_launcher_catalog.cpp
    dom_launcher_actions.cpp
    launcher_tui.cpp
    launcher_control_plane.cpp
    launcher_launch_plumbing.cpp
    ${CMAKE_SOURCE_DIR}/tools/launcher/ui/gen/ui_launcher_ui_actions_gen.cpp
    ${CMAKE_SOURCE_DIR}/tools/launcher/ui/user/ui_launcher_ui_actions_user.cpp
)

target_include_directories(dominium-launcher PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/include/dominium/_internal/dom_priv
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/tools/launcher/ui/gen
    ${CMAKE_SOURCE_DIR}/tools/launcher/ui/user
)

target_link_libraries(dominium-launcher
    PRIVATE
        dominium_common
        domino_core
        dominium_launcher_core
        dom_shared
        dsu_core
)

set_target_properties(dominium-launcher PROPERTIES
    OUTPUT_NAME "launch_dominium"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dist_set_role(dominium-launcher launch)

dominium_bundle_runtime(dominium-launcher)

set(LAUNCHER_UI_ROOT ${CMAKE_SOURCE_DIR}/tools/launcher/ui)
set(LAUNCHER_UI_DOC ${LAUNCHER_UI_ROOT}/doc/launcher_ui_doc.tlv)
set(LAUNCHER_UI_DOC_JSON ${LAUNCHER_UI_ROOT}/doc/launcher_ui_doc.json)
set(LAUNCHER_UI_SCRIPT ${LAUNCHER_UI_ROOT}/scripts/minecraft_launcher_v1.ops.json)
set(LAUNCHER_UI_GEN_DIR ${LAUNCHER_UI_ROOT}/gen)
set(LAUNCHER_UI_USER_DIR ${LAUNCHER_UI_ROOT}/user)
set(LAUNCHER_UI_REGISTRY ${LAUNCHER_UI_ROOT}/registry/launcher_actions_registry.json)
set(LAUNCHER_UI_REPORTS_DIR ${LAUNCHER_UI_ROOT}/reports)
set(LAUNCHER_UI_REPORT_APPLY ${LAUNCHER_UI_REPORTS_DIR}/launcher_apply_report.json)
set(LAUNCHER_UI_REPORT_FORMAT ${LAUNCHER_UI_REPORTS_DIR}/launcher_format_report.json)
set(LAUNCHER_UI_REPORT_CODEGEN ${LAUNCHER_UI_REPORTS_DIR}/launcher_codegen_report.json)
set(LAUNCHER_UI_REPORT_REGEN ${LAUNCHER_UI_REPORTS_DIR}/regen_report.json)
set(LAUNCHER_UI_GEN_CPP ${LAUNCHER_UI_GEN_DIR}/ui_launcher_ui_actions_gen.cpp)
set(LAUNCHER_UI_GEN_H ${LAUNCHER_UI_GEN_DIR}/ui_launcher_ui_actions_gen.h)
set(LAUNCHER_UI_USER_CPP ${LAUNCHER_UI_USER_DIR}/ui_launcher_ui_actions_user.cpp)
set(LAUNCHER_UI_USER_H ${LAUNCHER_UI_USER_DIR}/ui_launcher_ui_actions_user.h)

add_custom_command(
    OUTPUT
        ${LAUNCHER_UI_DOC}
        ${LAUNCHER_UI_DOC_JSON}
        ${LAUNCHER_UI_GEN_CPP}
        ${LAUNCHER_UI_GEN_H}
        ${LAUNCHER_UI_USER_CPP}
        ${LAUNCHER_UI_USER_H}
        ${LAUNCHER_UI_REGISTRY}
        ${LAUNCHER_UI_REPORT_APPLY}
        ${LAUNCHER_UI_REPORT_FORMAT}
        ${LAUNCHER_UI_REPORT_CODEGEN}
        ${LAUNCHER_UI_REPORT_REGEN}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${LAUNCHER_UI_ROOT}/doc
    COMMAND ${CMAKE_COMMAND} -E make_directory ${LAUNCHER_UI_GEN_DIR}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${LAUNCHER_UI_USER_DIR}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${LAUNCHER_UI_ROOT}/registry
    COMMAND ${CMAKE_COMMAND} -E make_directory ${LAUNCHER_UI_REPORTS_DIR}
    COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-apply ${LAUNCHER_UI_DOC} --script ${LAUNCHER_UI_SCRIPT} --out ${LAUNCHER_UI_DOC} --in-new --report ${LAUNCHER_UI_REPORT_APPLY}
    COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-format ${LAUNCHER_UI_DOC} --report ${LAUNCHER_UI_REPORT_FORMAT}
    COMMAND $<TARGET_FILE:dominium-ui-editor> --headless-codegen --in ${LAUNCHER_UI_DOC} --out ${LAUNCHER_UI_GEN_DIR} --registry ${LAUNCHER_UI_REGISTRY} --docname launcher_ui --report ${LAUNCHER_UI_REPORT_CODEGEN}
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${LAUNCHER_UI_REPORT_CODEGEN} ${LAUNCHER_UI_REPORT_REGEN}
    DEPENDS ${LAUNCHER_UI_SCRIPT}
    COMMENT "Regenerating launcher UI from ops script"
    VERBATIM
)

add_custom_target(ui_regen_launcher
    DEPENDS
        ${LAUNCHER_UI_DOC}
        ${LAUNCHER_UI_DOC_JSON}
        ${LAUNCHER_UI_GEN_CPP}
        ${LAUNCHER_UI_GEN_H}
        ${LAUNCHER_UI_USER_CPP}
        ${LAUNCHER_UI_USER_H}
        ${LAUNCHER_UI_REGISTRY}
        ${LAUNCHER_UI_REPORT_APPLY}
        ${LAUNCHER_UI_REPORT_FORMAT}
        ${LAUNCHER_UI_REPORT_CODEGEN}
        ${LAUNCHER_UI_REPORT_REGEN}
)
add_dependencies(ui_regen_launcher dominium-ui-editor)

add_executable(tool_manifest_inspector
    tools/tool_manifest_inspector.cpp
)

target_include_directories(tool_manifest_inspector PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(tool_manifest_inspector
    PRIVATE
        domino_core
        dominium_launcher_core
)

set_target_properties(tool_manifest_inspector PROPERTIES
    OUTPUT_NAME "tool_manifest_inspector"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dist_set_role(tool_manifest_inspector tools)

dominium_bundle_runtime(tool_manifest_inspector)

add_executable(dominium_launcher_control_plane_tests
    tests/launcher_control_plane_tests.cpp
    launcher_control_plane.cpp
    launcher_launch_plumbing.cpp
)

target_include_directories(dominium_launcher_control_plane_tests PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(dominium_launcher_control_plane_tests
    PRIVATE
        dominium_common
        domino_core
        dominium_launcher_core
)

set_target_properties(dominium_launcher_control_plane_tests PROPERTIES
    OUTPUT_NAME "dominium_launcher_control_plane_tests"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_control_plane_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_control_plane_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_dependencies(dominium_launcher_control_plane_tests dominium-launcher tool_manifest_inspector)

add_test(NAME dominium_launcher_control_plane_tests COMMAND dominium_launcher_control_plane_tests)

add_executable(dominium_launcher_ui_smoke_tests
    tests/launcher_ui_smoke_tests.cpp
    dom_launcher_app.cpp
    dom_launcher_catalog.cpp
    dom_launcher_actions.cpp
    launcher_launch_plumbing.cpp
)

target_include_directories(dominium_launcher_ui_smoke_tests PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(dominium_launcher_ui_smoke_tests
    PRIVATE
        dominium_common
        domino_core
        dominium_launcher_core
)

set_target_properties(dominium_launcher_ui_smoke_tests PROPERTIES
    OUTPUT_NAME "dominium_launcher_ui_smoke_tests"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_ui_smoke_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_ui_smoke_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_dependencies(dominium_launcher_ui_smoke_tests dominium-launcher tool_manifest_inspector)

add_test(NAME dominium_launcher_ui_smoke_tests COMMAND dominium_launcher_ui_smoke_tests)

add_executable(dominium_launcher_tui_smoke_tests
    tests/launcher_tui_smoke_tests.cpp
    launcher_tui.cpp
    launcher_control_plane.cpp
    launcher_launch_plumbing.cpp
)

target_include_directories(dominium_launcher_tui_smoke_tests PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(dominium_launcher_tui_smoke_tests
    PRIVATE
        dominium_common
        domino_core
        dominium_launcher_core
)

set_target_properties(dominium_launcher_tui_smoke_tests PROPERTIES
    OUTPUT_NAME "dominium_launcher_tui_smoke_tests"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_launcher_tui_smoke_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_launcher_tui_smoke_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_dependencies(dominium_launcher_tui_smoke_tests dominium-launcher tool_manifest_inspector)

add_test(NAME dominium_launcher_tui_smoke_tests COMMAND dominium_launcher_tui_smoke_tests)

add_executable(dominium_launcher_state_smoke_tests
    tests/launcher_state_smoke_tests.cpp
)

target_include_directories(dominium_launcher_state_smoke_tests PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(dominium_launcher_state_smoke_tests
    PRIVATE
        dsu_core
)

set_target_properties(dominium_launcher_state_smoke_tests PROPERTIES
    OUTPUT_NAME "dominium_launcher_state_smoke_tests"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_dependencies(dominium_launcher_state_smoke_tests dominium-launcher)

add_test(NAME dominium_launcher_state_smoke_tests COMMAND dominium_launcher_state_smoke_tests)
