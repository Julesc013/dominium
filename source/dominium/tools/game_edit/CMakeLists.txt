cmake_minimum_required(VERSION 3.16)

add_library(dominium_tool_game_edit STATIC
    game_edit_core.c
    tool_game_edit_cli.c
)

target_include_directories(dominium_tool_game_edit
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_tool_game_edit
    PRIVATE
        dominium_tools_core
        domino_sys
)

target_compile_features(dominium_tool_game_edit PRIVATE c_std_90)
