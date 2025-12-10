cmake_minimum_required(VERSION 3.16)

add_library(dominium_common STATIC
    dominium_product_manifest.c
    dominium_version.c
    game_content_api.c
    dominium_product_info.c
    dmn_paths.c
    dmn_repo.c
    dmn_instance.c
)

target_include_directories(dominium_common
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_common
    PUBLIC
        domino_mod
)
