cmake_minimum_required(VERSION 3.16)

add_subdirectory(core)

add_executable(dominium-launcher
    dom_launcher_cli.cpp
    dom_launcher_app.cpp
    dom_launcher_catalog.cpp
    dom_launcher_actions.cpp
)

target_include_directories(dominium-launcher PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(dominium-launcher
    PRIVATE
        dominium_common
        domino_core
        dominium_launcher_core
)

set_target_properties(dominium-launcher PROPERTIES
    OUTPUT_NAME "dominium-launcher"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-launcher)
