add_executable(dominium_game
    core/game_stub.c
)

target_include_directories(dominium_game
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal/dom_priv
)

target_link_libraries(dominium_game
    PRIVATE
        domino_sys
        domino_sim
        domino_mod
        domino_gfx
        dominium_rules
)
