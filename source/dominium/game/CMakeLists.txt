cmake_minimum_required(VERSION 3.16)

add_executable(dominium_game
    dom_game_cli.cpp
    dom_game_app.cpp
    dom_game_camera.cpp
    dom_game_phase.cpp
    dom_game_tools_build.cpp
    dom_game_ui.cpp
    dom_game_ui_debug.cpp
    dom_game_save.cpp
    dom_game_replay.cpp
    dom_game_net.cpp
    entry.cpp
    core/product_info.c
    runtime/dom_game_runtime.cpp
    runtime/dom_game_hash.c
    runtime/dom_game_paths.c
    runtime/dom_game_handshake.cpp
    runtime/dom_game_content_id.cpp
    runtime/dom_game_save.cpp
    runtime/dom_game_replay.cpp
    runtime/dom_game_session.cpp
    runtime/dom_game_net_driver.cpp
    runtime/dom_game_net_snapshot.cpp
    runtime/dom_cosmo_graph.cpp
    runtime/dom_qos.cpp
    runtime/dom_derived_jobs.cpp
    runtime/dom_io_guard.cpp
    runtime/dom_fidelity.cpp
    runtime/dom_snapshot.cpp
    runtime/dom_universe_bundle.cpp
    runtime/dom_frames.cpp
    runtime/dom_orbit_lane.cpp
    runtime/dom_calendar.cpp
    frontends/gui/dom_game_frontend_gui.cpp
    frontends/tui/dom_game_frontend_tui.cpp
    frontends/headless/dom_game_frontend_headless.cpp
    content/dom_game_content_placeholder.c
)

target_include_directories(dominium_game PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../common
)

target_link_libraries(dominium_game
    dominium_common
    core_tlv
    domino_core
)

if(WIN32)
    target_link_libraries(dominium_game ws2_32)
endif()

set_target_properties(dominium_game PROPERTIES
    OUTPUT_NAME "game_dominium"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
set_source_files_properties(runtime/dom_game_paths.c PROPERTIES LANGUAGE CXX)
dist_set_role(dominium_game game)

dominium_bundle_runtime(dominium_game)
