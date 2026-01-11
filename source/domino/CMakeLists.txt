cmake_minimum_required(VERSION 3.16)

add_library(dui_api INTERFACE)
target_include_directories(dui_api INTERFACE
    ${DOMINIUM_INCLUDE_DIR}
)

add_library(dom_shared STATIC
    system/core/base/shared/os_paths.cpp
    system/core/base/shared/json.cpp
    system/core/base/shared/logging.cpp
    system/core/base/shared/uuid.cpp
    system/core/base/shared/manifest_install.cpp
    system/core/base/shared/process.cpp
)

target_include_directories(dom_shared
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include/dominium/_internal/dom_priv
)

target_compile_features(dom_shared PRIVATE cxx_std_98)

set_target_properties(dom_shared PROPERTIES
    OUTPUT_NAME "core_dominium"
)
dist_set_role(dom_shared share)

add_library(domino_core STATIC
    core/types.c
    core/spacetime.c
    core/dom_time_core.c
    core/dom_time_events.c
    core/dom_time_frames.c
    core/dom_time_astronomy.c
    core/dom_build_info.c
    io/container/dtlv.c
    io/schema_registry.c
    core/dg_order_key.c
    core/dg_det_hash.c
    core/dg_pose.c
    core/dg_quant.c
    core/fixed.c
    core/fixed_debug.c
    core/fixed_math.c
    core/dom_deterministic_math.c
    core/rng.c
    core/d_subsystem.c
    core/d_model.c
    core/d_subsystems_init.c
    core/d_registry.c
    core/d_tlv_schema.c
    core/d_container_state.c
    core/d_account.c
    core/d_org.c
    core/d_org_validate.c
    dknowledge.c
    content/d_blueprint.c
    content/d_content_schema.c
    content/d_content.c
    content/d_content_validate.c
    policy/d_policy.c
    policy/d_policy_validate.c
    research/d_research_state.c
    research/d_research_validate.c
    econ/d_econ_metrics.c
    econ/d_econ_validate.c
    ai/d_agent.c
    agent/dg_agent.c
    agent/dg_agent_comp.c
    agent/mind/dg_mind.c
    agent/mind/dg_mind_registry.c
    agent/act/dg_intent_buffer.c
    agent/act/dg_intent_dispatch.c
    agent/group/dg_group.c
    agent/group/dg_group_ctrl.c
    app/startup.c
    cli/cli.c
    tui/tui.c
    render/d_gfx.c
    render/dgfx_trace.c
    render/soft/d_gfx_soft.c
    input/input.c
    input/ime.c
    caps/d_caps.c
    caps/d_caps_export.c
    caps/d_caps_builtin.c
    state/state.c
    system/sys.c
    system/d_system.c
    system/d_system_input.c
    system/input/input_trace.c
    system/dsys_term.c
    $<$<BOOL:${WIN32}>:system/dsys_proc_winnt.c>
    $<$<BOOL:${WIN32}>:system/dsys_window_winnt.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_window_stub.c>
    $<$<NOT:$<BOOL:${WIN32}>>:system/dsys_proc_stub.c>
    mod/domino_semver.c
    pkg/repo.c
    world/d_serialize.c
    world/d_world.c
    world/d_worldgen.c
    world/d_world_terrain.c
    world/d_litho.c
    world/d_litho_validate.c
    world/frame/d_world_frame.c
    world/frame/dg_frame.c
    world/frame/dg_frame_graph.c
    world/frame/dg_frame_eval.c
    world/frame/dg_anchor.c
    world/domain/dg_domain.c
    world/domain/dg_domain_registry.c
    world/domain/dg_domain_query.c
    world/domain/dg_domain_lod.c
    res/d_res.c
    res/d_res_validate.c
    res/dg_tlv_schema.c
    res/dg_tlv_validate.c
    res/dg_tlv_canon.c
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
    trans/model/dg_trans_alignment.c
    trans/model/dg_trans_section.c
    trans/model/dg_trans_attachment.c
    trans/model/dg_trans_junction.c
    trans/compile/dg_trans_compile.c
    trans/compile/dg_trans_microseg.c
    trans/compile/dg_trans_frame.c
    trans/compile/dg_trans_slotmap.c
    trans/compile/dg_trans_dirty.c
    struct/d_struct.c
    struct/d_struct_instance.c
    struct/d_struct_blueprint.c
    struct/d_struct_validate.c
    struct/model/dg_struct_instance.c
    struct/model/dg_struct_footprint.c
    struct/model/dg_struct_volume.c
    struct/model/dg_struct_enclosure.c
    struct/model/dg_struct_surface.c
    struct/model/dg_struct_socket.c
    struct/model/dg_struct_carrier_intent.c
    struct/compile/dg_struct_dirty.c
    struct/compile/dg_struct_occupancy.c
    struct/compile/dg_struct_enclosure_graph.c
    struct/compile/dg_struct_surface_graph.c
    struct/compile/dg_struct_support_graph.c
    struct/compile/dg_struct_carrier_compile.c
    struct/compile/dg_struct_compile.c
    decor/model/dg_decor_host.c
    decor/model/dg_decor_item.c
    decor/model/dg_decor_rulepack.c
    decor/model/dg_decor_override.c
    decor/compile/dg_decor_dirty.c
    decor/compile/dg_decor_instances.c
    decor/compile/dg_decor_tiles.c
    decor/compile/dg_decor_promote.c
    decor/compile/dg_decor_compile.c
    vehicle/d_vehicle.c
    vehicle/d_vehicle_validate.c
    job/d_job.c
    job/d_job_planner.c
    job/d_job_validate.c
    net/d_net.c
    net/d_net_apply.c
    net/d_net_cmd.c
    net/d_net_proto.c
    net/d_net_schema.c
    net/d_net_session.c
    net/d_net_transport.c
    replay/d_replay.c
    view/d_view.c
    ui/d_ui.c
    dui/dui_event_queue.c
    dui/dui_schema_parse.c
    dui/dui_caps.c
    dui/dui_null.c
    dui/dui_dgfx.c
    $<$<BOOL:${WIN32}>:dui/dui_win32.c>
    dui/dui_gtk.c
    dui/dui_macos.c
    sim/d_sim.c
    sim/d_sim_process.c
    sim/d_sim_hash.c
    sim/act/dg_delta_registry.c
    sim/act/dg_delta_buffer.c
    sim/act/dg_delta_commit.c
    sim/act/dg_capability.c
    sim/act/dg_action.c
    sim/act/dg_action_registry.c
    sim/pkt/dg_pkt_common.c
    sim/pkt/pkt_hash.c
    sim/pkt/registry/dg_type_registry.c
    sim/pkt/idmap/dg_idmap.c
    sim/sched/dg_phase.c
    sim/sched/dg_budget.c
    sim/sched/dg_work_item.c
    sim/sched/dg_work_queue.c
    sim/sched/dg_sched_hash.c
    sim/sched/dg_sched_replay.c
    sim/hash/dg_hash.c
    sim/hash/dg_hash_stream.c
    sim/hash/dg_hash_registry.c
    sim/replay/dg_replay.c
    sim/replay/dg_replay_stream.c
    sim/replay/dg_replay_validate.c
    sim/sched/dg_sched.c
    sim/bus/dg_event_bus.c
    sim/bus/dg_message_bus.c
    sim/bus/dg_field_layer.c
    sim/bus/dg_field.c
    sim/lod/dg_rep.c
    sim/lod/dg_representable.c
    sim/lod/dg_stride.c
    sim/lod/dg_accum.c
    sim/lod/dg_lod_index.c
    sim/lod/dg_interest.c
    sim/lod/dg_promo.c
    sim/sense/dg_observation_buffer.c
    sim/sense/dg_sensor.c
    sim/sense/dg_sensor_registry.c
    sim/prop/dg_prop.c
    sim/prop/dg_prop_registry.c
    sim/prop/dg_prop_lod.c
    sim/prop/dg_prop_cache.c
    core/graph/dg_graph.c
    core/graph/dg_graph_adj.c
    core/graph/dg_graph_iter.c
    core/graph/dg_graph_sort.c
    core/graph/dg_graph_registry.c
    core/graph/part/dg_graph_part.c
    core/graph/part/dg_graph_boundary.c
    sim/dg_dirtyset.c
    sim/dg_rebuild_work.c
    sim/dg_rebuild.c
    sim/sim.c
)

# Header-only scaffolding for the deterministic refactor (no compiled logic yet).
target_sources(domino_core PRIVATE
    core/det_invariants.h
    core/dom_deterministic_math.h
    core/dg_order_key.h
    core/dg_det_hash.h
    core/dg_pose.h
    core/dg_quant.h
    core/graph/dg_graph.h
    core/graph/dg_graph_node.h
    core/graph/dg_graph_edge.h
    core/graph/dg_graph_adj.h
    core/graph/dg_graph_iter.h
    core/graph/dg_graph_sort.h
    core/graph/dg_graph_registry.h
    core/graph/part/dg_graph_part.h
    core/graph/part/dg_graph_boundary.h
    agent/dg_agent_ids.h
    agent/dg_agent_comp.h
    agent/dg_agent.h
    agent/mind/dg_mind.h
    agent/mind/dg_mind_registry.h
    agent/act/dg_intent_buffer.h
    agent/act/dg_intent_dispatch.h
    agent/group/dg_group.h
    agent/group/dg_group_ctrl.h
    sim/sched/d_sim_sched.h
    sim/sched/dg_phase.h
    sim/sched/dg_budget.h
    sim/sched/dg_work_item.h
    sim/sched/dg_work_queue.h
    sim/sched/dg_sched_hash.h
    sim/sched/dg_sched_replay.h
    sim/sched/dg_sched.h
    sim/hash/dg_hash.h
    sim/hash/dg_hash_stream.h
    sim/hash/dg_hash_registry.h
    sim/replay/dg_replay.h
    sim/replay/dg_replay_stream.h
    sim/replay/dg_replay_validate.h
    sim/dg_dirtyset.h
    sim/dg_rebuild_work.h
    sim/dg_rebuild.h
    sim/pkt/d_sim_pkt.h
    sim/pkt/dg_pkt_common.h
    sim/pkt/dg_pkt_event.h
    sim/pkt/dg_pkt_message.h
    sim/pkt/dg_pkt_field.h
    sim/pkt/dg_pkt_observation.h
    sim/pkt/dg_pkt_intent.h
    sim/pkt/dg_pkt_delta.h
    sim/pkt/dg_pkt_probe.h
    sim/pkt/pkt_hash.h
    sim/pkt/registry/dg_type_registry.h
    sim/pkt/idmap/dg_idmap.h
    sim/bus/d_sim_bus.h
    sim/bus/dg_event_bus.h
    sim/bus/dg_message_bus.h
    sim/bus/dg_field_layer.h
    sim/bus/dg_field.h
    sim/lod/d_sim_lod.h
    sim/lod/dg_rep.h
    sim/lod/dg_representable.h
    sim/lod/dg_stride.h
    sim/lod/dg_accum.h
    sim/lod/dg_lod_index.h
    sim/lod/dg_interest.h
    sim/lod/dg_promo.h
    sim/act/d_sim_act.h
    sim/act/dg_delta_registry.h
    sim/act/dg_delta_buffer.h
    sim/act/dg_delta_commit.h
    sim/act/dg_capability.h
    sim/act/dg_action.h
    sim/act/dg_action_registry.h
    sim/sense/d_sim_sense.h
    sim/sense/dg_observation_buffer.h
    sim/sense/dg_sensor.h
    sim/sense/dg_sensor_registry.h
    sim/know/d_sim_know.h
    sim/vis/d_sim_vis.h
    sim/prop/d_sim_prop.h
    sim/prop/dg_prop.h
    sim/prop/dg_prop_registry.h
    sim/prop/dg_prop_lod.h
    sim/prop/dg_prop_cache.h
    world/domain/d_world_domain.h
    world/domain/dg_domain.h
    world/domain/dg_domain_registry.h
    world/domain/dg_domain_query.h
    world/domain/dg_domain_lod.h
    world/frame/d_world_frame.h
    world/frame/dg_frame.h
    world/frame/dg_frame_graph.h
    world/frame/dg_frame_eval.h
    world/frame/dg_anchor.h
    trans/compile/d_trans_compile.h
    trans/model/dg_trans_ids.h
    trans/model/dg_trans_alignment.h
    trans/model/dg_trans_section.h
    trans/model/dg_trans_attachment.h
    trans/model/dg_trans_junction.h
    trans/compile/dg_trans_compile.h
    trans/compile/dg_trans_microseg.h
    trans/compile/dg_trans_frame.h
    trans/compile/dg_trans_slotmap.h
    trans/compile/dg_trans_dirty.h
    struct/model/d_struct_model.h
    struct/model/dg_struct_ids.h
    struct/model/dg_struct_instance.h
    struct/model/dg_struct_footprint.h
    struct/model/dg_struct_volume.h
    struct/model/dg_struct_enclosure.h
    struct/model/dg_struct_surface.h
    struct/model/dg_struct_socket.h
    struct/model/dg_struct_carrier_intent.h
    struct/compile/d_struct_compile.h
    struct/compile/dg_struct_compile.h
    struct/compile/dg_struct_occupancy.h
    struct/compile/dg_struct_enclosure_graph.h
    struct/compile/dg_struct_surface_graph.h
    struct/compile/dg_struct_support_graph.h
    struct/compile/dg_struct_carrier_compile.h
    struct/compile/dg_struct_dirty.h
    struct/phys/d_struct_phys.h
    decor/d_decor.h
    decor/model/d_decor_model.h
    decor/compile/d_decor_compile.h
    decor/model/dg_decor_ids.h
    decor/model/dg_decor_host.h
    decor/model/dg_decor_item.h
    decor/model/dg_decor_rulepack.h
    decor/model/dg_decor_override.h
    decor/compile/dg_decor_dirty.h
    decor/compile/dg_decor_instances.h
    decor/compile/dg_decor_tiles.h
    decor/compile/dg_decor_promote.h
    decor/compile/dg_decor_compile.h
    res/dg_tlv_schema.h
    res/dg_tlv_validate.h
    res/dg_tlv_canon.h
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

if(TARGET dom_update_build_number)
    add_dependencies(dom_shared dom_update_build_number)
    add_dependencies(domino_core dom_update_build_number)
endif()

# Platform backend selection (compile exactly one DSYS_BACKEND_*).
string(TOLOWER "${DOM_PLATFORM}" _dom_platform_lc)
if(_dom_platform_lc STREQUAL "null")
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_NULL)
elseif(_dom_platform_lc STREQUAL "win32")
    if(NOT WIN32)
        message(FATAL_ERROR "DOM_PLATFORM=win32 is only supported on WIN32 hosts")
    endif()
    target_sources(domino_core PRIVATE system/plat/win32/win32_sys.c)
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_WIN32)
elseif(_dom_platform_lc STREQUAL "win32_headless")
    if(NOT WIN32)
        message(FATAL_ERROR "DOM_PLATFORM=win32_headless is only supported on WIN32 hosts")
    endif()
    target_sources(domino_core PRIVATE system/plat/win32/win32_sys.c)
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_WIN32_HEADLESS)
elseif(_dom_platform_lc STREQUAL "sdl2")
    set(DOM_SDL2_ROOT "" CACHE PATH "Root path for SDL2 (headers + libraries)")
    if(NOT DOM_SDL2_INCLUDE_DIR)
        find_path(DOM_SDL2_INCLUDE_DIR SDL.h
            PATHS ${DOM_SDL2_ROOT} ENV SDL2_DIR ENV SDL2_PATH
            PATH_SUFFIXES include include/SDL2 SDL2
        )
    endif()
    if(NOT DOM_SDL2_LIBRARY)
        find_library(DOM_SDL2_LIBRARY NAMES SDL2
            PATHS ${DOM_SDL2_ROOT} ENV SDL2_DIR ENV SDL2_PATH
            PATH_SUFFIXES lib lib/x64 lib/x86
        )
    endif()
    if(NOT DOM_SDL2_INCLUDE_DIR OR NOT DOM_SDL2_LIBRARY)
        message(FATAL_ERROR "DOM_PLATFORM=sdl2 requires SDL2 headers and libraries (SDL.h, SDL2)")
    endif()
    target_sources(domino_core PRIVATE system/plat/sdl2/sdl2_sys.c)
    target_include_directories(domino_core PRIVATE ${DOM_SDL2_INCLUDE_DIR})
    target_link_libraries(domino_core PRIVATE ${DOM_SDL2_LIBRARY})
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_SDL2)
elseif(_dom_platform_lc STREQUAL "posix_headless")
    if(NOT UNIX)
        message(FATAL_ERROR "DOM_PLATFORM=posix_headless requires a UNIX host")
    endif()
    target_sources(domino_core PRIVATE system/plat/posix/posix_sys.c)
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_POSIX)
elseif(_dom_platform_lc STREQUAL "posix_x11")
    if(NOT UNIX)
        message(FATAL_ERROR "DOM_PLATFORM=posix_x11 requires a UNIX host with X11 headers + libraries")
    endif()
    find_package(X11 QUIET)
    if(NOT X11_FOUND)
        message(FATAL_ERROR "DOM_PLATFORM=posix_x11 requires X11 development packages (headers + libX11)")
    endif()
    target_sources(domino_core PRIVATE system/plat/x11/x11_sys.c)
    target_include_directories(domino_core PRIVATE ${X11_INCLUDE_DIR})
    target_link_libraries(domino_core PRIVATE ${X11_LIBRARIES})
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_X11)
elseif(_dom_platform_lc STREQUAL "posix_wayland")
    if(NOT UNIX)
        message(FATAL_ERROR "DOM_PLATFORM=posix_wayland requires a UNIX host with Wayland headers + libraries")
    endif()
    find_path(DOM_WAYLAND_INCLUDE_DIR wayland-client.h)
    find_library(DOM_WAYLAND_CLIENT_LIB wayland-client)
    find_path(DOM_WAYLAND_PROTOCOL_INCLUDE_DIR wayland-client-protocol.h)
    find_path(DOM_WAYLAND_XDG_SHELL_INCLUDE_DIR xdg-shell-client-protocol.h)
    if(NOT DOM_WAYLAND_INCLUDE_DIR OR NOT DOM_WAYLAND_CLIENT_LIB OR NOT DOM_WAYLAND_PROTOCOL_INCLUDE_DIR OR NOT DOM_WAYLAND_XDG_SHELL_INCLUDE_DIR)
        message(FATAL_ERROR "DOM_PLATFORM=posix_wayland requires wayland-client headers + libwayland-client and xdg-shell-client-protocol.h (generated protocol headers)")
    endif()
    target_sources(domino_core PRIVATE system/plat/wayland/wayland_sys.c)
    target_include_directories(domino_core PRIVATE
        ${DOM_WAYLAND_INCLUDE_DIR}
        ${DOM_WAYLAND_PROTOCOL_INCLUDE_DIR}
        ${DOM_WAYLAND_XDG_SHELL_INCLUDE_DIR}
    )
    target_link_libraries(domino_core PRIVATE ${DOM_WAYLAND_CLIENT_LIB})
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_WAYLAND)
elseif(_dom_platform_lc STREQUAL "cocoa")
    if(NOT APPLE)
        message(FATAL_ERROR "DOM_PLATFORM=cocoa requires an Apple host (macOS)")
    endif()
    enable_language(OBJC)
    target_sources(domino_core PRIVATE
        system/plat/cocoa/cocoa_sys.c
        system/plat/cocoa/cocoa_sys_objc.m
    )
    target_compile_definitions(domino_core PRIVATE DSYS_BACKEND_COCOA)
    target_link_libraries(domino_core PRIVATE
        "-framework Cocoa"
        "-framework AppKit"
        "-framework Foundation"
    )
else()
    message(FATAL_ERROR "Unsupported DOM_PLATFORM: '${DOM_PLATFORM}'")
endif()

if(DOM_BACKEND_NULL)
    target_sources(domino_core PRIVATE render/null/d_gfx_null.c)
endif()

if(WIN32 AND DOM_BACKEND_DX9)
    target_sources(domino_core PRIVATE render/dx9/d_gfx_dx9.c)
    target_link_libraries(domino_core PRIVATE d3d9)
endif()

if(DOM_BACKEND_DX11)
    if(NOT WIN32)
        message(FATAL_ERROR "DOM_BACKEND_DX11 requires a WIN32 host with Windows SDK libraries (d3d11/dxgi/d3dcompiler)")
    endif()
    find_library(DOM_DX11_D3D11_LIB NAMES d3d11)
    find_library(DOM_DX11_DXGI_LIB NAMES dxgi)
    find_library(DOM_DX11_D3DCOMPILER_LIB NAMES d3dcompiler_47 d3dcompiler)
    if(NOT DOM_DX11_D3D11_LIB OR NOT DOM_DX11_DXGI_LIB OR NOT DOM_DX11_D3DCOMPILER_LIB)
        message(FATAL_ERROR "DOM_BACKEND_DX11=ON requires Windows SDK libraries: d3d11, dxgi, d3dcompiler_47 (or d3dcompiler)")
    endif()
    target_sources(domino_core PRIVATE render/dx11/d_gfx_dx11.c)
    target_link_libraries(domino_core PRIVATE
        ${DOM_DX11_D3D11_LIB}
        ${DOM_DX11_DXGI_LIB}
        ${DOM_DX11_D3DCOMPILER_LIB}
    )
endif()

if(DOM_BACKEND_GL2)
    if(NOT WIN32)
        message(FATAL_ERROR "DOM_BACKEND_GL2 is currently Windows-only (WGL path)")
    endif()
    if(NOT OpenGL_FOUND)
        find_package(OpenGL QUIET)
    endif()
    if(NOT OpenGL_FOUND)
        message(FATAL_ERROR "DOM_BACKEND_GL2=ON requires OpenGL headers and opengl32.lib")
    endif()
    target_sources(domino_core PRIVATE render/gl2/d_gfx_gl2.c)
    if(TARGET OpenGL::GL)
        target_link_libraries(domino_core PRIVATE OpenGL::GL)
    else()
        target_include_directories(domino_core PRIVATE ${OPENGL_INCLUDE_DIR})
        target_link_libraries(domino_core PRIVATE ${OPENGL_gl_LIBRARY})
    endif()
endif()

if(DOM_BACKEND_VK1)
    find_package(Vulkan QUIET)
    if(NOT Vulkan_FOUND)
        message(FATAL_ERROR "DOM_BACKEND_VK1=ON requires Vulkan headers and loader library (find_package(Vulkan))")
    endif()
    target_sources(domino_core PRIVATE render/vk1/d_gfx_vk1.c)
    if(TARGET Vulkan::Vulkan)
        target_link_libraries(domino_core PRIVATE Vulkan::Vulkan)
    else()
        target_include_directories(domino_core PRIVATE ${Vulkan_INCLUDE_DIRS})
        target_link_libraries(domino_core PRIVATE ${Vulkan_LIBRARIES})
    endif()
endif()

if(DOM_BACKEND_METAL)
    if(NOT APPLE)
        message(FATAL_ERROR "DOM_BACKEND_METAL=ON requires an Apple host (macOS)")
    endif()
    enable_language(OBJCXX)
    target_sources(domino_core PRIVATE render/metal/d_gfx_metal.mm)
    target_link_libraries(domino_core PRIVATE
        "-framework Metal"
        "-framework MetalKit"
        "-framework QuartzCore"
        "-framework Foundation"
    )
endif()

set_target_properties(domino_core PROPERTIES
    OUTPUT_NAME "eng_domino"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dist_set_role(domino_core engine)

if(WIN32)
    target_link_libraries(domino_core PRIVATE user32 gdi32 comctl32)
endif()

add_subdirectory(ui_ir)
add_subdirectory(ui_codegen)
