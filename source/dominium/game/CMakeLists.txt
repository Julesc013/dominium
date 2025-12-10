add_subdirectory(rules)

add_executable(dominium_game_cli
    core/dominium_game_main.c
    core/g_runtime.c
    core/g_modes.c
    core/product_info.c
    cli/dominium_game_cli_main.c
)

target_include_directories(dominium_game_cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal/dom_priv
        ${CMAKE_CURRENT_SOURCE_DIR}/core
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
        dominium_common
        -Wl,--end-group
)
