enable_testing()

add_executable(domino_sys_probe_tests
    domino_sys/test_platform_probe.c
)
target_link_libraries(domino_sys_probe_tests PRIVATE domino_sys domino_core)
add_test(NAME domino_sys_probe COMMAND domino_sys_probe_tests)

add_executable(domino_sys_dynarray_tests
    domino_sys/test_dynarray.c
)
target_link_libraries(domino_sys_dynarray_tests PRIVATE domino_sys domino_core)
add_test(NAME domino_sys_dynarray COMMAND domino_sys_dynarray_tests)

add_executable(dsys_stub_tests
    domino_sys/test_dsys_stub.c
)
target_link_libraries(dsys_stub_tests PRIVATE domino_sys domino_core)
add_test(NAME dsys_stub COMMAND dsys_stub_tests)

add_executable(domino_gfx_tests
    domino_gfx/test_gfx_soft.c
)
target_link_libraries(domino_gfx_tests PRIVATE domino_gfx domino_sys domino_core)
add_test(NAME domino_gfx_soft COMMAND domino_gfx_tests)

add_executable(domino_core_smoke
    domino_core/test_dom_core_smoke.c
)
target_link_libraries(domino_core_smoke PRIVATE
    -Wl,--start-group
    domino_engine
    dominium_rules
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME domino_core_smoke COMMAND domino_core_smoke)

add_executable(domino_sim_tests test_stub.c)
target_link_libraries(domino_sim_tests PRIVATE domino_sim)
add_test(NAME domino_sim_stub COMMAND domino_sim_tests)

add_executable(domino_mod_tests test_stub.c)
target_link_libraries(domino_mod_tests PRIVATE domino_mod)
add_test(NAME domino_mod_stub COMMAND domino_mod_tests)

add_executable(dominium_integration_tests test_stub.c)
target_link_libraries(dominium_integration_tests PRIVATE
    -Wl,--start-group
    dominium_rules
    domino_engine
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME dominium_integration_stub COMMAND dominium_integration_tests)

add_executable(domino_sim_dominium_tests
    domino_sim/test_domino_dominium_sim.c
)
target_link_libraries(domino_sim_dominium_tests PRIVATE
    -Wl,--start-group
    domino_engine
    dominium_rules
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME domino_sim_dominium COMMAND domino_sim_dominium_tests)

add_executable(domino_lod_framework_tests
    domino_sim/test_dg_lod_framework.c
)
target_link_libraries(domino_lod_framework_tests PRIVATE domino_core)
add_test(NAME domino_lod_framework COMMAND domino_lod_framework_tests)

add_executable(domino_pose_anchor_tests
    domino_sim/test_dg_pose_anchor_quant.c
)
target_link_libraries(domino_pose_anchor_tests PRIVATE domino_core)
add_test(NAME domino_pose_anchor COMMAND domino_pose_anchor_tests)

add_executable(domino_domains_frames_prop_tests
    domino_sim/test_dg_domains_frames_prop.c
)
target_link_libraries(domino_domains_frames_prop_tests PRIVATE domino_core)
add_test(NAME domino_domains_frames_prop COMMAND domino_domains_frames_prop_tests)

add_executable(domino_trans_compile_tests
    domino_trans/test_dg_trans_compile_determinism.c
)
target_link_libraries(domino_trans_compile_tests PRIVATE domino_core)
add_test(NAME domino_trans_compile COMMAND domino_trans_compile_tests)

add_executable(domino_struct_compile_tests
    domino_struct/test_dg_struct_compile_determinism.c
)
target_link_libraries(domino_struct_compile_tests PRIVATE domino_core)
add_test(NAME domino_struct_compile COMMAND domino_struct_compile_tests)

add_executable(domino_decor_compile_tests
    domino_decor/test_dg_decor_compile_determinism.c
)
target_link_libraries(domino_decor_compile_tests PRIVATE domino_core)
add_test(NAME domino_decor_compile COMMAND domino_decor_compile_tests)

add_executable(domino_canvas_tests
    domino_gfx/test_domino_canvas_build.c
)
target_link_libraries(domino_canvas_tests PRIVATE
    -Wl,--start-group
    domino_engine
    dominium_rules
    domino_mod
    domino_sim
    domino_core
    domino_gfx
    domino_sys
    -Wl,--end-group
)
add_test(NAME domino_canvas_build COMMAND domino_canvas_tests)

if(DOMINO_USE_X11_BACKEND)
    add_executable(dsys_x11_tests
        domino_sys/test_dsys_x11.c
    )
    target_link_libraries(dsys_x11_tests PRIVATE domino_engine)
    if(TARGET X11::X11)
        target_link_libraries(dsys_x11_tests PRIVATE X11::X11)
    elseif(X11_LIBRARIES)
        target_link_libraries(dsys_x11_tests PRIVATE ${X11_LIBRARIES})
    endif()
    add_test(NAME dsys_x11 COMMAND dsys_x11_tests)
endif()

if(DOMINO_USE_POSIX_BACKEND)
    add_executable(dsys_posix_tests
        domino_sys/test_dsys_posix.c
    )
    target_link_libraries(dsys_posix_tests PRIVATE domino_engine)
    add_test(NAME dsys_posix COMMAND dsys_posix_tests)
endif()

add_executable(dominium_contract_tests
    contract/dominium_contract_tests.cpp
)
target_include_directories(dominium_contract_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/launcher/core/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_compile_definitions(dominium_contract_tests PRIVATE
    DOM_TLV_VECTORS_DIR="${CMAKE_SOURCE_DIR}/tests/vectors/tlv"
)
target_link_libraries(dominium_contract_tests PRIVATE
    dominium_launcher_core
    launcher_services_impl_null
    dsk_kernel
    core_job
    core_tlv_schema
)
set_target_properties(dominium_contract_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_contract_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_contract_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_contract_schema_vectors COMMAND dominium_contract_tests schema_vectors)
add_test(NAME dominium_contract_installed_state COMMAND dominium_contract_tests installed_state_contract)
add_test(NAME dominium_contract_handshake COMMAND dominium_contract_tests handshake_contract)
add_test(NAME dominium_contract_pack_resolver COMMAND dominium_contract_tests pack_resolver_contract)
add_test(NAME dominium_contract_selection_audit COMMAND dominium_contract_tests selection_audit_contract)
add_test(NAME dominium_contract_job_journal COMMAND dominium_contract_tests job_journal_contract)

add_executable(dominium_tlv_fuzz_tests
    contract/dominium_tlv_fuzz_tests.cpp
)
target_include_directories(dominium_tlv_fuzz_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/launcher/core/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_compile_definitions(dominium_tlv_fuzz_tests PRIVATE
    DOM_TLV_VECTORS_DIR="${CMAKE_SOURCE_DIR}/tests/vectors/tlv"
)
target_link_libraries(dominium_tlv_fuzz_tests PRIVATE
    dominium_launcher_core
    dsk_kernel
    core_job
    core_tlv_schema
)
set_target_properties(dominium_tlv_fuzz_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_tlv_fuzz_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_tlv_fuzz_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_tlv_fuzz COMMAND dominium_tlv_fuzz_tests)

add_executable(dominium_fs_contract_tests
    contract/dominium_fs_contract_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_paths.c
)
set_source_files_properties(${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_paths.c PROPERTIES LANGUAGE CXX)
target_include_directories(dominium_fs_contract_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)
target_link_libraries(dominium_fs_contract_tests PRIVATE
    dominium_common
)
set_target_properties(dominium_fs_contract_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_fs_contract_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_fs_contract_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_fs_contract COMMAND dominium_fs_contract_tests)

add_executable(dominium_universe_bundle_tests
    contract/dominium_universe_bundle_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_universe_bundle.cpp
)
target_include_directories(dominium_universe_bundle_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
)
target_link_libraries(dominium_universe_bundle_tests PRIVATE
    dominium_common
    domino_core
)
set_target_properties(dominium_universe_bundle_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_universe_bundle_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_universe_bundle_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_universe_bundle COMMAND dominium_universe_bundle_tests)

add_executable(dominium_macro_tests
    contract/dominium_macro_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_macro_economy.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_macro_events.cpp
)
target_include_directories(dominium_macro_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
)
target_link_libraries(dominium_macro_tests PRIVATE
    dominium_common
)
set_target_properties(dominium_macro_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_macro_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_macro_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_macro COMMAND dominium_macro_tests)

add_executable(dominium_time_knowledge_tests
    contract/dominium_time_knowledge_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_time_knowledge.cpp
)
target_include_directories(dominium_time_knowledge_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/domino
)
target_link_libraries(dominium_time_knowledge_tests PRIVATE
    dominium_common
    domino_core
)
set_target_properties(dominium_time_knowledge_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_time_knowledge_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_time_knowledge_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_time_knowledge COMMAND dominium_time_knowledge_tests)

add_executable(dominium_no_modal_tests
    contract/dominium_no_modal_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_runtime.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_hash.c
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_snapshot.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_derived_jobs.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_io_guard.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_handshake.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_replay.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_net.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_save.cpp
)
target_include_directories(dominium_no_modal_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/domino
)
target_link_libraries(dominium_no_modal_tests PRIVATE
    dominium_common
    core_tlv
    domino_core
)
set_target_properties(dominium_no_modal_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_no_modal_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_no_modal_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
if (WIN32)
    target_link_libraries(dominium_no_modal_tests PRIVATE ws2_32)
endif()
add_test(NAME dominium_no_modal_loading COMMAND dominium_no_modal_tests)

add_executable(dominium_perf_tests
    contract/dominium_perf_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_chunks.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_derived_jobs.cpp
)
target_include_directories(dominium_perf_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/domino
)
target_link_libraries(dominium_perf_tests PRIVATE
    dominium_common
    domino_core
)
set_target_properties(dominium_perf_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_perf_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_perf_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
add_test(NAME dominium_perf COMMAND dominium_perf_tests)

add_executable(dominium_session_tests
    contract/dominium_session_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_runtime.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_hash.c
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_replay.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_net_driver.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_net_snapshot.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_session.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_io_guard.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_net.cpp
)
target_include_directories(dominium_session_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/domino
)
target_link_libraries(dominium_session_tests PRIVATE
    dominium_common
    core_tlv
    domino_core
)
target_compile_definitions(dominium_session_tests PRIVATE
    DOMINIUM_TEST_RUN_ROOT="${CMAKE_SOURCE_DIR}/tmp"
)
set_target_properties(dominium_session_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_session_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_session_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
if (WIN32)
    target_link_libraries(dominium_session_tests PRIVATE ws2_32)
endif()
add_test(NAME dominium_session_roles COMMAND dominium_session_tests)

add_executable(dominium_qos_tests
    contract/dominium_qos_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_runtime.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_hash.c
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_replay.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_qos.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_net.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_save.cpp
)
target_include_directories(dominium_qos_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/domino
)
target_link_libraries(dominium_qos_tests PRIVATE
    dominium_common
    core_tlv
    domino_core
)
set_target_properties(dominium_qos_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_qos_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_qos_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
if (WIN32)
    target_link_libraries(dominium_qos_tests PRIVATE ws2_32)
endif()
add_test(NAME dominium_qos COMMAND dominium_qos_tests)

add_executable(dominium_coredata_tests
    contract/dominium_coredata_tests.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_runtime.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_hash.c
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_replay.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_handshake.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_session.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_net_driver.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_net_snapshot.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_game_save.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_cosmo_graph.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_cosmo_transit.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_mech_profiles.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_macro_economy.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_macro_events.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_faction_registry.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_ai_scheduler.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_ai_planner_logistics.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_ai_planner_events.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_qos.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_derived_jobs.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_io_guard.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_fidelity.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_snapshot.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_universe_bundle.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_media_provider.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_atmos_provider.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_atmos_provider_profile_v1.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_ocean_provider.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_weather_provider.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_vehicle_aero.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_frames.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_lane_scheduler.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_construction_registry.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_station_registry.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_route_graph.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_transfer_scheduler.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_production.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_orbit_lane.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_calendar.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_system_registry.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_body_registry.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_topology.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_height.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_chunks.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_topology_sphere.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_surface_topology_torus.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/runtime/dom_coredata_load.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_net.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/game/dom_game_save.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile/coredata_load.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile/coredata_validate.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile/coredata_emit_tlv.cpp
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile/coredata_manifest.cpp
)
target_include_directories(dominium_coredata_tests PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/source/dominium/game
    ${CMAKE_SOURCE_DIR}/source/dominium/common
    ${CMAKE_SOURCE_DIR}/source/dominium/tools/coredata_compile
    ${CMAKE_SOURCE_DIR}/source/domino
)
target_link_libraries(dominium_coredata_tests PRIVATE
    dominium_common
    core_tlv
    domino_core
)
target_compile_definitions(dominium_coredata_tests PRIVATE
    DOMINIUM_TEST_FIXTURES_DIR="${CMAKE_SOURCE_DIR}/tests/fixtures"
)
set_target_properties(dominium_coredata_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
if (MSVC)
    target_compile_options(dominium_coredata_tests PRIVATE $<$<CONFIG:Release>:/UNDEBUG>)
else()
    target_compile_options(dominium_coredata_tests PRIVATE $<$<CONFIG:Release>:-UNDEBUG>)
endif()
if (WIN32)
    target_link_libraries(dominium_coredata_tests PRIVATE ws2_32)
endif()
add_test(NAME dominium_coredata COMMAND dominium_coredata_tests)

add_executable(domino_spacetime_tests
    determinism/test_spacetime_conversions.c
)
target_link_libraries(domino_spacetime_tests PRIVATE domino_core)
add_test(NAME domino_spacetime_conversions COMMAND domino_spacetime_tests)

add_executable(dominium_interest_tests
    interest/dom_interest_tests.c
)
target_link_libraries(dominium_interest_tests PRIVATE dominium_game)
set_target_properties(dominium_interest_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME dominium_interest COMMAND dominium_interest_tests)

add_executable(dominium_fidelity_tests
    fidelity/dom_fidelity_tests.c
)
target_link_libraries(dominium_fidelity_tests PRIVATE dominium_game)
set_target_properties(dominium_fidelity_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME dominium_fidelity COMMAND dominium_fidelity_tests)

add_executable(dominium_epistemic_tests
    epistemic/dom_epistemic_tests.c
)
target_link_libraries(dominium_epistemic_tests PRIVATE dominium_game)
set_target_properties(dominium_epistemic_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME dominium_epistemic COMMAND dominium_epistemic_tests)

add_executable(dominium_life_continuation_tests
    life/dom_life_continuation_tests.cpp
)
target_link_libraries(dominium_life_continuation_tests PRIVATE dominium_game)
set_target_properties(dominium_life_continuation_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_continuation COMMAND dominium_life_continuation_tests)

add_executable(dominium_life_death_tests
    life/dom_life_death_pipeline_tests.cpp
)
target_link_libraries(dominium_life_death_tests PRIVATE dominium_game)
set_target_properties(dominium_life_death_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_death COMMAND dominium_life_death_tests)

add_executable(dominium_life_birth_tests
    life/dom_life_birth_tests.cpp
)
target_link_libraries(dominium_life_birth_tests PRIVATE dominium_game)
set_target_properties(dominium_life_birth_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_birth COMMAND dominium_life_birth_tests)

add_executable(dominium_civ0a_survival_tests
    civ0a/dom_civ0a_survival_tests.cpp
)
target_link_libraries(dominium_civ0a_survival_tests PRIVATE dominium_game)
set_target_properties(dominium_civ0a_survival_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ0a_survival COMMAND dominium_civ0a_survival_tests)

add_executable(dominium_life_remains_tests
    life/dom_life_remains_salvage_tests.cpp
)
target_link_libraries(dominium_life_remains_tests PRIVATE dominium_game)
set_target_properties(dominium_life_remains_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_remains COMMAND dominium_life_remains_tests)

set(_dom_epis_try_script "${CMAKE_CURRENT_BINARY_DIR}/epistemic_ui_bypass_trycompile.cmake")
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/epistemic/epistemic_ui_bypass_trycompile.cmake.in
    ${_dom_epis_try_script}
    @ONLY
)
add_test(NAME dominium_epistemic_ui_bypass
    COMMAND ${CMAKE_COMMAND} -P ${_dom_epis_try_script}
)

add_test(NAME dominium_game_headless_flow
    COMMAND $<TARGET_FILE:dominium_game>
        --mode=headless
        --auto-host
        --headless-ticks=10
        --headless-local=1
        --dev-allow-ad-hoc-paths=1
        --dev-allow-missing-content=1
        --instance=headless_smoke
)

add_test(NAME dominium_layer_checks
    COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_SOURCE_DIR} python scripts/check_layers.py
)

add_subdirectory(setup)
