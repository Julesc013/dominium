cmake_minimum_required(VERSION 3.15)

add_library(dom_render STATIC
    dom_render_api.c
    dom_render_dx9.c
    dom_render_null.c
    dom_render_debug.c
    software/dom_render_software.c
    core/dom_draw_common.c
    core/dom_text_layout.c
    core/dom_sprite_batch.c
    core/dom_camera.c
    core/dom_view.c
    core/dom_view_build.c
    core/dom_target.c
)

target_include_directories(dom_render
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/core
        ${CMAKE_CURRENT_SOURCE_DIR}/software
        ${CMAKE_SOURCE_DIR}/engine/core
)

target_link_libraries(dom_render
    PUBLIC
        dom_core
        d3d9
)
