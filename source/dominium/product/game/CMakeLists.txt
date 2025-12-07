add_executable(dominium_game_cli
    core/dominium_game_main.c
    cli/dominium_game_cli_main.c
)

target_include_directories(dominium_game_cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal/dom_priv
)

target_link_libraries(dominium_game_cli
    PRIVATE
        domino_sys
        domino_mod
        domino_gfx
        dominium_product_common
)
