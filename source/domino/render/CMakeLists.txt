set(DOMINO_GFX_SOURCES
    api/dom_render_api.c
    api/gfx_stub.c
    api/core/dom_camera.c
    api/core/dom_draw_common.c
    api/core/dom_render_debug.c
    api/core/dom_sprite_batch.c
    api/core/dom_target.c
    api/core/dom_text_layout.c
    api/core/dom_view.c
    api/core/dom_view_build.c
    api/ui/dom_ui_core.c
    null/dom_rend_stub.c
    soft/core/dom_render_software.c
    soft/targets/null/dom_render_null.c
)

add_library(domino_gfx STATIC ${DOMINO_GFX_SOURCES})
target_include_directories(domino_gfx
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/api
        ${CMAKE_CURRENT_SOURCE_DIR}/api/core
        ${CMAKE_CURRENT_SOURCE_DIR}/api/ui
        ${CMAKE_CURRENT_SOURCE_DIR}/dx/dx9
        ${CMAKE_CURRENT_SOURCE_DIR}/soft
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/core
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/targets/null
        ${CMAKE_CURRENT_SOURCE_DIR}/../system/core/base
        ${CMAKE_CURRENT_SOURCE_DIR}/../system/core/base/dom_core
        ${CMAKE_CURRENT_SOURCE_DIR}/../system/core/base/shared
)
target_link_libraries(domino_gfx PUBLIC domino_sys)
