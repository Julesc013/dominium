cmake_minimum_required(VERSION 3.15)

add_executable(dom_inspect
    dom_inspect.c
)

target_include_directories(dom_inspect
    PRIVATE
        ${CMAKE_SOURCE_DIR}/source/core
        ${CMAKE_SOURCE_DIR}/source/core/base
        ${CMAKE_SOURCE_DIR}/source/core/base/dom_core
        ${CMAKE_SOURCE_DIR}/source/core/math
        ${CMAKE_SOURCE_DIR}/source/core/sim
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

target_link_libraries(dom_inspect
    PRIVATE
        dom_engine
)
