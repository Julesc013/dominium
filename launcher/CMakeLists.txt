cmake_minimum_required(VERSION 3.16)

add_library(launcher_core STATIC
    core/launcher_core.c
    core/launcher_config_stub.c
    core/launcher_authority.c
    core/launcher_profile_stub.c
    core/launcher_mods_stub.c
    core/launcher_process_stub.c
)
target_include_directories(launcher_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_link_libraries(launcher_core
    PUBLIC
        engine::domino
        libs::contracts
)
set_target_properties(launcher_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(launcher::launcher ALIAS launcher_core)

add_executable(launcher_cli
    cli/launcher_cli_main.c
    cli/launcher_ui_shell.c
)
target_link_libraries(launcher_cli PRIVATE launcher::launcher)
target_link_libraries(launcher_cli PRIVATE app::runtime)
target_include_directories(launcher_cli PRIVATE
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(launcher_cli PROPERTIES
    OUTPUT_NAME "launcher"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(launcher_gui
    gui/launcher_gui_stub.c
)
set_target_properties(launcher_gui PROPERTIES
    OUTPUT_NAME "launcher_gui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
if(WIN32)
    add_executable(launcher_app_win32 WIN32
        gui/launcher_app_win32.cpp
    )
    target_link_libraries(launcher_app_win32 PRIVATE
        libs::appcore
        shared_ui::win32
    )
    set_target_properties(launcher_app_win32 PROPERTIES
        OUTPUT_NAME "launcher_app_win32"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    if(MSVC)
        target_compile_options(launcher_app_win32 PRIVATE /W4 /WX)
    endif()
endif()
add_executable(launcher_tui
    tui/launcher_tui_stub.c
)
set_target_properties(launcher_tui PROPERTIES
    OUTPUT_NAME "launcher_tui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(dom_launcher ALIAS launcher_cli)
dom_register_product(launcher launcher_cli)
add_executable(launcher::cli ALIAS launcher_cli)
add_executable(launcher::gui ALIAS launcher_gui)
add_executable(launcher::tui ALIAS launcher_tui)
