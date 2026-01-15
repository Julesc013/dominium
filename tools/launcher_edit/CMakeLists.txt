cmake_minimum_required(VERSION 3.16)

add_library(dominium_tool_launcher_edit STATIC
    launcher_edit_core.c
    tool_launcher_edit_cli.c
)

target_include_directories(dominium_tool_launcher_edit
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_tool_launcher_edit
    PRIVATE
        dominium_tools_core
        domino_sys
)

target_compile_features(dominium_tool_launcher_edit PRIVATE c_std_90)
