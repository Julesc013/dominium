set(DOMINO_GFX_SOURCES
    api/domino_gfx_core.c
    api/domino_gfx_internal.h
    soft/core/domino_soft_core.c
    soft/soft_internal.h
    soft/targets/null/soft_target_null.c
)

if(WIN32)
    list(APPEND DOMINO_GFX_SOURCES
        soft/targets/win32/soft_target_win32.c
    )
endif()

add_library(domino_gfx STATIC ${DOMINO_GFX_SOURCES})
target_include_directories(domino_gfx
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/api
        ${CMAKE_CURRENT_SOURCE_DIR}/soft
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/core
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/targets/null
        ${CMAKE_CURRENT_SOURCE_DIR}/soft/targets/win32
)
target_link_libraries(domino_gfx PUBLIC domino_sys)
target_compile_features(domino_gfx PRIVATE c_std_90)
if(WIN32)
    target_link_libraries(domino_gfx PRIVATE gdi32 user32)
endif()
