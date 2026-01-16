cmake_minimum_required(VERSION 3.16)

add_library(dominium_game STATIC
    dominium_game_stub.c
)
target_include_directories(dominium_game
    PUBLIC
        ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(dominium_game
    PUBLIC
        engine::domino
        libs::contracts
)
set_target_properties(dominium_game PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(game::dominium ALIAS dominium_game)
