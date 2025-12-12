cmake_minimum_required(VERSION 3.16)

add_library(dominium_common STATIC
    dominium_product_manifest.c
    dominium_version.c
    game_content_api.c
    dominium_product_info.c
    dmn_paths.c
    dmn_repo.c
    dmn_instance.c
    dom_paths.cpp
    dom_instance.cpp
    dom_packset.cpp
    dom_session.cpp
    dom_compat.cpp
)

target_include_directories(dominium_common
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/source/domino
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dominium_common
    PUBLIC
        domino_mod
        domino_gfx
)
