cmake_minimum_required(VERSION 3.15)

add_library(dom_render STATIC
    dom_render_api.c
)

target_include_directories(dom_render
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/engine/core
)

target_link_libraries(dom_render
    PUBLIC
        dom_core
)
