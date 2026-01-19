cmake_minimum_required(VERSION 3.16)

add_executable(dominium_server
    app/main_server.c
)
target_link_libraries(dominium_server PRIVATE
    domino_engine
    dominium_game
)
set_target_properties(dominium_server PROPERTIES
    OUTPUT_NAME "server"
    LINKER_LANGUAGE CXX
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
