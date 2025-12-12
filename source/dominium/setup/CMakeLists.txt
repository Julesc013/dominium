cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup
    dom_setup_cli.cpp
    dom_setup_app.cpp
    dom_setup_ops.cpp
)

target_include_directories(dominium-setup PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dominium-setup
    PRIVATE
        dominium_common
        domino_core
)

set_target_properties(dominium-setup PROPERTIES
    OUTPUT_NAME "dominium-setup"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup)
