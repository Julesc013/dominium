cmake_minimum_required(VERSION 3.16)

set(ENGINE_CORE_SOURCES
    modules/agent/dg_agent.c
    modules/agent/dg_agent_comp.c
    modules/ai/d_agent.c
    modules/audio/audio.c
    modules/build/d_build.c
    modules/build/d_build_validate.c
    modules/caps/d_caps.c
    modules/caps/d_caps_builtin.c
    modules/caps/d_caps_export.c
    modules/compat/compat_core.c
    modules/compat/compat_modes.c
    modules/compat/capability_set.c
    modules/compat/fixed_debug.c
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
    modules/io/dtlv.c
    modules/io/schema_registry.c
    modules/job/d_job.c
    modules/job/d_job_planner.c
    modules/job/d_job_validate.c
    modules/mod/domino_semver.c
    modules/mod/instance.c
    modules/mod/manifest_io.c
    modules/mod/package_registry.c
    modules/ups/d_ups.c
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
    modules/res/dg_data_validate.c
    modules/res/d_res.c
    modules/res/d_res_model_strata.c
    modules/res/d_res_validate.c
    modules/research/d_research_state.c
    modules/research/d_research_validate.c
    modules/scale/d_macro_capsule_store.c
    modules/scale/d_macro_capsule_subsys.c
    modules/scale/d_macro_schedule_store.c
    modules/scale/d_macro_schedule_subsys.c
    modules/scale/d_macro_event_queue_store.c
    modules/scale/d_macro_event_queue_subsys.c
    modules/sim/dg_dirtyset.c
    modules/sim/dg_rebuild.c
    modules/sim/dg_rebuild_work.c
    modules/sim/d_sim.c
    modules/sim/d_sim_hash.c
    modules/sim/d_sim_process.c
    modules/sim/sim.c
    modules/sim/dg_due_sched.c
    modules/sim/act/dg_action.c
    modules/sim/act/dg_action_registry.c
    modules/sim/act/dg_capability.c
    modules/sim/act/dg_delta_buffer.c
    modules/sim/act/dg_delta_commit.c
    modules/sim/act/dg_delta_registry.c
    modules/sim/lod/dg_accum.c
    modules/sim/lod/dg_interest.c
    modules/sim/lod/dg_lod_index.c
    modules/sim/lod/dg_promo.c
    modules/sim/lod/dg_rep.c
    modules/sim/lod/dg_representable.c
    modules/sim/lod/dg_stride.c
    modules/sim/pkt/dg_pkt_common.c
    modules/sim/pkt/pkt_hash.c
    modules/sim/pkt/idmap/dg_idmap.c
    modules/sim/pkt/registry/dg_type_registry.c
    modules/execution/budgets/dg_budget.c
    modules/execution/budget_model.cpp
    modules/execution/execution_policy.cpp
    modules/execution/execution_context.cpp
    modules/execution/kernel_iface.c
    modules/execution/ir/access_set.cpp
    modules/execution/ir/cost_model.cpp
    modules/execution/ir/task_graph.cpp
    modules/execution/ir/task_node.cpp
    modules/execution/ir/dg_work_item.c
    modules/execution/ir/dg_work_queue.c
    modules/execution/scheduler/dg_phase.c
    modules/execution/scheduler/dg_sched.c
    modules/execution/scheduler/dg_sched_hash.c
    modules/execution/scheduler/dg_sched_replay.c
    modules/execution/scheduler/scheduler_single_thread.cpp
    modules/execution/scheduler/scheduler_parallel.cpp
    modules/execution/scheduler/scheduler_iface.cpp
    modules/execution/kernels/kernel_registry.cpp
    modules/execution/kernels/kernel_dispatch.cpp
    modules/execution/kernels/kernel_policy.cpp
    modules/execution/kernels/kernel_selector.cpp
    modules/execution/kernels/scalar/op_ids.cpp
    modules/execution/kernels/scalar/scalar_kernels.cpp
    modules/execution/kernels/simd/simd_caps.cpp
    modules/execution/kernels/simd/simd_kernels.cpp
    modules/execution/kernels/gpu/gpu_caps.cpp
    modules/execution/kernels/gpu/gpu_kernels.cpp
    modules/ecs/ecs_archetype_id.c
    modules/ecs/storage_iface.cpp
    modules/ecs/component_view.cpp
    modules/ecs/entity_range.cpp
    modules/ecs/soa_archetype_storage.cpp
    modules/ecs/packed_view.cpp
    modules/ecs/delta_codec.cpp
    modules/ecs/visibility_mask.cpp
    modules/state/state.c
    modules/struct/d_struct.c
    modules/sys/sys_caps.cpp
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
    modules/world/domain_tile.cpp
    modules/world/domain_volume.cpp
    modules/world/domain_query.cpp
    modules/world/domain_cache.cpp
    modules/world/domain_streaming_hints.cpp
    modules/world/terrain_surface.cpp
    modules/world/climate_fields.cpp
    modules/world/weather_fields.cpp
    modules/world/geology_fields.cpp
    modules/world/terrain_mesh.cpp
    modules/world/frame/dg_anchor.c
    modules/world/frame/dg_frame.c
    modules/world/frame/dg_frame_eval.c
    modules/world/frame/dg_frame_graph.c
    modules/world/frame/d_world_frame.c
)

set(ENGINE_CORE_LEGACY_SOURCES
    modules/core/core.c
    modules/core/dg_det_hash.c
    modules/core/dg_order_key.c
    modules/core/dg_pose.c
    modules/core/dg_quant.c
    modules/core/dom_build_info.c
    modules/core/dom_control.c
    modules/core/dom_sim.c
    modules/core/dom_registry.c
    modules/core/dom_deterministic_math.c
    modules/core/dom_ledger_accounts.c
    modules/core/dom_ledger_aggregate.c
    modules/core/dom_ledger_core.c
    modules/core/dom_ledger_events.c
    modules/core/dom_ledger_lots.c
    modules/core/dom_ledger_transactions.c
    modules/core/dom_time_astronomy.c
    modules/core/dom_time_core.c
    modules/core/dom_time_events.c
    modules/core/dom_time_frames.c
    modules/core/det_order.c
    modules/core/det_reduce.c
    modules/core/d_account.c
    modules/core/d_container_state.c
    modules/core/d_model.c
    modules/core/d_org.c
    modules/core/d_org_validate.c
    modules/core/d_registry.c
    modules/core/d_subsystem.c
    modules/core/d_subsystems_init.c
    modules/core/d_tlv_kv.c
    modules/core/d_tlv_schema.c
    modules/core/event.c
    modules/core/fixed.c
    modules/core/fixed_math.c
    modules/core/fs_util.c
    modules/core/inst.c
    modules/core/model_table.c
    modules/core/model_tree.c
    modules/core/mod_loader.c
    modules/core/pkg.c
    modules/core/rng.c
    modules/core/rng_streams.c
    modules/core/rng_model.c
    modules/core/spacetime.c
    modules/core/types.c
    modules/core/view.c
    modules/core/graph/dg_graph.c
    modules/core/graph/dg_graph_adj.c
    modules/core/graph/dg_graph_iter.c
    modules/core/graph/dg_graph_registry.c
    modules/core/graph/dg_graph_sort.c
    modules/core/graph/part/dg_graph_boundary.c
    modules/core/graph/part/dg_graph_part.c
)

set(ENGINE_RENDER_SOURCES
    render/d_gfx.c
    render/dgfx_trace.c
    render/backend_detect.c
    render/soft/d_gfx_soft.c
    render/null/d_gfx_null.c
    render/stub/d_gfx_stub.c
)

set(ENGINE_SYSTEM_SOURCES
    modules/system/dsys_guard.c
    modules/system/dsys_dir_sorted.c
    modules/system/dsys_perf.c
    modules/system/dsys_platform_stub.c
    modules/system/dsys_stub.c
    modules/system/dsys_term.c
    modules/system/dsys_posix.c
    modules/system/dsys_sdl2_stub.c
    modules/system/dsys_win32_headless.c
    modules/system/d_system.c
    modules/system/d_system_input.c
    modules/system/sys.c
    modules/system/input/input_trace.c
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
    )
endif()

add_library(domino_engine STATIC
    ${ENGINE_CORE_SOURCES}
    ${ENGINE_CORE_LEGACY_SOURCES}
    ${ENGINE_SYSTEM_SOURCES}
    ${ENGINE_RENDER_SOURCES}
)

add_custom_target(engine_include_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_includes_sanity.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking include boundaries for engine sources"
)
add_dependencies(domino_engine engine_include_sanity)

target_include_directories(domino_engine
    PUBLIC
        ${DOMINIUM_ENGINE_INCLUDE_DIR}
    PRIVATE
        ${DOMINIUM_GENERATED_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/modules
        ${CMAKE_CURRENT_SOURCE_DIR}/render
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/agent
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/ai
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/audio
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/caps
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/compat
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/content
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/decor
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/econ
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/env
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/execution
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/hydro
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/input
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/job
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/mod
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/net
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/policy
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/replay
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/res
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/research
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/scale
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/sim
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/state
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/struct
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/system
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/trans
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/tui
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/ui
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/ups
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/vehicle
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/view
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/world
)

get_target_property(_dom_engine_iface_includes domino_engine INTERFACE_INCLUDE_DIRECTORIES)
if(NOT _dom_engine_iface_includes OR _dom_engine_iface_includes STREQUAL "INTERFACE_INCLUDE_DIRECTORIES-NOTFOUND")
    message(FATAL_ERROR "domino_engine must expose engine/include as its only public include directory.")
endif()
set(_dom_engine_expected_include "${DOMINIUM_ENGINE_INCLUDE_DIR}")
set(_dom_engine_expected_found FALSE)
foreach(_dom_inc IN LISTS _dom_engine_iface_includes)
    if(_dom_inc MATCHES "engine/modules")
        message(FATAL_ERROR "domino_engine exposes internal engine/modules include path: '${_dom_inc}'.")
    endif()
    if(_dom_inc STREQUAL "${_dom_engine_expected_include}")
        set(_dom_engine_expected_found TRUE)
    else()
        message(FATAL_ERROR "domino_engine exposes non-public include path: '${_dom_inc}'. Only '${_dom_engine_expected_include}' is allowed.")
    endif()
endforeach()
if(NOT _dom_engine_expected_found)
    message(FATAL_ERROR "domino_engine must expose engine/include as its only public include directory.")
endif()

target_compile_definitions(domino_engine PUBLIC
    DOMUI_ENABLE_JSON_MIRROR=$<BOOL:${DOMUI_ENABLE_JSON_MIRROR}>
)

set_target_properties(domino_engine PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

set(DOMINO_SYS_BACKEND "auto" CACHE STRING "System backend (auto|win32|win32_headless|posix_headless|x11|wayland|sdl1|sdl2|cocoa|null)")
set_property(CACHE DOMINO_SYS_BACKEND PROPERTY STRINGS auto win32 win32_headless posix_headless x11 wayland sdl1 sdl2 cocoa null)

if(DOMINO_SYS_BACKEND STREQUAL "auto")
    if(WIN32)
        set(_dom_sys_backend "win32")
    else()
        set(_dom_sys_backend "posix_headless")
    endif()
else()
    set(_dom_sys_backend "${DOMINO_SYS_BACKEND}")
endif()

if(_dom_sys_backend STREQUAL "win32")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_WIN32)
elseif(_dom_sys_backend STREQUAL "win32_headless")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_WIN32_HEADLESS)
elseif(_dom_sys_backend STREQUAL "posix_headless")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_POSIX)
elseif(_dom_sys_backend STREQUAL "x11")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_X11)
elseif(_dom_sys_backend STREQUAL "wayland")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_WAYLAND)
elseif(_dom_sys_backend STREQUAL "sdl1")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_SDL1)
elseif(_dom_sys_backend STREQUAL "sdl2")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_SDL2)
elseif(_dom_sys_backend STREQUAL "cocoa")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_COCOA)
elseif(_dom_sys_backend STREQUAL "null")
    target_compile_definitions(domino_engine PRIVATE DSYS_BACKEND_NULL)
else()
    message(FATAL_ERROR "Unknown DOMINO_SYS_BACKEND: ${DOMINO_SYS_BACKEND}")
endif()

if(WIN32)
    target_link_libraries(domino_engine PRIVATE user32 gdi32)
else()
    target_link_libraries(domino_engine PRIVATE m)
endif()

add_library(engine::domino ALIAS domino_engine)
add_library(engine_domino ALIAS domino_engine)
add_library(domino_core ALIAS domino_engine)
add_library(domino_gfx ALIAS domino_engine)
add_library(domino_sys ALIAS domino_engine)
add_library(domino_sim ALIAS domino_engine)
add_library(domino_mod ALIAS domino_engine)

if(DOM_BUILD_TESTS)
    add_subdirectory(tests)
endif()
