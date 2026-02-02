cmake_minimum_required(VERSION 3.16)

add_executable(dominium_client
    app/main_client.c
    input/client_input_bindings.c
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
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/input
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
