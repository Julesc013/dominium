cmake_minimum_required(VERSION 3.16)

add_executable(dominium_client
    app/main_client.c
    adapters/client_fs_adapter.c
    adapters/client_network_adapter.c
    core/client_command_bridge.c
    core/client_commands_registry.c
    core/client_models_options.c
    core/client_models_server.c
    core/client_models_world.c
    core/client_state_machine.c
    input/client_input_bindings.c
    modes/client_mode_cli.c
    modes/client_mode_gui.c
    modes/client_mode_tui.c
    observability/readonly_view_model.c
    shell/client_shell.c
    ui/client_ui_compositor.c
    presentation/frame_graph_builder.cpp
    presentation/render_prep_system.cpp
)
target_link_libraries(dominium_client PRIVATE
    app::runtime
    domino_engine
    dominium_game
    libs::contracts
)
target_include_directories(dominium_client PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/adapters
    ${CMAKE_CURRENT_SOURCE_DIR}/core
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/input
    ${CMAKE_CURRENT_SOURCE_DIR}/modes
    ${CMAKE_CURRENT_SOURCE_DIR}/observability
    ${CMAKE_CURRENT_SOURCE_DIR}/shell
    ${CMAKE_CURRENT_SOURCE_DIR}/ui
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

if(WIN32)
    add_executable(client_app_win32 WIN32
        gui/client_app_win32.cpp
    )
    target_link_libraries(client_app_win32 PRIVATE
        libs::appcore
        shared_ui::win32
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
