cmake_minimum_required(VERSION 3.16)

add_executable(dominium_game
    main_game.cpp
    game_app.cpp
)

target_include_directories(dominium_game PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_game
    domino_core
)

set_target_properties(dominium_game PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
