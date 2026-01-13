cmake_minimum_required(VERSION 3.16)

enable_testing()

include_directories(
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

set(DOM_GAME_RUNTIME_TEST_EXTRAS
    ../dominium/game/runtime/dom_coredata_load.cpp
    ../dominium/game/runtime/dom_mech_profiles.cpp
    ../dominium/game/runtime/dom_asset_registry.cpp
    ../dominium/game/runtime/dom_money_standard.cpp
    ../dominium/game/runtime/dom_contract_templates.cpp
    ../dominium/game/runtime/dom_instrument_registry.cpp
    ../dominium/game/runtime/dom_econ_access_control.cpp
    ../dominium/game/runtime/dom_econ_pack_load.cpp
    ../dominium/game/runtime/dom_contract_runtime.cpp
    ../dominium/game/runtime/dom_media_provider.cpp
    ../dominium/game/runtime/dom_atmos_provider.cpp
    ../dominium/game/runtime/dom_atmos_provider_profile_v1.cpp
    ../dominium/game/runtime/dom_ocean_provider.cpp
    ../dominium/game/runtime/dom_weather_provider.cpp
    ../dominium/game/runtime/dom_vehicle_aero.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
    ../dominium/game/runtime/dom_qos.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_station_registry.cpp
    ../dominium/game/runtime/dom_route_graph.cpp
    ../dominium/game/runtime/dom_transfer_scheduler.cpp
    ../dominium/game/runtime/dom_production.cpp
    ../dominium/game/runtime/dom_macro_economy.cpp
    ../dominium/game/runtime/dom_macro_events.cpp
    ../dominium/game/runtime/dom_faction_registry.cpp
    ../dominium/game/runtime/dom_ai_scheduler.cpp
    ../dominium/game/runtime/dom_ai_planner_logistics.cpp
    ../dominium/game/runtime/dom_ai_planner_events.cpp
    ../dominium/game/runtime/dom_orbit_lane.cpp
    ../dominium/game/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_paths.c
)

add_library(dom_game_runtime_test_support STATIC ${DOM_GAME_RUNTIME_TEST_EXTRAS})

set_source_files_properties(../dominium/game/runtime/dom_game_paths.c
    PROPERTIES LANGUAGE CXX
)

target_include_directories(dom_game_runtime_test_support PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

set_target_properties(dom_game_runtime_test_support PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

set(DG_DET_SCAN_FILES "")
foreach(dir IN ITEMS
    ${CMAKE_SOURCE_DIR}/source/domino/core
    ${CMAKE_SOURCE_DIR}/source/domino/agent
    ${CMAKE_SOURCE_DIR}/source/domino/decor
    ${CMAKE_SOURCE_DIR}/source/domino/sim
    ${CMAKE_SOURCE_DIR}/source/domino/struct
    ${CMAKE_SOURCE_DIR}/source/domino/trans
    ${CMAKE_SOURCE_DIR}/source/domino/world
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime
)
    file(GLOB_RECURSE dir_files CONFIGURE_DEPENDS
        ${dir}/*.c
        ${dir}/*.h
        ${dir}/*.cpp
    )
    list(APPEND DG_DET_SCAN_FILES ${dir_files})
endforeach()
list(SORT DG_DET_SCAN_FILES)

list(FILTER DG_DET_SCAN_FILES EXCLUDE REGEX "core_internal\\.h$")
list(FILTER DG_DET_SCAN_FILES EXCLUDE REGEX "fixed_debug\\.c$")
list(FILTER DG_DET_SCAN_FILES EXCLUDE REGEX "fs_util\\.c$")

set(DG_DET_SCAN_FILES_REL "")
foreach(abs IN LISTS DG_DET_SCAN_FILES)
    file(RELATIVE_PATH rel ${CMAKE_SOURCE_DIR} ${abs})
    string(REPLACE "\\" "/" rel ${rel})
    list(APPEND DG_DET_SCAN_FILES_REL ${rel})
endforeach()

set(DG_DET_SCAN_OUT_H ${CMAKE_CURRENT_BINARY_DIR}/dg_det_scan_files.h)
file(WRITE ${DG_DET_SCAN_OUT_H}
    "/* Generated: deterministic source scan file list. */\n"
    "#ifndef DG_DET_SCAN_FILES_H\n"
    "#define DG_DET_SCAN_FILES_H\n"
    "static const char *dg_det_scan_files[] = {\n"
)
foreach(rel IN LISTS DG_DET_SCAN_FILES_REL)
    file(APPEND ${DG_DET_SCAN_OUT_H} "    \"${rel}\",\n")
endforeach()
file(APPEND ${DG_DET_SCAN_OUT_H}
    "};\n"
    "static const unsigned dg_det_scan_file_count = (unsigned)(sizeof(dg_det_scan_files) / sizeof(dg_det_scan_files[0]));\n"
    "#endif /* DG_DET_SCAN_FILES_H */\n"
)

add_executable(domino_numeric_test
    numeric_test.c
)

target_include_directories(domino_numeric_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_numeric_test
    domino_core
)

set_target_properties(domino_numeric_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_numeric_test COMMAND domino_numeric_test)

add_executable(dom_time_core_tests
    dom_time_core_tests.c
)

target_include_directories(dom_time_core_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(dom_time_core_tests
    domino_core
)

set_target_properties(dom_time_core_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dom_time_core_tests COMMAND dom_time_core_tests)

add_executable(dom_ledger_core_tests
    dom_ledger_core_tests.c
)

target_include_directories(dom_ledger_core_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(dom_ledger_core_tests
    domino_core
)

set_target_properties(dom_ledger_core_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dom_ledger_core_tests COMMAND dom_ledger_core_tests)

add_executable(dom_universe_bundle_epoch_test
    dom_universe_bundle_epoch_test.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
)

target_include_directories(dom_universe_bundle_epoch_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_universe_bundle_epoch_test
    core_tlv
    dominium_common
    domino_core
)

set_target_properties(dom_universe_bundle_epoch_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_universe_bundle_epoch_test COMMAND dom_universe_bundle_epoch_test)

add_executable(dom_cosmo_graph_determinism_test
    dom_cosmo_graph_determinism_test.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
)

target_include_directories(dom_cosmo_graph_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_cosmo_graph_determinism_test
    domino_core
)

set_target_properties(dom_cosmo_graph_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_cosmo_graph_determinism_test COMMAND dom_cosmo_graph_determinism_test)

add_executable(dom_cosmo_transit_determinism_test
    dom_cosmo_transit_determinism_test.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_cosmo_transit_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_cosmo_transit_determinism_test
    domino_core
)

set_target_properties(dom_cosmo_transit_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_cosmo_transit_determinism_test COMMAND dom_cosmo_transit_determinism_test)

add_executable(dom_cosmo_bundle_roundtrip_test
    dom_cosmo_bundle_roundtrip_test.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
)

target_include_directories(dom_cosmo_bundle_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_cosmo_bundle_roundtrip_test
    core_tlv
    dominium_common
    domino_core
)

set_target_properties(dom_cosmo_bundle_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_cosmo_bundle_roundtrip_test COMMAND dom_cosmo_bundle_roundtrip_test)

add_executable(dom_frames_validation_test
    dom_frames_validation_test.cpp
    ../dominium/game/runtime/dom_frames.cpp
)

target_include_directories(dom_frames_validation_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_frames_validation_test
    domino_core
)

set_target_properties(dom_frames_validation_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_frames_validation_test COMMAND dom_frames_validation_test)

add_executable(dom_frames_transform_roundtrip_test
    dom_frames_transform_roundtrip_test.cpp
    ../dominium/game/runtime/dom_frames.cpp
)

target_include_directories(dom_frames_transform_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_frames_transform_roundtrip_test
    domino_core
)

set_target_properties(dom_frames_transform_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_frames_transform_roundtrip_test COMMAND dom_frames_transform_roundtrip_test)

add_executable(dom_topology_default_test
    dom_topology_default_test.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
)

target_include_directories(dom_topology_default_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_topology_default_test
    domino_core
)

set_target_properties(dom_topology_default_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_topology_default_test COMMAND dom_topology_default_test)

add_executable(dom_surface_latlong_determinism_test
    dom_surface_latlong_determinism_test.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
)

target_include_directories(dom_surface_latlong_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_surface_latlong_determinism_test
    domino_core
)

set_target_properties(dom_surface_latlong_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_surface_latlong_determinism_test COMMAND dom_surface_latlong_determinism_test)

add_executable(dom_surface_chunk_activation_determinism_test
    dom_surface_chunk_activation_determinism_test.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
)

target_include_directories(dom_surface_chunk_activation_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_surface_chunk_activation_determinism_test
    dominium_common
    domino_core
)

set_target_properties(dom_surface_chunk_activation_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_surface_chunk_activation_determinism_test COMMAND dom_surface_chunk_activation_determinism_test)

add_executable(dom_landing_attachment_invariance_test
    dom_landing_attachment_invariance_test.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
)

target_include_directories(dom_landing_attachment_invariance_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_landing_attachment_invariance_test
    domino_core
)

set_target_properties(dom_landing_attachment_invariance_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_landing_attachment_invariance_test COMMAND dom_landing_attachment_invariance_test)

add_executable(dom_surface_streaming_no_modal_loading_test
    dom_surface_streaming_no_modal_loading_test.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_surface_streaming_no_modal_loading_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_surface_streaming_no_modal_loading_test
    dominium_common
    domino_core
)

set_target_properties(dom_surface_streaming_no_modal_loading_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_surface_streaming_no_modal_loading_test COMMAND dom_surface_streaming_no_modal_loading_test)

add_executable(dom_construction_placement_determinism_test
    dom_construction_placement_determinism_test.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
)

target_include_directories(dom_construction_placement_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_construction_placement_determinism_test
    core_tlv
    domino_core
)

set_target_properties(dom_construction_placement_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_construction_placement_determinism_test COMMAND dom_construction_placement_determinism_test)

add_executable(dom_construction_overlap_refusal_test
    dom_construction_overlap_refusal_test.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
)

target_include_directories(dom_construction_overlap_refusal_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_construction_overlap_refusal_test
    domino_core
)

set_target_properties(dom_construction_overlap_refusal_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_construction_overlap_refusal_test COMMAND dom_construction_overlap_refusal_test)

add_executable(dom_construction_save_load_roundtrip_test
    dom_construction_save_load_roundtrip_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_construction_save_load_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_construction_save_load_roundtrip_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_construction_save_load_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_construction_save_load_roundtrip_test COMMAND dom_construction_save_load_roundtrip_test)

add_executable(dom_construction_replay_test
    dom_construction_replay_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_construction_replay_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_construction_replay_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_construction_replay_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_construction_replay_test COMMAND dom_construction_replay_test)

add_executable(dom_logistics_schedule_determinism_test
    dom_logistics_schedule_determinism_test.cpp
    ../dominium/game/runtime/dom_station_registry.cpp
    ../dominium/game/runtime/dom_route_graph.cpp
    ../dominium/game/runtime/dom_transfer_scheduler.cpp
)

target_include_directories(dom_logistics_schedule_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_logistics_schedule_determinism_test
    domino_core
)

set_target_properties(dom_logistics_schedule_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_logistics_schedule_determinism_test COMMAND dom_logistics_schedule_determinism_test)

add_executable(dom_logistics_inventory_conservation_test
    dom_logistics_inventory_conservation_test.cpp
    ../dominium/game/runtime/dom_station_registry.cpp
    ../dominium/game/runtime/dom_route_graph.cpp
    ../dominium/game/runtime/dom_transfer_scheduler.cpp
)

target_include_directories(dom_logistics_inventory_conservation_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_logistics_inventory_conservation_test
    domino_core
)

set_target_properties(dom_logistics_inventory_conservation_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_logistics_inventory_conservation_test COMMAND dom_logistics_inventory_conservation_test)

add_executable(dom_production_tick_invariance_test
    dom_production_tick_invariance_test.cpp
    ../dominium/game/runtime/dom_station_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_macro_economy.cpp
    ../dominium/game/runtime/dom_production.cpp
)

target_include_directories(dom_production_tick_invariance_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_production_tick_invariance_test
    domino_core
)

set_target_properties(dom_production_tick_invariance_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_production_tick_invariance_test COMMAND dom_production_tick_invariance_test)

add_executable(dom_logistics_save_load_roundtrip_test
    dom_logistics_save_load_roundtrip_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_logistics_save_load_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_logistics_save_load_roundtrip_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_logistics_save_load_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_logistics_save_load_roundtrip_test COMMAND dom_logistics_save_load_roundtrip_test)

add_executable(dom_ai_determinism_same_seed_test
    dom_ai_determinism_same_seed_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_ai_determinism_same_seed_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ai_determinism_same_seed_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_ai_determinism_same_seed_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ai_determinism_same_seed_test COMMAND dom_ai_determinism_same_seed_test)

add_executable(dom_ai_budget_behavior_test
    dom_ai_budget_behavior_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_ai_budget_behavior_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ai_budget_behavior_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_ai_budget_behavior_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ai_budget_behavior_test COMMAND dom_ai_budget_behavior_test)

add_executable(dom_ai_budget_baseline_cap_test
    dom_ai_budget_baseline_cap_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_budgets.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_ai_budget_baseline_cap_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ai_budget_baseline_cap_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_ai_budget_baseline_cap_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ai_budget_baseline_cap_test COMMAND dom_ai_budget_baseline_cap_test)

add_executable(dom_ai_persistence_roundtrip_test
    dom_ai_persistence_roundtrip_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_ai_persistence_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ai_persistence_roundtrip_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_ai_persistence_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ai_persistence_roundtrip_test COMMAND dom_ai_persistence_roundtrip_test)

add_executable(dom_ai_replay_test
    dom_ai_replay_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_ai_replay_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ai_replay_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_ai_replay_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ai_replay_test COMMAND dom_ai_replay_test)

add_executable(dom_universe_bundle_systems_roundtrip_test
    dom_universe_bundle_systems_roundtrip_test.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
)

target_include_directories(dom_universe_bundle_systems_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_universe_bundle_systems_roundtrip_test
    core_tlv
    dominium_common
    domino_core
)

set_target_properties(dom_universe_bundle_systems_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_universe_bundle_systems_roundtrip_test COMMAND dom_universe_bundle_systems_roundtrip_test)

add_executable(dom_caps_hash_test
    dom_caps_hash_test.cpp
)

target_include_directories(dom_caps_hash_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)

target_link_libraries(dom_caps_hash_test
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_caps_hash_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_caps_hash_test COMMAND dom_caps_hash_test)

add_executable(dom_handshake_identity_test
    dom_handshake_identity_test.cpp
    ../dominium/game/runtime/dom_game_handshake.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_handshake_identity_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_handshake_identity_test
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_handshake_identity_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_handshake_identity_test COMMAND dom_handshake_identity_test)

add_executable(dom_replay_epoch_test
    dom_replay_epoch_test.cpp
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_replay_epoch_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_replay_epoch_test
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_replay_epoch_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_replay_epoch_test COMMAND dom_replay_epoch_test)

add_executable(dom_no_modal_loading_test
    dom_no_modal_loading_test.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_no_modal_loading_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_no_modal_loading_test
    dominium_common
    domino_core
)

set_target_properties(dom_no_modal_loading_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_no_modal_loading COMMAND dom_no_modal_loading_test)

add_executable(dom_derived_order_independence_test
    dom_derived_order_independence_test.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
)

target_include_directories(dom_derived_order_independence_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_derived_order_independence_test
    dominium_common
    domino_core
)

set_target_properties(dom_derived_order_independence_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_derived_order_independence COMMAND dom_derived_order_independence_test)

add_executable(dom_snapshot_isolation_test
    dom_snapshot_isolation_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_snapshot.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_snapshot_isolation_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_snapshot_isolation_test PRIVATE
    dominium_common
    domino_core
)

set_target_properties(dom_snapshot_isolation_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_snapshot_isolation COMMAND dom_snapshot_isolation_test)

add_executable(dominium_capability_tests
    dominium_capability_tests.cpp
    ../dominium/game/runtime/dom_belief_store.cpp
    ../dominium/game/runtime/dom_capability_engine.cpp
    ../dominium/game/runtime/dom_time_knowledge.cpp
)

target_include_directories(dominium_capability_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dominium_capability_tests
    dominium_common
    domino_core
)

set_target_properties(dominium_capability_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if (MSVC)
    target_compile_options(dominium_capability_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_capability_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()

add_test(NAME dominium_capability_tests COMMAND dominium_capability_tests)

add_executable(dom_ui_continuity_tests
    dom_ui_continuity_tests.cpp
    ../dominium/game/ui/dom_ui_state.cpp
    ../dominium/game/ui/dom_ui_views.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_ui_continuity_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ui_continuity_tests
    domino_core
)

set_target_properties(dom_ui_continuity_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME seamless_travel_test COMMAND dom_ui_continuity_tests seamless_travel)
add_test(NAME fidelity_degradation_visual_test COMMAND dom_ui_continuity_tests fidelity_degradation_visual)
add_test(NAME input_continuity_test COMMAND dom_ui_continuity_tests input_continuity)

add_executable(dom_session_authority_tests
    dom_session_authority_tests.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_net_driver.cpp
    ../dominium/game/runtime/dom_game_net_snapshot.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_game_session.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_qos.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_session_authority_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_session_authority_tests PRIVATE
    dominium_common
    domino_core
)

set_target_properties(dom_session_authority_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_session_authority_smoke COMMAND dom_session_authority_tests)

add_executable(dom_qos_determinism_test
    dom_qos_determinism_test.cpp
    ../dominium/game/runtime/dom_qos.cpp
)

target_include_directories(dom_qos_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)

target_link_libraries(dom_qos_determinism_test
    core_tlv
    domino_core
)

set_target_properties(dom_qos_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_qos_determinism COMMAND dom_qos_determinism_test)

add_executable(dom_qos_no_sim_effect_test
    dom_qos_no_sim_effect_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_qos.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_qos_no_sim_effect_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_qos_no_sim_effect_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_qos_no_sim_effect_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_qos_no_sim_effect COMMAND dom_qos_no_sim_effect_test)

add_executable(dom_qos_overload_test
    dom_qos_overload_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_qos.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_qos_overload_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_qos_overload_test PRIVATE
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_qos_overload_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME test_qos_overload COMMAND dom_qos_overload_test)

add_executable(dom_orbit_golden_vectors_test
    dom_orbit_golden_vectors_test.cpp
    ../dominium/game/runtime/dom_orbit_lane.cpp
)

target_include_directories(dom_orbit_golden_vectors_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_orbit_golden_vectors_test
    dominium_common
    domino_core
)

set_target_properties(dom_orbit_golden_vectors_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_orbit_golden_vectors_test COMMAND dom_orbit_golden_vectors_test)

add_executable(dom_orbit_warp_invariance_test
    dom_orbit_warp_invariance_test.cpp
    ../dominium/game/runtime/dom_orbit_lane.cpp
)

target_include_directories(dom_orbit_warp_invariance_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_orbit_warp_invariance_test
    dominium_common
    domino_core
)

set_target_properties(dom_orbit_warp_invariance_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_orbit_warp_invariance_test COMMAND dom_orbit_warp_invariance_test)

add_executable(dom_orbit_event_consistency_test
    dom_orbit_event_consistency_test.cpp
    ../dominium/game/runtime/dom_orbit_lane.cpp
)

target_include_directories(dom_orbit_event_consistency_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_orbit_event_consistency_test
    dominium_common
    domino_core
)

set_target_properties(dom_orbit_event_consistency_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_orbit_event_consistency_test COMMAND dom_orbit_event_consistency_test)

add_executable(dom_orbit_warp_authority_test
    dom_orbit_warp_authority_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_net_driver.cpp
    ../dominium/game/runtime/dom_game_net_snapshot.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_game_session.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_qos.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_orbit_warp_authority_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_orbit_warp_authority_test PRIVATE
    dominium_common
    domino_core
)

set_target_properties(dom_orbit_warp_authority_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_orbit_warp_authority_test COMMAND dom_orbit_warp_authority_test)

add_executable(dom_orbit_replay_test
    dom_orbit_replay_test.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_system_registry.cpp
    ../dominium/game/runtime/dom_body_registry.cpp
    ../dominium/game/runtime/dom_frames.cpp
    ../dominium/game/runtime/dom_lane_scheduler.cpp
    ../dominium/game/runtime/dom_surface_chunks.cpp
    ../dominium/game/runtime/dom_derived_jobs.cpp
    ../dominium/game/runtime/dom_surface_topology.cpp
    ../dominium/game/runtime/dom_surface_topology_sphere.cpp
    ../dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ../dominium/game/runtime/dom_surface_topology_torus.cpp
    ../dominium/game/runtime/dom_surface_height.cpp
    ../dominium/game/runtime/dom_construction_registry.cpp
    ../dominium/game/runtime/dom_game_hash.c
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_game_save.cpp
    ../dominium/game/runtime/dom_game_content_id.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_cosmo_graph.cpp
    ../dominium/game/runtime/dom_cosmo_transit.cpp
)

target_include_directories(dom_orbit_replay_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_orbit_replay_test PRIVATE
    dominium_common
    domino_core
)

set_target_properties(dom_orbit_replay_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_orbit_replay_test COMMAND dom_orbit_replay_test)

add_executable(domino_pkt_determinism_test
    pkt_determinism_test.c
)

target_include_directories(domino_pkt_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_pkt_determinism_test
    domino_core
)

set_target_properties(domino_pkt_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_pkt_determinism_test COMMAND domino_pkt_determinism_test)

add_executable(domino_sched_determinism_test
    sched_determinism_test.c
)

target_include_directories(domino_sched_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_sched_determinism_test
    domino_core
)

set_target_properties(domino_sched_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_sched_determinism_test COMMAND domino_sched_determinism_test)

add_executable(domino_stimulus_determinism_test
    stimulus_determinism_test.c
)

target_include_directories(domino_stimulus_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_stimulus_determinism_test
    domino_core
)

set_target_properties(domino_stimulus_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_stimulus_determinism_test COMMAND domino_stimulus_determinism_test)

add_executable(domino_lod_framework_test
    lod_framework_test.c
)

target_include_directories(domino_lod_framework_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_lod_framework_test
    domino_core
)

set_target_properties(domino_lod_framework_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_lod_framework_test COMMAND domino_lod_framework_test)

add_executable(domino_pose_anchor_quant_test
    pose_anchor_quant_test.c
)

target_include_directories(domino_pose_anchor_quant_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_pose_anchor_quant_test
    domino_core
)

set_target_properties(domino_pose_anchor_quant_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_pose_anchor_quant_test COMMAND domino_pose_anchor_quant_test)

add_executable(domino_trans_compile_determinism_test
    ../../tests/domino_trans/test_dg_trans_compile_determinism.c
)

target_include_directories(domino_trans_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_trans_compile_determinism_test
    domino_core
)

set_target_properties(domino_trans_compile_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_trans_compile_determinism_test COMMAND domino_trans_compile_determinism_test)

add_executable(domino_struct_compile_determinism_test
    ../../tests/domino_struct/test_dg_struct_compile_determinism.c
)

target_include_directories(domino_struct_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_struct_compile_determinism_test
    domino_core
)

set_target_properties(domino_struct_compile_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_struct_compile_determinism_test COMMAND domino_struct_compile_determinism_test)

add_executable(domino_decor_compile_determinism_test
    ../../tests/domino_decor/test_dg_decor_compile_determinism.c
)

target_include_directories(domino_decor_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_decor_compile_determinism_test
    domino_core
)

set_target_properties(domino_decor_compile_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_decor_compile_determinism_test COMMAND domino_decor_compile_determinism_test)

add_executable(domino_agent_behavior_determinism_test
    agent_behavior_determinism_test.c
)

target_include_directories(domino_agent_behavior_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_agent_behavior_determinism_test
    domino_core
)

set_target_properties(domino_agent_behavior_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_agent_behavior_determinism_test COMMAND domino_agent_behavior_determinism_test)

add_executable(domino_graph_toolkit_determinism_test
    graph_toolkit_determinism_test.c
)

target_include_directories(domino_graph_toolkit_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_graph_toolkit_determinism_test
    domino_core
)

set_target_properties(domino_graph_toolkit_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_graph_toolkit_determinism_test COMMAND domino_graph_toolkit_determinism_test)

add_executable(domino_domains_frames_prop_determinism_test
    domains_frames_prop_determinism_test.c
)

target_include_directories(domino_domains_frames_prop_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_domains_frames_prop_determinism_test
    domino_core
)

set_target_properties(domino_domains_frames_prop_determinism_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_domains_frames_prop_determinism_test COMMAND domino_domains_frames_prop_determinism_test)

add_executable(domino_det_regression_scan_test
    determinism_regression_scan_test.c
)

target_include_directories(domino_det_regression_scan_test PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)

set_target_properties(domino_det_regression_scan_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_regression_scan_test COMMAND domino_det_regression_scan_test)
set_tests_properties(domino_det_regression_scan_test PROPERTIES
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

add_executable(domino_det_sched_test
    ../../tests/determinism/det_sched.c
)

target_include_directories(domino_det_sched_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_sched_test
    domino_core
)

set_target_properties(domino_det_sched_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_sched_test COMMAND domino_det_sched_test)

add_executable(domino_det_packets_test
    ../../tests/determinism/det_packets.c
)

target_include_directories(domino_det_packets_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_packets_test
    domino_core
)

set_target_properties(domino_det_packets_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_packets_test COMMAND domino_det_packets_test)

add_executable(domino_det_lod_test
    ../../tests/determinism/det_lod.c
)

target_include_directories(domino_det_lod_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_lod_test
    domino_core
)

set_target_properties(domino_det_lod_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_lod_test COMMAND domino_det_lod_test)

add_executable(domino_det_trans_test
    ../../tests/determinism/det_trans.c
)

target_include_directories(domino_det_trans_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_trans_test
    domino_core
)

set_target_properties(domino_det_trans_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_trans_test COMMAND domino_det_trans_test)

add_executable(domino_det_struct_test
    ../../tests/determinism/det_struct.c
)

target_include_directories(domino_det_struct_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_struct_test
    domino_core
)

set_target_properties(domino_det_struct_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_struct_test COMMAND domino_det_struct_test)

add_executable(domino_det_decor_test
    ../../tests/determinism/det_decor.c
)

target_include_directories(domino_det_decor_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_decor_test
    domino_core
)

set_target_properties(domino_det_decor_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_decor_test COMMAND domino_det_decor_test)

add_executable(domino_det_agents_test
    ../../tests/determinism/det_agents.c
)

target_include_directories(domino_det_agents_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_agents_test
    domino_core
)

set_target_properties(domino_det_agents_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_agents_test COMMAND domino_det_agents_test)

add_executable(domino_det_graph_test
    ../../tests/determinism/det_graph.c
)

target_include_directories(domino_det_graph_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_graph_test
    domino_core
)

set_target_properties(domino_det_graph_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_graph_test COMMAND domino_det_graph_test)

add_executable(domino_det_domains_test
    ../../tests/determinism/det_domains.c
)

target_include_directories(domino_det_domains_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_domains_test
    domino_core
)

set_target_properties(domino_det_domains_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_domains_test COMMAND domino_det_domains_test)

add_executable(domino_det_knowledge_test
    ../../tests/determinism/det_knowledge.c
)

target_include_directories(domino_det_knowledge_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_det_knowledge_test
    domino_core
)

set_target_properties(domino_det_knowledge_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME domino_det_knowledge_test COMMAND domino_det_knowledge_test)

add_executable(dgfx_soft_hash_test
    ../../tests/domino_gfx/test_dgfx_soft_hash.c
    ../../external/xxhash/xxhash.c
)

target_include_directories(dgfx_soft_hash_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../source/domino
    ${CMAKE_CURRENT_SOURCE_DIR}/../../external/xxhash
)

target_link_libraries(dgfx_soft_hash_test
    domino_core
)

set_target_properties(dgfx_soft_hash_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dgfx_soft_hash_test COMMAND dgfx_soft_hash_test)

add_executable(dgfx_conformance_test
    ../../tests/domino_gfx/test_dgfx_conformance.c
)

target_include_directories(dgfx_conformance_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../source/domino
)

target_link_libraries(dgfx_conformance_test
    domino_core
)

set_target_properties(dgfx_conformance_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dgfx_conformance_test COMMAND dgfx_conformance_test)

add_executable(dgfx_caps_contract_test
    ../../tests/domino_gfx/test_dgfx_caps_contract.c
)

target_include_directories(dgfx_caps_contract_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../source/domino
)

target_link_libraries(dgfx_caps_contract_test
    domino_core
)

set_target_properties(dgfx_caps_contract_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dgfx_caps_contract_test COMMAND dgfx_caps_contract_test)

add_executable(dgfx_stall_watchdog_test
    ../../tests/domino_gfx/test_dgfx_stall_watchdog.c
)

target_include_directories(dgfx_stall_watchdog_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../source/domino
)

target_link_libraries(dgfx_stall_watchdog_test
    domino_core
)

set_target_properties(dgfx_stall_watchdog_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dgfx_stall_watchdog_test COMMAND dgfx_stall_watchdog_test)

add_executable(domino_sys_smoke
    domino_sys_smoke.c
)

target_link_libraries(domino_sys_smoke
    domino_core
)

set_target_properties(domino_sys_smoke PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_executable(dsys_input_trace_test
    ../../tests/domino_sys/test_input_trace.c
)

target_include_directories(dsys_input_trace_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../source/domino
)

target_link_libraries(dsys_input_trace_test
    domino_core
)

set_target_properties(dsys_input_trace_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dsys_input_trace_test COMMAND dsys_input_trace_test)

add_executable(domino_dui_smoke
    domino_dui_smoke.c
)

target_include_directories(domino_dui_smoke PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_dui_smoke
    domino_core
)

set_target_properties(domino_dui_smoke PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME domino_dui_smoke_null COMMAND domino_dui_smoke null)
add_test(NAME domino_dui_smoke_dgfx COMMAND domino_dui_smoke dgfx)
if(WIN32)
    add_test(NAME domino_dui_smoke_native COMMAND domino_dui_smoke win32)
endif()

add_executable(dominium_launcher_ui_backend_swap_test
    launcher_ui_backend_swap_test.c
)

target_include_directories(dominium_launcher_ui_backend_swap_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(dominium_launcher_ui_backend_swap_test
    domino_core
)

set_target_properties(dominium_launcher_ui_backend_swap_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

add_test(NAME dominium_launcher_ui_backend_swap_test COMMAND dominium_launcher_ui_backend_swap_test)

if(WIN32)
    add_executable(ui_cli_determinism_test
        ui_cli_determinism_test.cpp
    )

    set_target_properties(ui_cli_determinism_test PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_dependencies(ui_cli_determinism_test dominium-ui-editor)

    set(UI_CLI_TEST_ROOT ${CMAKE_CURRENT_BINARY_DIR}/ui_cli_tests)

    add_test(NAME test_ui_apply_determinism_launcher
        COMMAND ui_cli_determinism_test
            --mode apply_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --script ${CMAKE_SOURCE_DIR}/tools/launcher/ui/scripts/minecraft_launcher_v1.ops.json
            --doc-basename launcher_ui_doc
            --work-dir ${UI_CLI_TEST_ROOT}/launcher_apply
    )

    add_test(NAME test_ui_apply_determinism_setup
        COMMAND ui_cli_determinism_test
            --mode apply_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --script ${CMAKE_SOURCE_DIR}/tools/setup/ui/scripts/minecraft_setup_v1.ops.json
            --doc-basename setup_ui_doc
            --work-dir ${UI_CLI_TEST_ROOT}/setup_apply
    )

    add_test(NAME test_ui_codegen_determinism_launcher
        COMMAND ui_cli_determinism_test
            --mode codegen_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --doc ${CMAKE_SOURCE_DIR}/tools/launcher/ui/doc/launcher_ui_doc.tlv
            --docname launcher_ui
            --work-dir ${UI_CLI_TEST_ROOT}/launcher_codegen
    )

    add_test(NAME test_ui_codegen_determinism_setup
        COMMAND ui_cli_determinism_test
            --mode codegen_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --doc ${CMAKE_SOURCE_DIR}/tools/setup/ui/doc/setup_ui_doc.tlv
            --docname setup_ui
            --work-dir ${UI_CLI_TEST_ROOT}/setup_codegen
    )

    add_test(NAME test_ui_registry_stability
        COMMAND ui_cli_determinism_test
            --mode registry_stability
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --work-dir ${UI_CLI_TEST_ROOT}/registry
    )

    add_test(NAME test_ui_index_determinism
        COMMAND ui_cli_determinism_test
            --mode scan_determinism
            --ui-editor $<TARGET_FILE:dominium-ui-editor>
            --work-dir ${UI_CLI_TEST_ROOT}/scan
    )
    set_tests_properties(test_ui_index_determinism PROPERTIES
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
endif()

add_executable(dgfx_demo
    ../../tests/domino_gfx/dgfx_demo.c
)

target_include_directories(dgfx_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(dgfx_demo
    PRIVATE domino_core
)

if(WIN32 AND DOM_BACKEND_DX9)
    target_link_libraries(dgfx_demo PRIVATE d3d9)
endif()

set_target_properties(dgfx_demo PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

if(WIN32)
    function(setup_copy_winpthread target)
        get_filename_component(DSK_COMPILER_DIR "${CMAKE_CXX_COMPILER}" DIRECTORY)
        set(DSK_RUNTIME_DLLS
            "${DSK_COMPILER_DIR}/libwinpthread-1.dll"
            "${DSK_COMPILER_DIR}/libstdc++-6.dll"
            "${DSK_COMPILER_DIR}/libgcc_s_seh-1.dll"
            "${DSK_COMPILER_DIR}/libgcc_s_dw2-1.dll"
            "${DSK_COMPILER_DIR}/libgcc_s_sjlj-1.dll"
            "${DSK_COMPILER_DIR}/libatomic-1.dll"
        )
        foreach(dll IN LISTS DSK_RUNTIME_DLLS)
            if(EXISTS "${dll}")
                add_custom_command(TARGET ${target} POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${dll}"
                        $<TARGET_FILE_DIR:${target}>
                )
            endif()
        endforeach()
    endfunction()
endif()

add_executable(setup_kernel_tests
    ../../tests/setup/setup_kernel_tests.cpp
)

target_include_directories(setup_kernel_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)

target_link_libraries(setup_kernel_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup_kernel_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_kernel_tests)
if(WIN32)
    setup_copy_winpthread(setup_kernel_tests)
endif()

add_test(NAME test_tlv_roundtrip_known_fields COMMAND setup_kernel_tests tlv_roundtrip_known_fields)
add_test(NAME test_tlv_skip_unknown COMMAND setup_kernel_tests tlv_skip_unknown)
add_test(NAME test_manifest_validate_missing_required COMMAND setup_kernel_tests manifest_validate_missing_required)
add_test(NAME test_request_validate_missing_required COMMAND setup_kernel_tests request_validate_missing_required)
add_test(NAME test_kernel_emits_audit_on_failure COMMAND setup_kernel_tests kernel_emits_audit_on_failure)
add_test(NAME test_splat_selection_deterministic COMMAND setup_kernel_tests splat_selection_deterministic)
add_test(NAME test_state_auto_migration_missing_version COMMAND setup_kernel_tests state_auto_migration_missing_version)
add_test(NAME test_state_skip_unknown_fields COMMAND setup_kernel_tests state_skip_unknown_fields)

add_executable(setup_services_fs_tests
    ../../tests/setup/test_services_fs_sandbox.cpp
)

target_include_directories(setup_services_fs_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup_services_fs_tests
    PRIVATE dss_services
)

target_compile_definitions(setup_services_fs_tests PRIVATE
    SETUP_TESTS_SANDBOX_ROOT=\"${CMAKE_CURRENT_BINARY_DIR}/setup_fs_sandbox\"
)

set_target_properties(setup_services_fs_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_services_fs_tests)
if(WIN32)
    setup_copy_winpthread(setup_services_fs_tests)
endif()

add_test(NAME test_services_fs_rejects_escape
    COMMAND setup_services_fs_tests services_fs_rejects_escape ${CMAKE_CURRENT_BINARY_DIR}/setup_fs_sandbox_escape
)
add_test(NAME test_services_fs_atomic_write
    COMMAND setup_services_fs_tests services_fs_atomic_write ${CMAKE_CURRENT_BINARY_DIR}/setup_fs_sandbox_atomic
)
add_test(NAME test_services_fs_canonicalize
    COMMAND setup_services_fs_tests services_fs_canonicalize ${CMAKE_CURRENT_BINARY_DIR}/setup_fs_sandbox_canon
)

add_executable(setup_services_platform_tests
    ../../tests/setup/test_services_platform_fake.cpp
)

target_include_directories(setup_services_platform_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup_services_platform_tests
    PRIVATE dss_services
)

set_target_properties(setup_services_platform_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_services_platform_tests)
if(WIN32)
    setup_copy_winpthread(setup_services_platform_tests)
endif()

add_test(NAME test_services_platform_fake COMMAND setup_services_platform_tests services_platform_fake)

add_executable(setup_kernel_services_tests
    ../../tests/setup/test_kernel_uses_services_platform.cpp
)

target_include_directories(setup_kernel_services_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup_kernel_services_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup_kernel_services_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_kernel_services_tests)
if(WIN32)
    setup_copy_winpthread(setup_kernel_services_tests)
endif()

add_test(NAME test_kernel_uses_services_platform COMMAND setup_kernel_services_tests kernel_uses_services_platform)

add_executable(setup_splat_tests
    ../../tests/setup/test_splat_selection.cpp
)

target_include_directories(setup_splat_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_link_libraries(setup_splat_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup_splat_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_splat_tests)
if(WIN32)
    setup_copy_winpthread(setup_splat_tests)
endif()

add_test(NAME test_splat_registry_sorted COMMAND setup_splat_tests splat_registry_sorted)
add_test(NAME test_splat_select_requested_id_success COMMAND setup_splat_tests splat_select_requested_id_success)
add_test(NAME test_splat_select_requested_id_not_found COMMAND setup_splat_tests splat_select_requested_id_not_found)
add_test(NAME test_splat_select_requested_id_removed COMMAND setup_splat_tests splat_select_requested_id_removed)
add_test(NAME test_splat_select_filters_by_platform COMMAND setup_splat_tests splat_select_filters_by_platform)
add_test(NAME test_splat_select_filters_by_scope COMMAND setup_splat_tests splat_select_filters_by_scope)
add_test(NAME test_splat_select_filters_by_ui_mode COMMAND setup_splat_tests splat_select_filters_by_ui_mode)
add_test(NAME test_splat_select_no_compatible_emits_rejections_and_audit COMMAND setup_splat_tests splat_select_no_compatible_emits_rejections_and_audit)
add_test(NAME test_splat_select_deterministic_choice_first_compatible COMMAND setup_splat_tests splat_select_deterministic_choice_first_compatible)
add_test(NAME test_splat_select_deprecated_emits_warning COMMAND setup_splat_tests splat_select_deprecated_emits_warning)

add_executable(setup_plan_tests
    ../../tests/setup/test_plan.cpp
)

target_include_directories(setup_plan_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/src/plan
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)

target_compile_definitions(setup_plan_tests PRIVATE
    SETUP_TESTS_SOURCE_DIR=\"${CMAKE_SOURCE_DIR}/tests/setup\"
)

target_link_libraries(setup_plan_tests
    PRIVATE dsk_kernel
)

set_target_properties(setup_plan_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_plan_tests)
if(WIN32)
    setup_copy_winpthread(setup_plan_tests)
endif()

add_test(NAME test_resolve_default_components COMMAND setup_plan_tests resolve_default_components)
add_test(NAME test_resolve_explicit_components COMMAND setup_plan_tests resolve_explicit_components)
add_test(NAME test_resolve_dependency_closure COMMAND setup_plan_tests resolve_dependency_closure)
add_test(NAME test_resolve_conflict_refusal COMMAND setup_plan_tests resolve_conflict_refusal)
add_test(NAME test_resolve_platform_incompat_refusal COMMAND setup_plan_tests resolve_platform_incompat_refusal)
add_test(NAME test_plan_byte_identical_repeat COMMAND setup_plan_tests plan_byte_identical_repeat)
add_test(NAME test_plan_digest_stable COMMAND setup_plan_tests plan_digest_stable)
add_test(NAME test_plan_validate_rejects_corrupt_header COMMAND setup_plan_tests plan_validate_rejects_corrupt_header)
add_test(NAME test_plan_lists_canonically_sorted COMMAND setup_plan_tests plan_lists_canonically_sorted)
add_test(NAME test_plan_golden_default COMMAND setup_plan_tests plan_golden_default)
add_test(NAME test_plan_golden_custom COMMAND setup_plan_tests plan_golden_custom)

add_executable(setup_apply_tests
    ../../tests/setup/test_apply.cpp
)

target_include_directories(setup_apply_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/src/plan
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)

target_compile_definitions(setup_apply_tests PRIVATE
    SETUP_TESTS_SANDBOX_ROOT=\"${CMAKE_CURRENT_BINARY_DIR}/setup_apply_sandbox\"
)

target_link_libraries(setup_apply_tests
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup_apply_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_apply_tests)
if(WIN32)
    setup_copy_winpthread(setup_apply_tests)
endif()

add_test(NAME test_apply_fresh_install_succeeds COMMAND setup_apply_tests apply_fresh_install_succeeds)
add_test(NAME test_fail_mid_commit_then_rollback_restores_pristine COMMAND setup_apply_tests fail_mid_commit_then_rollback_restores_pristine)
add_test(NAME test_fail_mid_commit_then_resume_completes COMMAND setup_apply_tests fail_mid_commit_then_resume_completes)
add_test(NAME test_crash_during_stage_then_resume COMMAND setup_apply_tests crash_during_stage_then_resume)
add_test(NAME test_no_in_place_mutation COMMAND setup_apply_tests no_in_place_mutation)
add_test(NAME test_deterministic_journals COMMAND setup_apply_tests deterministic_journals)

add_executable(setup_cli_golden_tests
    ../../tests/setup/test_cli_golden.cpp
)

add_dependencies(setup_cli_golden_tests
    dominium-setup
)

set_target_properties(setup_cli_golden_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_cli_golden_tests)
if(WIN32)
    setup_copy_winpthread(setup_cli_golden_tests)
endif()

file(RELATIVE_PATH setup_fixtures_rel
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/tests/setup/fixtures
)
file(RELATIVE_PATH setup_golden_rel
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/tests/setup/golden
)
file(RELATIVE_PATH setup_gold_master_rel
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/artifacts/setup/gold_master
)

add_test(NAME setup_cli_golden
    COMMAND setup_cli_golden_tests
        $<TARGET_FILE:dominium-setup>
        ${setup_fixtures_rel}
        ${setup_golden_rel}
        setup_cli_golden
)
set_tests_properties(setup_cli_golden PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

add_executable(setup_import_tests
    ../../tests/setup/test_import_legacy_state.cpp
)
target_include_directories(setup_import_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup_import_tests PRIVATE
    dsk_kernel
)
target_compile_definitions(setup_import_tests PRIVATE
    SETUP_TESTS_SOURCE_DIR=\"${CMAKE_SOURCE_DIR}/tests/setup\"
)
set_target_properties(setup_import_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_import_tests)
if(WIN32)
    setup_copy_winpthread(setup_import_tests)
endif()
add_test(NAME setup_import_legacy_state
    COMMAND setup_import_tests
)

add_executable(setup_adapter_steam_tests
    ../../tests/setup/test_adapter_steam.cpp
)
target_include_directories(setup_adapter_steam_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup_adapter_steam_tests PRIVATE
    dsk_kernel
)
set_target_properties(setup_adapter_steam_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup_adapter_steam_tests
    dominium-setup
    dominium-setup-steam
)
add_test(NAME setup_adapter_steam
    COMMAND setup_adapter_steam_tests
        $<TARGET_FILE:dominium-setup>
        $<TARGET_FILE:dominium-setup-steam>
        adapter_steam
)
set_tests_properties(setup_adapter_steam PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

add_executable(setup_adapter_macos_pkg_tests
    ../../tests/setup/test_adapter_macos_pkg.cpp
)
set_target_properties(setup_adapter_macos_pkg_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup_adapter_macos_pkg
    COMMAND setup_adapter_macos_pkg_tests
        ${CMAKE_SOURCE_DIR}
)
set_tests_properties(setup_adapter_macos_pkg PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

if(APPLE)
    add_executable(setup_adapter_macos_gui_tests
        ../../tests/setup/test_adapter_macos_gui.cpp
    )
    set_target_properties(setup_adapter_macos_gui_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_dependencies(setup_adapter_macos_gui_tests
        dominium-setup-macos-gui
    )
    add_test(NAME setup_adapter_macos_gui_export
        COMMAND setup_adapter_macos_gui_tests
            $<TARGET_FILE:dominium-setup-macos-gui>
            ${CMAKE_SOURCE_DIR}
            ${CMAKE_CURRENT_BINARY_DIR}/setup_adapter_macos_gui
    )
    set_tests_properties(setup_adapter_macos_gui_export PROPERTIES
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    )
endif()

add_executable(setup_adapter_linux_wrappers_tests
    ../../tests/setup/test_adapter_linux_wrappers.cpp
)
set_target_properties(setup_adapter_linux_wrappers_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup_adapter_linux_wrappers
    COMMAND setup_adapter_linux_wrappers_tests
        ${CMAKE_SOURCE_DIR}
)
set_tests_properties(setup_adapter_linux_wrappers PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

add_executable(setup_adapter_wrapper_tests
    ../../tests/setup/test_adapter_wrapper_scripts.cpp
)
set_target_properties(setup_adapter_wrapper_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup_adapter_wrapper_scripts
    COMMAND setup_adapter_wrapper_tests
        ${CMAKE_SOURCE_DIR}
)
set_tests_properties(setup_adapter_wrapper_scripts PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

if(WIN32)
    add_executable(setup_adapter_windows_tests
        ../../tests/setup/test_adapter_windows_exe.cpp
    )
    target_include_directories(setup_adapter_windows_tests PRIVATE
        ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    )
    target_link_libraries(setup_adapter_windows_tests PRIVATE
        dsk_kernel
    )
    set_target_properties(setup_adapter_windows_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_dependencies(setup_adapter_windows_tests
        dominium-setup
        dominium-setup-win-exe
    )
    add_test(NAME setup_adapter_windows_exe
        COMMAND setup_adapter_windows_tests
            $<TARGET_FILE:dominium-setup>
            $<TARGET_FILE:dominium-setup-win-exe>
            adapter_windows
    )
    set_tests_properties(setup_adapter_windows_exe PROPERTIES
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    )
endif()

add_executable(setup_parity_tests
    ../../tests/setup/parity/setup_parity_tests.cpp
)
target_compile_definitions(setup_parity_tests PRIVATE
    SETUP_SOURCE_DIR=\"${CMAKE_SOURCE_DIR}\"
)
set_target_properties(setup_parity_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_parity_tests)
if(WIN32)
    setup_copy_winpthread(setup_parity_tests)
endif()
add_test(NAME setup_parity_kernel_invariants_match_launcher
    COMMAND setup_parity_tests kernel_invariants_match_launcher
)
add_test(NAME setup_parity_capability_registry_semantics_match
    COMMAND setup_parity_tests capability_registry_semantics_match
)
add_test(NAME setup_parity_job_journal_semantics_match
    COMMAND setup_parity_tests job_journal_semantics_match
)

add_executable(setup_parity_lock_tests
    ../../tests/setup/parity_lock/setup_parity_lock_tests.cpp
)
target_include_directories(setup_parity_lock_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup_parity_lock_tests PRIVATE
    dsk_kernel
)
set_target_properties(setup_parity_lock_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_parity_lock_tests)
if(WIN32)
    setup_copy_winpthread(setup_parity_lock_tests)
endif()
add_dependencies(setup_parity_lock_tests
    dominium-setup
    dominium-setup-tui
)
if(TARGET dominium-setup-steam)
    add_dependencies(setup_parity_lock_tests dominium-setup-steam)
    set(SETUP_PARITY_STEAM_BIN $<TARGET_FILE:dominium-setup-steam>)
else()
    set(SETUP_PARITY_STEAM_BIN "none")
endif()
if(WIN32 AND TARGET dominium-setup-win-exe)
    add_dependencies(setup_parity_lock_tests dominium-setup-win-exe)
    set(SETUP_PARITY_WIN_EXE_BIN $<TARGET_FILE:dominium-setup-win-exe>)
else()
    set(SETUP_PARITY_WIN_EXE_BIN "none")
endif()

add_test(NAME setup_parity_lock_request_equivalence_across_adapters
    COMMAND setup_parity_lock_tests request_equivalence_across_adapters
        $<TARGET_FILE:dominium-setup>
        $<TARGET_FILE:dominium-setup-tui>
        ${setup_fixtures_rel}
        ${CMAKE_CURRENT_BINARY_DIR}/setup_parity_lock
        ${CMAKE_SOURCE_DIR}
        ${SETUP_PARITY_STEAM_BIN}
        ${SETUP_PARITY_WIN_EXE_BIN}
)
add_test(NAME setup_parity_lock_plan_digest_equivalence_across_adapters
    COMMAND setup_parity_lock_tests plan_digest_equivalence_across_adapters
        $<TARGET_FILE:dominium-setup>
        $<TARGET_FILE:dominium-setup-tui>
        ${setup_fixtures_rel}
        ${CMAKE_CURRENT_BINARY_DIR}/setup_parity_lock
        ${CMAKE_SOURCE_DIR}
        ${SETUP_PARITY_STEAM_BIN}
        ${SETUP_PARITY_WIN_EXE_BIN}
)
add_test(NAME setup_parity_lock_refusal_code_equivalence
    COMMAND setup_parity_lock_tests refusal_code_equivalence
        $<TARGET_FILE:dominium-setup>
        $<TARGET_FILE:dominium-setup-tui>
        ${setup_fixtures_rel}
        ${CMAKE_CURRENT_BINARY_DIR}/setup_parity_lock
        ${CMAKE_SOURCE_DIR}
        ${SETUP_PARITY_STEAM_BIN}
        ${SETUP_PARITY_WIN_EXE_BIN}
)

add_executable(setup_conformance_runner
    ../../tests/setup/conformance/setup_conformance_runner.cpp
)

target_include_directories(setup_conformance_runner PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/src/plan
)

target_link_libraries(setup_conformance_runner
    PRIVATE dsk_kernel dss_services
)

set_target_properties(setup_conformance_runner PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_conformance_runner)
if(WIN32)
    setup_copy_winpthread(setup_conformance_runner)
endif()

add_test(NAME setup_conformance
    COMMAND setup_conformance_runner
        --sandbox-root setup_conformance
        --fixtures-root ${setup_fixtures_rel}
        --deterministic 1
        --out-json setup_conformance/conformance_summary.json
)

add_test(NAME setup_conformance_golden
    COMMAND ${CMAKE_COMMAND} -E compare_files
        ${CMAKE_CURRENT_BINARY_DIR}/setup_conformance/conformance_summary.json
        ${setup_golden_rel}/conformance_summary.json
)
set_tests_properties(setup_conformance_golden PROPERTIES
    DEPENDS setup_conformance
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

add_executable(setup_conformance_repeat_tests
    ../../tests/setup/conformance/setup_conformance_repeat_tests.cpp
)
set_target_properties(setup_conformance_repeat_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_conformance_repeat_tests)
if(WIN32)
    setup_copy_winpthread(setup_conformance_repeat_tests)
endif()
add_dependencies(setup_conformance_repeat_tests
    setup_conformance_runner
)
add_test(NAME setup_conformance_repeat
    COMMAND setup_conformance_repeat_tests
        $<TARGET_FILE:setup_conformance_runner>
        ${setup_fixtures_rel}
        ${CMAKE_CURRENT_BINARY_DIR}/setup_conformance_repeat
)

add_executable(setup_gold_master_tests
    ../../tests/setup/gold_master/setup_gold_master_tests.cpp
)
target_include_directories(setup_gold_master_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/services/include
)
target_link_libraries(setup_gold_master_tests PRIVATE
    dsk_kernel dss_services
)
set_target_properties(setup_gold_master_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dominium_bundle_runtime(setup_gold_master_tests)
if(WIN32)
    setup_copy_winpthread(setup_gold_master_tests)
endif()
add_dependencies(setup_gold_master_tests
    dominium-setup
)
add_test(NAME setup_gold_master_roundtrip
    COMMAND setup_gold_master_tests roundtrip
        $<TARGET_FILE:dominium-setup>
        ${setup_fixtures_rel}
        ${setup_gold_master_rel}
        ${CMAKE_CURRENT_BINARY_DIR}/setup_gold_master
)
add_test(NAME setup_gold_master_digests_unchanged
    COMMAND setup_gold_master_tests digests
        $<TARGET_FILE:dominium-setup>
        ${setup_fixtures_rel}
        ${setup_gold_master_rel}
        ${CMAKE_CURRENT_BINARY_DIR}/setup_gold_master
)

set(setup_labeled_tests
    test_tlv_roundtrip_known_fields
    test_tlv_skip_unknown
    test_manifest_validate_missing_required
    test_request_validate_missing_required
    test_kernel_emits_audit_on_failure
    test_splat_selection_deterministic
    test_state_auto_migration_missing_version
    test_state_skip_unknown_fields
    test_services_platform_fake
    test_kernel_uses_services_platform
    test_splat_registry_sorted
    test_splat_select_requested_id_success
    test_splat_select_requested_id_not_found
    test_splat_select_requested_id_removed
    test_splat_select_filters_by_platform
    test_splat_select_filters_by_scope
    test_splat_select_filters_by_ui_mode
    test_splat_select_no_compatible_emits_rejections_and_audit
    test_splat_select_deterministic_choice_first_compatible
    test_splat_select_deprecated_emits_warning
    test_resolve_default_components
    test_resolve_explicit_components
    test_resolve_dependency_closure
    test_resolve_conflict_refusal
    test_resolve_platform_incompat_refusal
    test_plan_byte_identical_repeat
    test_plan_digest_stable
    test_plan_validate_rejects_corrupt_header
    test_plan_lists_canonically_sorted
    test_plan_golden_default
    test_plan_golden_custom
    test_apply_fresh_install_succeeds
    test_fail_mid_commit_then_rollback_restores_pristine
    test_fail_mid_commit_then_resume_completes
    test_crash_during_stage_then_resume
    test_no_in_place_mutation
    test_deterministic_journals
    setup_cli_golden
    setup_import_legacy_state
    setup_parity_kernel_invariants_match_launcher
    setup_parity_capability_registry_semantics_match
    setup_parity_job_journal_semantics_match
    setup_parity_lock_request_equivalence_across_adapters
    setup_parity_lock_plan_digest_equivalence_across_adapters
    setup_parity_lock_refusal_code_equivalence
    setup_gold_master_roundtrip
    setup_gold_master_digests_unchanged
    setup_conformance
    setup_conformance_golden
    setup_conformance_repeat
)
set_tests_properties(${setup_labeled_tests} PROPERTIES LABELS setup)

set(setup_adapter_tests
    setup_adapter_steam
    setup_adapter_macos_pkg
    setup_adapter_linux_wrappers
    setup_adapter_wrapper_scripts
)
set_tests_properties(${setup_adapter_tests} PROPERTIES LABELS "setup;setup_adapters")
if(WIN32)
    set_tests_properties(setup_adapter_windows_exe PROPERTIES LABELS "setup;setup_adapters")
endif()
if(APPLE)
    set_tests_properties(setup_adapter_macos_gui_export PROPERTIES LABELS "setup;setup_adapters")
endif()

if(WIN32)
    add_test(NAME setup_kernel_purity_check
        COMMAND ${CMAKE_SOURCE_DIR}/scripts/setup/check_kernel_purity.bat
    )
    set_tests_properties(setup_kernel_purity_check PROPERTIES LABELS setup)
else()
    add_test(NAME setup_kernel_purity_check
        COMMAND sh ${CMAKE_SOURCE_DIR}/scripts/setup/check_kernel_purity.sh
    )
    set_tests_properties(setup_kernel_purity_check PROPERTIES LABELS setup)
endif()

add_executable(dom_tool_handshake_validation_test
    dom_tool_handshake_validation_test.cpp
    ../dominium/tools/dom_tool_runtime.cpp
    ../dominium/game/runtime/dom_game_handshake.cpp
    ../dominium/game/runtime/dom_game_paths.c
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
)

set_source_files_properties(../dominium/game/runtime/dom_game_paths.c
    PROPERTIES LANGUAGE CXX
)

target_include_directories(dom_tool_handshake_validation_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_tool_handshake_validation_test
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_tool_handshake_validation_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_tool_handshake_validation_test COMMAND dom_tool_handshake_validation_test)

add_executable(dom_universe_editor_roundtrip_test
    dom_universe_editor_roundtrip_test.cpp
    ../dominium/tools/universe_editor/ue_commands.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
)

target_include_directories(dom_universe_editor_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_universe_editor_roundtrip_test
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_universe_editor_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_universe_editor_roundtrip_test COMMAND dom_universe_editor_roundtrip_test)

add_executable(dom_validator_invalid_content_test
    dom_validator_invalid_content_test.cpp
    ../dominium/tools/validator/validator_checks.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
)

target_include_directories(dom_validator_invalid_content_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_validator_invalid_content_test
    dominium_tools_common
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_validator_invalid_content_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_validator_invalid_content_test COMMAND dom_validator_invalid_content_test)

add_executable(dom_replay_analyzer_basic_test
    dom_replay_analyzer_basic_test.cpp
    ../dominium/tools/replay_analyzer/ra_parser.cpp
    ../dominium/tools/replay_analyzer/ra_diff.cpp
    ../dominium/game/runtime/dom_game_replay.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_replay_analyzer_basic_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_replay_analyzer_basic_test
    dominium_common
    core_tlv
    domino_core
)

set_target_properties(dom_replay_analyzer_basic_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_replay_analyzer_basic_test COMMAND dom_replay_analyzer_basic_test)

add_executable(coredata_compile_determinism_test
    coredata_compile_determinism_test.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
    ../dominium/tools/coredata_compile/coredata_emit_tlv.cpp
    ../dominium/tools/coredata_compile/coredata_manifest.cpp
)

target_include_directories(coredata_compile_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(coredata_compile_determinism_test
    dominium_common
    core_tlv
    domino_core
)

target_compile_definitions(coredata_compile_determinism_test PRIVATE
    COREDATA_FIXTURE_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/coredata_min\"
)

set_target_properties(coredata_compile_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME coredata_compile_determinism_test COMMAND coredata_compile_determinism_test)

add_executable(coredata_compile_schema_failure_test
    coredata_compile_schema_failure_test.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
)

target_include_directories(coredata_compile_schema_failure_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(coredata_compile_schema_failure_test
    dominium_common
    domino_core
)

target_compile_definitions(coredata_compile_schema_failure_test PRIVATE
    COREDATA_FIXTURE_INVALID_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/coredata_invalid_missing_profile\"
)

set_target_properties(coredata_compile_schema_failure_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME coredata_compile_schema_failure_test COMMAND coredata_compile_schema_failure_test)

add_executable(coredata_validate_valid_passes
    coredata_validate_valid_passes.cpp
    ../dominium/tools/coredata_validate/coredata_validate_load.cpp
    ../dominium/tools/coredata_validate/coredata_validate_checks.cpp
    ../dominium/tools/coredata_validate/coredata_validate_report.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
)

target_include_directories(coredata_validate_valid_passes PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(coredata_validate_valid_passes
    dominium_common
    core_tlv
    domino_core
)

target_compile_definitions(coredata_validate_valid_passes PRIVATE
    COREDATA_FIXTURE_VALID_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/coredata_valid\"
)

set_target_properties(coredata_validate_valid_passes PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME coredata_validate_valid_passes COMMAND coredata_validate_valid_passes)

add_executable(coredata_validate_schema_error_fails
    coredata_validate_schema_error_fails.cpp
    ../dominium/tools/coredata_validate/coredata_validate_load.cpp
    ../dominium/tools/coredata_validate/coredata_validate_checks.cpp
    ../dominium/tools/coredata_validate/coredata_validate_report.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
)

target_include_directories(coredata_validate_schema_error_fails PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(coredata_validate_schema_error_fails
    dominium_common
    core_tlv
    domino_core
)

target_compile_definitions(coredata_validate_schema_error_fails PRIVATE
    COREDATA_FIXTURE_SCHEMA_INVALID_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/coredata_invalid_schema\"
)

set_target_properties(coredata_validate_schema_error_fails PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME coredata_validate_schema_error_fails COMMAND coredata_validate_schema_error_fails)

add_executable(coredata_validate_policy_error_fails
    coredata_validate_policy_error_fails.cpp
    ../dominium/tools/coredata_validate/coredata_validate_load.cpp
    ../dominium/tools/coredata_validate/coredata_validate_checks.cpp
    ../dominium/tools/coredata_validate/coredata_validate_report.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
)

target_include_directories(coredata_validate_policy_error_fails PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(coredata_validate_policy_error_fails
    dominium_common
    core_tlv
    domino_core
)

target_compile_definitions(coredata_validate_policy_error_fails PRIVATE
    COREDATA_FIXTURE_POLICY_INVALID_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/coredata_invalid_candidate_progression\"
)

set_target_properties(coredata_validate_policy_error_fails PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME coredata_validate_policy_error_fails COMMAND coredata_validate_policy_error_fails)

add_executable(coredata_validate_tlv_pack_passes
    coredata_validate_tlv_pack_passes.cpp
    ../dominium/tools/coredata_validate/coredata_validate_load.cpp
    ../dominium/tools/coredata_validate/coredata_validate_checks.cpp
    ../dominium/tools/coredata_validate/coredata_validate_report.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
    ../dominium/tools/coredata_compile/coredata_emit_tlv.cpp
    ../dominium/tools/coredata_compile/coredata_manifest.cpp
)

target_include_directories(coredata_validate_tlv_pack_passes PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(coredata_validate_tlv_pack_passes
    dominium_common
    core_tlv
    domino_core
)

target_compile_definitions(coredata_validate_tlv_pack_passes PRIVATE
    COREDATA_FIXTURE_VALID_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/coredata_valid\"
)

set_target_properties(coredata_validate_tlv_pack_passes PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME coredata_validate_tlv_pack_passes COMMAND coredata_validate_tlv_pack_passes)

add_executable(dominium_coredata_tests
    ../../tests/contract/dominium_coredata_tests.cpp
    ../dominium/game/dom_game_net.cpp
    ../dominium/game/runtime/dom_game_runtime.cpp
    ../dominium/game/runtime/dom_game_handshake.cpp
    ../dominium/game/runtime/dom_game_session.cpp
    ../dominium/game/runtime/dom_game_net_driver.cpp
    ../dominium/game/runtime/dom_game_net_snapshot.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
    ../dominium/game/runtime/dom_universe_bundle.cpp
    ../dominium/tools/coredata_compile/coredata_load.cpp
    ../dominium/tools/coredata_compile/coredata_validate.cpp
    ../dominium/tools/coredata_compile/coredata_emit_tlv.cpp
    ../dominium/tools/coredata_compile/coredata_manifest.cpp
)

target_include_directories(dominium_coredata_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/tools
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_validate
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dominium_coredata_tests PRIVATE
    dominium_common
    core_tlv
    domino_core
    dom_game_runtime_test_support
)

target_compile_definitions(dominium_coredata_tests PRIVATE
    DOMINIUM_TEST_FIXTURES_DIR=\"${CMAKE_SOURCE_DIR}/tests/fixtures\"
)

set_target_properties(dominium_coredata_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if(WIN32)
    target_link_libraries(dominium_coredata_tests PRIVATE ws2_32)
endif()

add_test(NAME dominium_coredata_tests COMMAND dominium_coredata_tests)

add_executable(dom_money_standard_roundtrip_test
    dom_money_standard_roundtrip_test.cpp
    ../dominium/game/runtime/dom_money_standard.cpp
)

target_include_directories(dom_money_standard_roundtrip_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_money_standard_roundtrip_test
    domino_core
)

set_target_properties(dom_money_standard_roundtrip_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_money_standard_roundtrip_test COMMAND dom_money_standard_roundtrip_test)

add_executable(dom_econ_access_control_test
    dom_econ_access_control_test.cpp
    ../dominium/game/runtime/dom_econ_access_control.cpp
)

target_include_directories(dom_econ_access_control_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_econ_access_control_test
    domino_core
)

set_target_properties(dom_econ_access_control_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_econ_access_control_test COMMAND dom_econ_access_control_test)

add_executable(dom_contract_runtime_schedule_test
    dom_contract_runtime_schedule_test.cpp
    ../dominium/game/runtime/dom_contract_templates.cpp
    ../dominium/game/runtime/dom_contract_runtime.cpp
)

target_include_directories(dom_contract_runtime_schedule_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_contract_runtime_schedule_test
    domino_core
)

set_target_properties(dom_contract_runtime_schedule_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_contract_runtime_schedule_test COMMAND dom_contract_runtime_schedule_test)

add_executable(dom_econ_pack_load_test
    dom_econ_pack_load_test.cpp
    ../dominium/game/runtime/dom_econ_pack_load.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_econ_pack_load_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_econ_pack_load_test
    core_tlv
    domino_core
)

set_target_properties(dom_econ_pack_load_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_econ_pack_load_test COMMAND dom_econ_pack_load_test)

add_executable(dom_market_orderbook_determinism_test
    dom_market_orderbook_determinism_test.cpp
    ../dominium/game/runtime/dom_market_registry.cpp
    ../dominium/game/runtime/dom_market_orderbook.cpp
    ../dominium/game/runtime/dom_market_quote_stream.cpp
)

target_include_directories(dom_market_orderbook_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_orderbook_determinism_test
    domino_core
)

set_target_properties(dom_market_orderbook_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_orderbook_determinism_test COMMAND dom_market_orderbook_determinism_test)

add_executable(dom_market_auction_determinism_test
    dom_market_auction_determinism_test.cpp
    ../dominium/game/runtime/dom_market_registry.cpp
    ../dominium/game/runtime/dom_market_auction.cpp
    ../dominium/game/runtime/dom_market_quote_stream.cpp
)

target_include_directories(dom_market_auction_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_auction_determinism_test
    domino_core
)

set_target_properties(dom_market_auction_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_auction_determinism_test COMMAND dom_market_auction_determinism_test)

add_executable(dom_market_barter_determinism_test
    dom_market_barter_determinism_test.cpp
    ../dominium/game/runtime/dom_market_registry.cpp
    ../dominium/game/runtime/dom_market_barter.cpp
    ../dominium/game/runtime/dom_market_quote_stream.cpp
)

target_include_directories(dom_market_barter_determinism_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_barter_determinism_test
    domino_core
)

set_target_properties(dom_market_barter_determinism_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_barter_determinism_test COMMAND dom_market_barter_determinism_test)

add_executable(dom_market_settlement_conservation_test
    dom_market_settlement_conservation_test.cpp
    ../dominium/game/runtime/dom_market_registry.cpp
)

target_include_directories(dom_market_settlement_conservation_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_settlement_conservation_test
    domino_core
)

set_target_properties(dom_market_settlement_conservation_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_settlement_conservation_test COMMAND dom_market_settlement_conservation_test)

add_executable(dom_market_quote_stream_test
    dom_market_quote_stream_test.cpp
    ../dominium/game/runtime/dom_market_quote_stream.cpp
)

target_include_directories(dom_market_quote_stream_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_quote_stream_test
    domino_core
)

set_target_properties(dom_market_quote_stream_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_quote_stream_test COMMAND dom_market_quote_stream_test)

add_executable(dom_market_due_tick_test
    dom_market_due_tick_test.cpp
    ../dominium/game/runtime/dom_market_registry.cpp
    ../dominium/game/runtime/dom_market_orderbook.cpp
    ../dominium/game/runtime/dom_market_quote_stream.cpp
)

target_include_directories(dom_market_due_tick_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_due_tick_test
    domino_core
)

set_target_properties(dom_market_due_tick_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_due_tick_test COMMAND dom_market_due_tick_test)

add_executable(dom_market_batch_equivalence_test
    dom_market_batch_equivalence_test.cpp
    ../dominium/game/runtime/dom_market_registry.cpp
    ../dominium/game/runtime/dom_market_orderbook.cpp
    ../dominium/game/runtime/dom_market_quote_stream.cpp
)

target_include_directories(dom_market_batch_equivalence_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_market_batch_equivalence_test
    domino_core
)

set_target_properties(dom_market_batch_equivalence_test PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_market_batch_equivalence_test COMMAND dom_market_batch_equivalence_test)

add_executable(dom_ui_widgets_tests
    dom_ui_widgets_tests.cpp
    ../dominium/game/ui/dom_ui_widgets.cpp
    ../dominium/game/runtime/dom_belief_store.cpp
    ../dominium/game/runtime/dom_capability_engine.cpp
    ../dominium/game/runtime/dom_time_knowledge.cpp
)

target_include_directories(dom_ui_widgets_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ui_widgets_tests
    domino_core
)

target_compile_definitions(dom_ui_widgets_tests PRIVATE
    UI_FIXTURE_ROOT=\"${CMAKE_SOURCE_DIR}/tests/fixtures/ui\"
)

set_target_properties(dom_ui_widgets_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ui_widgets_tests COMMAND dom_ui_widgets_tests)

add_executable(dom_ui_projection_tests
    dom_ui_projection_tests.cpp
    ../dominium/game/ui/dom_ui_widgets.cpp
    ../dominium/game/ui/dom_ui_projection.cpp
    ../dominium/game/runtime/dom_io_guard.cpp
)

target_include_directories(dom_ui_projection_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${CMAKE_SOURCE_DIR}/source
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)

target_link_libraries(dom_ui_projection_tests
    domino_core
)

set_target_properties(dom_ui_projection_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME dom_ui_projection_tests COMMAND dom_ui_projection_tests)

function(dom_attach_runtime_test_support)
    get_property(dom_all_targets GLOBAL PROPERTY TARGETS)
    foreach(dom_tgt IN LISTS dom_all_targets)
        if(TARGET ${dom_tgt})
            get_target_property(dom_tgt_type ${dom_tgt} TYPE)
            if(dom_tgt_type STREQUAL "EXECUTABLE")
                get_target_property(dom_tgt_sources ${dom_tgt} SOURCES)
                if(dom_tgt_sources)
                    string(TOLOWER "${dom_tgt_sources}" dom_tgt_sources_lower)
                    string(FIND "${dom_tgt_sources_lower}" "dom_game_runtime.cpp" dom_runtime_pos)
                    if(NOT dom_runtime_pos EQUAL -1)
                        get_target_property(dom_skip_support ${dom_tgt} DOM_SKIP_RUNTIME_SUPPORT)
                        if(dom_skip_support)
                            continue()
                        endif()
                        target_link_libraries(${dom_tgt} PRIVATE dom_game_runtime_test_support)
                        target_include_directories(${dom_tgt} PRIVATE
                            ${CMAKE_SOURCE_DIR}/include
                            ${CMAKE_SOURCE_DIR}/source
                            ${CMAKE_SOURCE_DIR}/source/dominium/common
                            ${CMAKE_SOURCE_DIR}/source/dominium/game
                            ${CMAKE_SOURCE_DIR}/source/domino
                        )
                    endif()
                endif()
            endif()
        endif()
    endforeach()
endfunction()

dom_attach_runtime_test_support()

set(dom_runtime_support_tests
    dom_construction_save_load_roundtrip_test
    dom_construction_replay_test
    dom_logistics_save_load_roundtrip_test
    dom_ai_determinism_same_seed_test
    dom_ai_budget_behavior_test
    dom_ai_budget_baseline_cap_test
    dom_ai_persistence_roundtrip_test
    dom_ai_replay_test
    dom_snapshot_isolation_test
    dom_session_authority_tests
    dom_qos_no_sim_effect_test
    dom_qos_overload_test
    dom_orbit_warp_authority_test
    dom_orbit_replay_test
)
foreach(dom_tgt IN LISTS dom_runtime_support_tests)
    if(TARGET ${dom_tgt})
        target_link_libraries(${dom_tgt} PRIVATE dom_game_runtime_test_support)
    endif()
endforeach()

foreach(dom_budget_test IN ITEMS dom_ai_budget_baseline_cap_test dom_ai_budget_behavior_test)
    if(TARGET ${dom_budget_test})
        target_link_libraries(${dom_budget_test} PRIVATE dom_game_runtime_test_support)
        target_include_directories(${dom_budget_test} PRIVATE
            ${CMAKE_SOURCE_DIR}/include
            ${CMAKE_SOURCE_DIR}/source
            ${CMAKE_SOURCE_DIR}/source/dominium/common
            ${CMAKE_SOURCE_DIR}/source/dominium/game
            ${CMAKE_SOURCE_DIR}/source/domino
        )
    endif()
endforeach()

if(TARGET dom_ui_continuity_tests)
    target_include_directories(dom_ui_continuity_tests PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/source
        ${CMAKE_SOURCE_DIR}/source/domino
    )
endif()
