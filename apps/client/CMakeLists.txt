cmake_minimum_required(VERSION 3.16)

add_executable(dominium_client
    main_client.c
    adapters/client_fs_adapter.c
    adapters/client_network_adapter.c
    command/client_command_bridge.c
    command/client_commands_registry.c
    model/client_models_options.c
    model/client_models_server.c
    model/client_models_world.c
    session/client_state_machine.c
    session/session_artifacts.c
    session/session_pipeline.c
    session/session_refusal_codes.c
    session/session_stage_registry.c
    ${CMAKE_SOURCE_DIR}/runtime/input/client/client_input_bindings.c
    modes/client_mode_cli.c
    modes/client_mode_gui.c
    modes/client_mode_tui.c
    observability/readonly_view_model.c
    observability/perceived_model_v1.c
    ${CMAKE_SOURCE_DIR}/runtime/shell/client/client_shell.c
    ${CMAKE_SOURCE_DIR}/runtime/ui/client/client_ui_compositor.c
    presentation/frame_graph_builder.cpp
    presentation/render_prep_system.cpp
    presentation/render_model_adapter_v1.c
    presentation/ui_host_v1.c
)
target_link_libraries(dominium_client PRIVATE
    app::runtime
    domino_engine
    dominium_game
    libs::contracts
)
target_include_directories(dominium_client PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/adapters
    ${CMAKE_CURRENT_SOURCE_DIR}/command
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/runtime/input/client
    ${CMAKE_SOURCE_DIR}/runtime/shell/client
    ${CMAKE_SOURCE_DIR}/runtime/ui/client
    ${CMAKE_CURRENT_SOURCE_DIR}/modes
    ${CMAKE_CURRENT_SOURCE_DIR}/model
    ${CMAKE_CURRENT_SOURCE_DIR}/observability
    ${CMAKE_CURRENT_SOURCE_DIR}/presentation
    ${CMAKE_CURRENT_SOURCE_DIR}/session
)
set_source_files_properties(
    presentation/frame_graph_builder.cpp
    presentation/render_prep_system.cpp
    presentation/render_model_adapter_v1.c
    presentation/ui_host_v1.c
    PROPERTIES COMPILE_DEFINITIONS "DOMINIUM_RENDERER_BOUNDARY=1"
)
set_target_properties(dominium_client PROPERTIES
    OUTPUT_NAME "client"
    LINKER_LANGUAGE CXX
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(dom_client ALIAS dominium_client)
dom_register_product(client dominium_client)

get_target_property(_dom_client_sources dominium_client SOURCES)
if(NOT _dom_client_sources OR _dom_client_sources STREQUAL "SOURCES-NOTFOUND")
    message(FATAL_ERROR "dominium_client source list unavailable for renderer boundary checks.")
endif()
foreach(_dom_src IN LISTS _dom_client_sources)
    if(_dom_src MATCHES "client[/\\\\]presentation[/\\\\]" OR _dom_src MATCHES "presentation[/\\\\]")
        get_source_file_property(_dom_src_defs ${_dom_src} COMPILE_DEFINITIONS)
        if(_dom_src_defs STREQUAL "NOTFOUND")
            set(_dom_src_defs "")
        endif()
        string(FIND "${_dom_src_defs}" "DOMINIUM_RENDERER_BOUNDARY=1" _dom_boundary_idx)
        if(_dom_boundary_idx EQUAL -1)
            message(FATAL_ERROR "Renderer boundary violation: '${_dom_src}' must compile with DOMINIUM_RENDERER_BOUNDARY=1.")
        endif()
    endif()
endforeach()

if(WIN32)
    add_executable(client_app_win32 WIN32
        ${CMAKE_SOURCE_DIR}/runtime/platform/win32/client/client_app_win32.cpp
    )
    target_link_libraries(client_app_win32 PRIVATE
        libs::appcore
        runtime_platform_win32_ui
    )
    set_target_properties(client_app_win32 PROPERTIES
        OUTPUT_NAME "client_app_win32"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    if(TARGET ui_bind_phase)
        add_dependencies(client_app_win32 ui_bind_phase)
    endif()
    if(MSVC)
        target_compile_options(client_app_win32 PRIVATE /W4 /WX)
    endif()
endif()
