cmake_minimum_required(VERSION 3.16)

add_library(domino_core STATIC
    core/types.c
    core/fixed.c
    core/fixed_debug.c
    core/rng.c
    core/d_subsystem.c
    core/d_model.c
    core/d_subsystems_init.c
    core/d_registry.c
    core/d_tlv_schema.c
    core/d_container_state.c
    core/d_account.c
    content/d_blueprint.c
    content/d_content_schema.c
    content/d_content.c
    content/d_content_validate.c
    ai/d_agent.c
    app/startup.c
    cli/cli.c
    tui/tui.c
    render/d_gfx.c
    render/soft/d_gfx_soft.c
    input/input.c
    input/ime.c
    state/state.c
    system/sys.c
    system/d_system.c
    system/d_system_input.c
    system/dsys_term.c
    $<$<BOOL:${WIN32}>:system/dsys_proc_winnt.c>
    $<$<BOOL:${WIN32}>:system/dsys_window_winnt.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_window_stub.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_proc_stub.c>
    pkg/repo.c
    world/d_serialize.c
    world/d_world.c
    world/d_worldgen.c
    world/d_world_terrain.c
    world/d_litho.c
    world/d_litho_validate.c
    res/d_res.c
    res/d_res_validate.c
    res/d_res_model_strata.c
    env/d_env.c
    env/d_env_volume.c
    env/d_env_validate.c
    hydro/d_hydro.c
    hydro/d_hydro_validate.c
    build/d_build.c
    build/d_build_validate.c
    trans/d_trans.c
    trans/d_trans_validate.c
    struct/d_struct.c
    struct/d_struct_instance.c
    struct/d_struct_blueprint.c
    struct/d_struct_validate.c
    vehicle/d_vehicle.c
    vehicle/d_vehicle_validate.c
    job/d_job.c
    job/d_job_planner.c
    job/d_job_validate.c
    net/d_net.c
    replay/d_replay.c
    view/d_view.c
    ui/d_ui.c
    sim/d_sim.c
    sim/d_sim_process.c
    sim/d_sim_hash.c
    sim/sim.c
)

if(WIN32)
    target_sources(domino_core PRIVATE system/dsys_terminal_detect_winnt.c)
elseif(UNIX)
    target_sources(domino_core PRIVATE system/dsys_terminal_detect_posix.c)
else()
    target_sources(domino_core PRIVATE system/dsys_terminal_detect_stub.c)
endif()

target_include_directories(domino_core PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

set_target_properties(domino_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

if(WIN32)
    target_link_libraries(domino_core PRIVATE user32 gdi32)
endif()
