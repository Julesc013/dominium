cmake_minimum_required(VERSION 3.16)

add_executable(dominium_client
    main_client.c
)
target_link_libraries(dominium_client PRIVATE
    engine::domino
    game::dominium
)
set_target_properties(dominium_client PROPERTIES
    OUTPUT_NAME "client"
    LINKER_LANGUAGE CXX
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
