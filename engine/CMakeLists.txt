cmake_minimum_required(VERSION 3.16)

set(ENGINE_CORE_SOURCES
    ${CMAKE_SOURCE_DIR}/game/domain/agent/dg_agent.c
    ${CMAKE_SOURCE_DIR}/game/domain/agent/dg_agent_comp.c
    ${CMAKE_SOURCE_DIR}/game/domain/ai/d_agent.c
    ${CMAKE_SOURCE_DIR}/game/domain/build/d_build.c
    ${CMAKE_SOURCE_DIR}/game/domain/build/d_build_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/economy/d_econ_metrics.c
    ${CMAKE_SOURCE_DIR}/game/domain/economy/d_econ_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/environment/d_env.c
    ${CMAKE_SOURCE_DIR}/game/domain/environment/d_env_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/environment/d_env_volume.c
    ${CMAKE_SOURCE_DIR}/game/domain/hydrology/d_hydro.c
    ${CMAKE_SOURCE_DIR}/game/domain/hydrology/d_hydro_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/job/d_job.c
    ${CMAKE_SOURCE_DIR}/game/domain/job/d_job_planner.c
    ${CMAKE_SOURCE_DIR}/game/domain/job/d_job_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/mobility/vehicle/d_vehicle.c
    ${CMAKE_SOURCE_DIR}/game/domain/mobility/vehicle/d_vehicle_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/research/d_research_state.c
    ${CMAKE_SOURCE_DIR}/game/domain/research/d_research_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/d_res.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/d_res_model_strata.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/d_res_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/dg_data_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/dg_tlv_canon.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/dg_tlv_schema.c
    ${CMAKE_SOURCE_DIR}/game/domain/resource/dg_tlv_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/scale/d_macro_capsule_store.c
    ${CMAKE_SOURCE_DIR}/game/domain/scale/d_macro_capsule_subsys.c
    ${CMAKE_SOURCE_DIR}/game/domain/scale/d_macro_event_queue_store.c
    ${CMAKE_SOURCE_DIR}/game/domain/scale/d_macro_event_queue_subsys.c
    ${CMAKE_SOURCE_DIR}/game/domain/scale/d_macro_schedule_store.c
    ${CMAKE_SOURCE_DIR}/game/domain/scale/d_macro_schedule_subsys.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/act/dg_action.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/act/dg_action_registry.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/act/dg_capability.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/act/dg_delta_buffer.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/act/dg_delta_commit.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/act/dg_delta_registry.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/d_sim.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/d_sim_hash.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/d_sim_process.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/dg_dirtyset.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/dg_due_sched.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/dg_rebuild.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/dg_rebuild_work.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_accum.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_interest.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_lod_index.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_promo.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_rep.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_representable.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod/dg_stride.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt/dg_pkt_common.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt/idmap/dg_idmap.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt/pkt_hash.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt/registry/dg_type_registry.c
    ${CMAKE_SOURCE_DIR}/game/domain/simulation/sim.c
    ${CMAKE_SOURCE_DIR}/game/domain/structure/d_struct.c
    ${CMAKE_SOURCE_DIR}/game/domain/structure/d_struct_blueprint.c
    ${CMAKE_SOURCE_DIR}/game/domain/structure/d_struct_instance.c
    ${CMAKE_SOURCE_DIR}/game/domain/structure/d_struct_validate.c
    ${CMAKE_SOURCE_DIR}/game/domain/systems/ups/d_ups.c
    ${CMAKE_SOURCE_DIR}/game/domain/transport/d_trans.c
    ${CMAKE_SOURCE_DIR}/game/domain/transport/d_trans_validate.c
    ${CMAKE_SOURCE_DIR}/game/rule/policy/d_policy.c
    ${CMAKE_SOURCE_DIR}/game/rule/policy/d_policy_validate.c
    ${CMAKE_SOURCE_DIR}/game/world/animal_agents.cpp
    ${CMAKE_SOURCE_DIR}/game/world/autonomy_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/climate_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/conflict_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/crafting_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/d_litho.c
    ${CMAKE_SOURCE_DIR}/game/world/d_litho_validate.c
    ${CMAKE_SOURCE_DIR}/game/world/d_serialize.c
    ${CMAKE_SOURCE_DIR}/game/world/d_world.c
    ${CMAKE_SOURCE_DIR}/game/world/d_world_terrain.c
    ${CMAKE_SOURCE_DIR}/game/world/d_worldgen.c
    ${CMAKE_SOURCE_DIR}/game/world/domain_cache.cpp
    ${CMAKE_SOURCE_DIR}/game/world/domain_query.cpp
    ${CMAKE_SOURCE_DIR}/game/world/domain_streaming_hints.cpp
    ${CMAKE_SOURCE_DIR}/game/world/domain_tile.cpp
    ${CMAKE_SOURCE_DIR}/game/world/domain_volume.cpp
    ${CMAKE_SOURCE_DIR}/game/world/economy_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/energy_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/fluid_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/frame/d_world_frame.c
    ${CMAKE_SOURCE_DIR}/game/world/frame/dg_anchor.c
    ${CMAKE_SOURCE_DIR}/game/world/frame/dg_frame.c
    ${CMAKE_SOURCE_DIR}/game/world/frame/dg_frame_eval.c
    ${CMAKE_SOURCE_DIR}/game/world/frame/dg_frame_graph.c
    ${CMAKE_SOURCE_DIR}/game/world/geology_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/hazard_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/heat_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/history_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/information_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/institution_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/knowledge_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/mining_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/risk_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/srz_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/standard_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/structure_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/terrain_mesh.cpp
    ${CMAKE_SOURCE_DIR}/game/world/terrain_surface.cpp
    ${CMAKE_SOURCE_DIR}/game/world/travel_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/trust_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/vegetation_fields.cpp
    ${CMAKE_SOURCE_DIR}/game/world/weather_fields.cpp
    ${CMAKE_SOURCE_DIR}/runtime/audio/audio.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/compatibility/capability_set.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/compatibility/compat_core.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/compatibility/compat_modes.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/compatibility/fixed_debug.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/d_caps.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/d_caps_builtin.c
    ${CMAKE_SOURCE_DIR}/runtime/capability/d_caps_export.c
    ${CMAKE_SOURCE_DIR}/runtime/input/ime.c
    ${CMAKE_SOURCE_DIR}/runtime/input/input.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net_apply.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net_cmd.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net_proto.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net_schema.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net_session.c
    ${CMAKE_SOURCE_DIR}/runtime/network/d_net_transport.c
    ${CMAKE_SOURCE_DIR}/runtime/package/content/d_blueprint.c
    ${CMAKE_SOURCE_DIR}/runtime/package/content/d_content.c
    ${CMAKE_SOURCE_DIR}/runtime/package/content/d_content_schema.c
    ${CMAKE_SOURCE_DIR}/runtime/package/content/d_content_validate.c
    ${CMAKE_SOURCE_DIR}/runtime/package/mod/domino_semver.c
    ${CMAKE_SOURCE_DIR}/runtime/package/mod/instance.c
    ${CMAKE_SOURCE_DIR}/runtime/package/mod/manifest_io.c
    ${CMAKE_SOURCE_DIR}/runtime/package/mod/package_registry.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/sys_caps.cpp
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/thread_pool.cpp
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/work_steal_deque.cpp
    ${CMAKE_SOURCE_DIR}/runtime/storage/io/dtlv.c
    ${CMAKE_SOURCE_DIR}/runtime/storage/io/schema_registry.c
    ${CMAKE_SOURCE_DIR}/runtime/ui/service/d_ui.c
    ${CMAKE_SOURCE_DIR}/runtime/ui/service/ui.c
    ${CMAKE_SOURCE_DIR}/runtime/ui/tui/tui.c
    ${CMAKE_SOURCE_DIR}/runtime/ui/view/d_view.c
    execution/budget_model.cpp
    execution/budgets/dg_budget.c
    execution/execution_context.cpp
    execution/execution_policy.cpp
    execution/ir/access_set.cpp
    execution/ir/cost_model.cpp
    execution/ir/dg_work_item.c
    execution/ir/dg_work_queue.c
    execution/ir/task_graph.cpp
    execution/ir/task_node.cpp
    execution/kernel_iface.c
    execution/kernels/gpu/gpu_caps.cpp
    execution/kernels/gpu/gpu_kernels.cpp
    execution/kernels/kernel_dispatch.cpp
    execution/kernels/kernel_policy.cpp
    execution/kernels/kernel_registry.cpp
    execution/kernels/kernel_selector.cpp
    execution/kernels/scalar/op_ids.cpp
    execution/kernels/scalar/scalar_kernels.cpp
    execution/kernels/simd/simd_caps.cpp
    execution/kernels/simd/simd_kernels.cpp
    execution/scheduler/dg_phase.c
    execution/scheduler/dg_sched.c
    execution/scheduler/dg_sched_hash.c
    execution/scheduler/dg_sched_replay.c
    execution/scheduler/scheduler_iface.cpp
    execution/scheduler/scheduler_parallel.cpp
    execution/scheduler/scheduler_single_thread.cpp
    replay/d_replay.c
    state/ecs/component_view.cpp
    state/ecs/delta_codec.cpp
    state/ecs/ecs_archetype_id.c
    state/ecs/entity_range.cpp
    state/ecs/packed_view.cpp
    state/ecs/soa_archetype_storage.cpp
    state/ecs/storage_iface.cpp
    state/ecs/visibility_mask.cpp
    state/state.c
)

set(ENGINE_CORE_LEGACY_SOURCES
    kernel/core.c
    kernel/d_account.c
    kernel/d_container_state.c
    kernel/d_model.c
    kernel/d_org.c
    kernel/d_org_validate.c
    kernel/d_registry.c
    kernel/d_subsystem.c
    kernel/d_subsystems_init.c
    kernel/d_tlv_kv.c
    kernel/d_tlv_schema.c
    kernel/det_order.c
    kernel/det_reduce.c
    kernel/dg_det_hash.c
    kernel/dg_order_key.c
    kernel/dg_pose.c
    kernel/dg_quant.c
    kernel/dom_build_info.c
    kernel/dom_control.c
    kernel/dom_deterministic_math.c
    kernel/dom_ledger_accounts.c
    kernel/dom_ledger_aggregate.c
    kernel/dom_ledger_core.c
    kernel/dom_ledger_events.c
    kernel/dom_ledger_lots.c
    kernel/dom_ledger_transactions.c
    kernel/dom_registry.c
    kernel/dom_sim.c
    kernel/dom_time_astronomy.c
    kernel/dom_time_core.c
    kernel/dom_time_events.c
    kernel/dom_time_frames.c
    kernel/event.c
    kernel/fixed.c
    kernel/fixed_math.c
    kernel/fs_util.c
    kernel/inst.c
    kernel/mod_loader.c
    kernel/model_table.c
    kernel/model_tree.c
    kernel/pkg.c
    kernel/process_guard.c
    kernel/rng.c
    kernel/rng_model.c
    kernel/rng_streams.c
    kernel/spacetime.c
    kernel/types.c
    kernel/view.c
    state/graph/dg_graph.c
    state/graph/dg_graph_adj.c
    state/graph/dg_graph_iter.c
    state/graph/dg_graph_registry.c
    state/graph/dg_graph_sort.c
    state/graph/part/dg_graph_boundary.c
    state/graph/part/dg_graph_part.c
)

set(ENGINE_RENDER_SOURCES
    ${CMAKE_SOURCE_DIR}/runtime/render/backend_detect.c
    ${CMAKE_SOURCE_DIR}/runtime/render/d_gfx.c
    ${CMAKE_SOURCE_DIR}/runtime/render/d_gfx_caps_stub.c
    ${CMAKE_SOURCE_DIR}/runtime/render/dgfx_trace.c
    ${CMAKE_SOURCE_DIR}/runtime/render/null/d_gfx_null.c
    ${CMAKE_SOURCE_DIR}/runtime/render/software/d_gfx_soft.c
    ${CMAKE_SOURCE_DIR}/runtime/render/null/d_gfx_stub.c
)

set(ENGINE_SYSTEM_SOURCES
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/d_system.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/d_system_input.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_dir_sorted.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_guard.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_perf.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_platform_stub.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_posix.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_sdl2_stub.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_stub.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_term.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_terminal_detect_stub.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_win32_headless.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_window_stub.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/input/input_trace.c
    ${CMAKE_SOURCE_DIR}/runtime/platform/system/sys.c
)
if(WIN32)
    list(APPEND ENGINE_SYSTEM_SOURCES
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_proc_winnt.c
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_terminal_detect_winnt.c
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_window_winnt.c
    )
else()
    list(APPEND ENGINE_SYSTEM_SOURCES
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_proc_stub.c
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/dsys_terminal_detect_posix.c
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
        ${DOMINIUM_GAME_INCLUDE_DIR}
        ${DOMINIUM_RUNTIME_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/execution
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/budgets
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/ir
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/kernels/gpu
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/kernels
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/kernels/scalar
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/kernels/simd
        ${CMAKE_CURRENT_SOURCE_DIR}/execution/scheduler
        ${CMAKE_CURRENT_SOURCE_DIR}/kernel
        ${CMAKE_CURRENT_SOURCE_DIR}/replay
        ${CMAKE_CURRENT_SOURCE_DIR}/state/ecs
        ${CMAKE_CURRENT_SOURCE_DIR}/state/graph
        ${CMAKE_CURRENT_SOURCE_DIR}/state/graph/part
        ${CMAKE_CURRENT_SOURCE_DIR}/state
        ${CMAKE_SOURCE_DIR}/game/domain/agent
        ${CMAKE_SOURCE_DIR}/game/domain/ai
        ${CMAKE_SOURCE_DIR}/game/domain/build
        ${CMAKE_SOURCE_DIR}/game/domain/decor
        ${CMAKE_SOURCE_DIR}/game/domain/economy
        ${CMAKE_SOURCE_DIR}/game/domain/environment
        ${CMAKE_SOURCE_DIR}/game/domain/hydrology
        ${CMAKE_SOURCE_DIR}/game/domain/job
        ${CMAKE_SOURCE_DIR}/game/domain/mobility/vehicle
        ${CMAKE_SOURCE_DIR}/game/domain/research
        ${CMAKE_SOURCE_DIR}/game/domain/resource
        ${CMAKE_SOURCE_DIR}/game/domain/scale
        ${CMAKE_SOURCE_DIR}/game/domain/simulation
        ${CMAKE_SOURCE_DIR}/game/domain/simulation/act
        ${CMAKE_SOURCE_DIR}/game/domain/simulation/lod
        ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt
        ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt/idmap
        ${CMAKE_SOURCE_DIR}/game/domain/simulation/pkt/registry
        ${CMAKE_SOURCE_DIR}/game/domain/structure
        ${CMAKE_SOURCE_DIR}/game/domain/systems/ups
        ${CMAKE_SOURCE_DIR}/game/domain/transport
        ${CMAKE_SOURCE_DIR}/game/rule/policy
        ${CMAKE_SOURCE_DIR}/game/world
        ${CMAKE_SOURCE_DIR}/game/world/frame
        ${CMAKE_SOURCE_DIR}/runtime/audio
        ${CMAKE_SOURCE_DIR}/runtime/capability/compatibility
        ${CMAKE_SOURCE_DIR}/runtime/capability
        ${CMAKE_SOURCE_DIR}/runtime/input
        ${CMAKE_SOURCE_DIR}/runtime/network
        ${CMAKE_SOURCE_DIR}/runtime/package/content
        ${CMAKE_SOURCE_DIR}/runtime/package/mod
        ${CMAKE_SOURCE_DIR}/runtime/platform/system
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/input
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/plat/cocoa
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/plat/posix
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/plat/sdl1
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/plat/wayland
        ${CMAKE_SOURCE_DIR}/runtime/platform/system/plat/x11
        ${CMAKE_SOURCE_DIR}/runtime/render
        ${CMAKE_SOURCE_DIR}/runtime/render/null
        ${CMAKE_SOURCE_DIR}/runtime/render/software
        ${CMAKE_SOURCE_DIR}/runtime/storage/io
        ${CMAKE_SOURCE_DIR}/runtime/ui/service
        ${CMAKE_SOURCE_DIR}/runtime/ui/tui
        ${CMAKE_SOURCE_DIR}/runtime/ui/view
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
    C_STANDARD 17
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 17
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
    add_subdirectory(${CMAKE_SOURCE_DIR}/tests/engine ${CMAKE_BINARY_DIR}/tests/engine)
endif()
