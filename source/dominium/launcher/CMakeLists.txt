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
)

target_include_directories(dominium-launcher PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/include/dominium/_internal/dom_priv
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
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
    OUTPUT_NAME "dominium-launcher"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-launcher)

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
