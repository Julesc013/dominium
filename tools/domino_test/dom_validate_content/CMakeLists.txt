cmake_minimum_required(VERSION 3.15)

add_executable(dom_validate_content
    dom_validate_content.c
)

target_include_directories(dom_validate_content
    PRIVATE
        ${CMAKE_SOURCE_DIR}/source/core
        ${CMAKE_SOURCE_DIR}/source/core/base
        ${CMAKE_SOURCE_DIR}/source/core/base/dom_core
        ${CMAKE_SOURCE_DIR}/source/core/math
        ${CMAKE_SOURCE_DIR}/source/core/sim
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

target_link_libraries(dom_validate_content
    PRIVATE
        dom_engine
)
