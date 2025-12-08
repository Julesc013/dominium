cmake_minimum_required(VERSION 3.16)

add_library(dominium_product_common STATIC
    common/dominium_product_manifest.c
    common/dominium_version.c
    common/game_content_api.c
)

target_include_directories(dominium_product_common
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(dominium_product_common
    PUBLIC
        domino_mod
)

add_subdirectory(launcher)
add_subdirectory(setup)
add_subdirectory(game)
