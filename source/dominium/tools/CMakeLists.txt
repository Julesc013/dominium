cmake_minimum_required(VERSION 3.16)

add_subdirectory(core)
add_subdirectory(assetc)
add_subdirectory(pack)
add_subdirectory(replay)
add_subdirectory(test)
add_subdirectory(world_edit)
add_subdirectory(save_edit)
add_subdirectory(game_edit)
add_subdirectory(launcher_edit)
add_subdirectory(editor_gui)
add_subdirectory(modcheck)

target_link_libraries(dominium-tools
    PRIVATE
        dominium_tool_assetc
        dominium_tool_pack
        dominium_tool_replay
        dominium_tool_test
        dominium_tool_world_edit
        dominium_tool_save_edit
        dominium_tool_game_edit
        dominium_tool_launcher_edit
        domino_sys
)
