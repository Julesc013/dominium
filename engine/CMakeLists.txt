cmake_minimum_required(VERSION 3.16)

set(ENGINE_CORE_SOURCES
    modules/agent/dg_agent.c
    modules/agent/dg_agent_comp.c
    modules/ai/d_agent.c
    modules/audio/audio.c
    modules/caps/d_caps.c
    modules/caps/d_caps_builtin.c
    modules/caps/d_caps_export.c
    modules/compat/compat_core.c
    modules/content/d_blueprint.c
    modules/content/d_content.c
    modules/content/d_content_schema.c
    modules/content/d_content_validate.c
    modules/econ/d_econ_metrics.c
    modules/econ/d_econ_validate.c
    modules/env/d_env.c
    modules/env/d_env_validate.c
    modules/env/d_env_volume.c
    modules/hydro/d_hydro.c
    modules/hydro/d_hydro_validate.c
    modules/input/ime.c
    modules/input/input.c
    modules/job/d_job.c
    modules/job/d_job_planner.c
    modules/job/d_job_validate.c
    modules/mod/domino_semver.c
    modules/mod/instance.c
    modules/mod/manifest_io.c
    modules/mod/package_registry.c
    modules/net/d_net.c
    modules/net/d_net_apply.c
    modules/net/d_net_cmd.c
    modules/net/d_net_proto.c
    modules/net/d_net_schema.c
    modules/net/d_net_session.c
    modules/net/d_net_transport.c
    modules/policy/d_policy.c
    modules/policy/d_policy_validate.c
    modules/replay/d_replay.c
    modules/res/dg_tlv_canon.c
    modules/res/dg_tlv_schema.c
    modules/res/dg_tlv_validate.c
    modules/res/d_res.c
    modules/res/d_res_model_strata.c
    modules/res/d_res_validate.c
    modules/research/d_research_state.c
    modules/research/d_research_validate.c
    modules/sim/dg_dirtyset.c
    modules/sim/dg_rebuild.c
    modules/sim/dg_rebuild_work.c
    modules/sim/d_sim.c
    modules/sim/d_sim_hash.c
    modules/sim/d_sim_process.c
    modules/sim/sim.c
    modules/state/state.c
    modules/struct/d_struct.c
    modules/struct/d_struct_blueprint.c
    modules/struct/d_struct_instance.c
    modules/struct/d_struct_validate.c
    modules/trans/d_trans.c
    modules/trans/d_trans_validate.c
    modules/tui/tui.c
    modules/ui/d_ui.c
    modules/ui/ui.c
    modules/vehicle/d_vehicle.c
    modules/vehicle/d_vehicle_validate.c
    modules/view/d_view.c
    modules/world/d_litho.c
    modules/world/d_litho_validate.c
    modules/world/d_serialize.c
    modules/world/d_world.c
    modules/world/d_worldgen.c
    modules/world/d_world_terrain.c
)

set(ENGINE_SYSTEM_SOURCES
    modules/system/dsys_stub.c
    modules/system/dsys_term.c
    modules/system/d_system.c
    modules/system/d_system_input.c
    modules/system/sys.c
)
if(WIN32)
    list(APPEND ENGINE_SYSTEM_SOURCES
        modules/system/dsys_proc_winnt.c
        modules/system/dsys_terminal_detect_winnt.c
        modules/system/dsys_window_winnt.c
    )
else()
    list(APPEND ENGINE_SYSTEM_SOURCES
        modules/system/dsys_proc_stub.c
        modules/system/dsys_terminal_detect_posix.c
        modules/system/dsys_window_stub.c
    )
endif()

add_library(engine_domino STATIC
    ${ENGINE_CORE_SOURCES}
    ${ENGINE_SYSTEM_SOURCES}
)

add_custom_target(engine_include_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_includes_sanity.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking include boundaries for engine sources"
)
add_dependencies(engine_domino engine_include_sanity)

target_include_directories(engine_domino
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
        ${DOMINIUM_GENERATED_INCLUDE_DIR}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/agent
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/ai
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/audio
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/caps
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/compat
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/content
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/decor
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/econ
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/env
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/hydro
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/input
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/job
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/mod
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/net
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/policy
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/replay
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/res
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/research
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/sim
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/state
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/struct
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/system
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/trans
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/tui
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/ui
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/vehicle
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/view
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/world
)

target_compile_definitions(engine_domino PUBLIC
    DOMUI_ENABLE_JSON_MIRROR=$<BOOL:${DOMUI_ENABLE_JSON_MIRROR}>
)

set_target_properties(engine_domino PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if(WIN32)
    target_link_libraries(engine_domino PRIVATE user32 gdi32)
else()
    target_link_libraries(engine_domino PRIVATE m)
endif()

add_library(engine::domino ALIAS engine_domino)
add_library(domino_core ALIAS engine_domino)
add_library(domino_engine ALIAS engine_domino)
add_library(domino_gfx ALIAS engine_domino)
add_library(domino_sys ALIAS engine_domino)
add_library(domino_sim ALIAS engine_domino)
add_library(domino_mod ALIAS engine_domino)

if(DOM_BUILD_TESTS)
    add_subdirectory(tests)
endif()
