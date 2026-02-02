cmake_minimum_required(VERSION 3.16)

add_library(setup_core STATIC
    core/dsk_setup_core.c
)
target_include_directories(setup_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_include_directories(setup_core PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
)
target_link_libraries(setup_core
    PUBLIC
        libs::contracts
)
set_target_properties(setup_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(setup::setup ALIAS setup_core)

add_executable(setup_cli
    cli/setup_cli_main.c
)
target_link_libraries(setup_cli PRIVATE setup::setup)
target_link_libraries(setup_cli PRIVATE app::runtime)
target_include_directories(setup_cli PRIVATE
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(setup_cli PROPERTIES
    OUTPUT_NAME "setup"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(setup_gui
    gui/dsu_gui_stub.c
)
target_link_libraries(setup_gui PRIVATE setup::setup)
set_target_properties(setup_gui PROPERTIES
    OUTPUT_NAME "setup_gui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
if(WIN32)
    add_executable(setup_app_win32 WIN32
        gui/setup_app_win32.cpp
    )
    target_link_libraries(setup_app_win32 PRIVATE
        libs::appcore
        shared_ui::win32
    )
    set_target_properties(setup_app_win32 PROPERTIES
        OUTPUT_NAME "setup_app_win32"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    if(TARGET ui_bind_phase)
        add_dependencies(setup_app_win32 ui_bind_phase)
    endif()
    if(MSVC)
        target_compile_options(setup_app_win32 PRIVATE /W4 /WX)
    endif()
endif()
add_executable(setup_tui
    tui/dsu_tui_stub.c
)
target_link_libraries(setup_tui PRIVATE setup::setup)
set_target_properties(setup_tui PROPERTIES
    OUTPUT_NAME "setup_tui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(dom_setup ALIAS setup_cli)
dom_register_product(setup setup_cli)
add_executable(setup::cli ALIAS setup_cli)
add_executable(setup::gui ALIAS setup_gui)
add_executable(setup::tui ALIAS setup_tui)
