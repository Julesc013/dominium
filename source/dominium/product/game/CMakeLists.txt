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
        -Wl,--start-group
        domino_engine
        domino_mod
        dominium_rules
        domino_sim
        domino_core
        domino_gfx
        domino_sys
        dominium_product_common
        -Wl,--end-group
)
