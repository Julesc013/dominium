cmake_minimum_required(VERSION 3.16)

add_executable(dominium-modcheck
    modcheck/dom_modcheck_main.cpp
    modcheck/dom_modcheck.cpp
)

target_include_directories(dominium-modcheck PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/domino
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dominium-modcheck
    PRIVATE
        dominium_common
        domino_core
)

set_target_properties(dominium-modcheck PROPERTIES
    OUTPUT_NAME "dominium-modcheck"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-modcheck)
