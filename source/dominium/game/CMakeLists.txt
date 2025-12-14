cmake_minimum_required(VERSION 3.16)

add_executable(dominium_game
    dom_game_cli.cpp
    dom_game_app.cpp
    dom_game_camera.cpp
    dom_game_states.cpp
    dom_game_tools_build.cpp
    dom_game_ui.cpp
    dom_game_ui_debug.cpp
    dom_game_save.cpp
    dom_game_replay.cpp
    dom_game_net.cpp
    entry.cpp
)

target_include_directories(dominium_game PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../common
)

target_link_libraries(dominium_game
    dominium_common
    domino_core
)

if(WIN32)
    target_link_libraries(dominium_game ws2_32)
endif()

set_target_properties(dominium_game PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium_game)
