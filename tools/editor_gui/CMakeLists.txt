cmake_minimum_required(VERSION 3.16)

add_executable(dominium-editor
    editor_gui.c
)

target_include_directories(dominium-editor
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium-editor
    PRIVATE
        dominium_tool_world_edit
        dominium_tool_save_edit
        dominium_tool_game_edit
        dominium_tool_launcher_edit
        dominium_tools_core
        domino_sys
)

target_compile_features(dominium-editor PRIVATE c_std_90)
