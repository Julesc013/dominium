cmake_minimum_required(VERSION 3.16)

add_executable(dominium_game
    dom_game_cli.cpp
    dom_game_app.cpp
    dom_game_camera.cpp
    dom_game_phase.cpp
    dom_game_tools_build.cpp
    dom_game_ui.cpp
    dom_game_ui_debug.cpp
    ui/dom_ui_state.cpp
    ui/dom_ui_views.cpp
    ui/dom_ui_widgets.cpp
    ui/dom_ui_projection.cpp
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
    runtime/dom_coredata_load.cpp
    runtime/dom_game_save.cpp
    runtime/dom_game_replay.cpp
    runtime/dom_game_session.cpp
    runtime/dom_game_budgets.cpp
    runtime/dom_game_net_driver.cpp
    runtime/dom_game_net_snapshot.cpp
    runtime/dom_cosmo_graph.cpp
    runtime/dom_cosmo_transit.cpp
    runtime/dom_mech_profiles.cpp
    runtime/dom_macro_economy.cpp
    runtime/dom_macro_events.cpp
    runtime/dom_faction_registry.cpp
    runtime/dom_ai_scheduler.cpp
    runtime/dom_ai_planner_logistics.cpp
    runtime/dom_ai_planner_events.cpp
    runtime/dom_qos.cpp
    runtime/dom_derived_jobs.cpp
    runtime/dom_io_guard.cpp
    runtime/dom_fidelity.cpp
    runtime/dom_snapshot.cpp
    runtime/dom_belief_store.cpp
    runtime/dom_capability_engine.cpp
    runtime/dom_universe_bundle.cpp
    runtime/dom_media_provider.cpp
    runtime/dom_atmos_provider.cpp
    runtime/dom_atmos_provider_profile_v1.cpp
    runtime/dom_ocean_provider.cpp
    runtime/dom_weather_provider.cpp
    runtime/dom_vehicle_aero.cpp
    runtime/dom_frames.cpp
    runtime/dom_lane_scheduler.cpp
    runtime/dom_construction_registry.cpp
    runtime/dom_station_registry.cpp
    runtime/dom_route_graph.cpp
    runtime/dom_transfer_scheduler.cpp
    runtime/dom_production.cpp
    runtime/dom_orbit_lane.cpp
    runtime/dom_calendar.cpp
    runtime/dom_time_knowledge.cpp
    runtime/dom_system_registry.cpp
    runtime/dom_body_registry.cpp
    runtime/dom_surface_topology.cpp
    runtime/dom_surface_height.cpp
    runtime/dom_surface_chunks.cpp
    runtime/dom_surface_topology_sphere.cpp
    runtime/dom_surface_topology_ellipsoid.cpp
    runtime/dom_surface_topology_torus.cpp
    frontends/gui/dom_game_frontend_gui.cpp
    frontends/tui/dom_game_frontend_tui.cpp
    frontends/headless/dom_game_frontend_headless.cpp
    content/dom_game_content_placeholder.c
)

target_include_directories(dominium_game PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/domino
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
