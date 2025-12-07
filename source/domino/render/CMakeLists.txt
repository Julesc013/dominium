set(DOMINO_GFX_SOURCES
    api/gfx_stub.c
)

add_library(domino_gfx STATIC ${DOMINO_GFX_SOURCES})
target_include_directories(domino_gfx
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(domino_gfx PUBLIC domino_sys)
