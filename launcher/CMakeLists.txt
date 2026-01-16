cmake_minimum_required(VERSION 3.16)

add_library(launcher_core STATIC
    core/launcher_core.c
    core/launcher_config_stub.c
    core/launcher_profile_stub.c
    core/launcher_mods_stub.c
    core/launcher_process_stub.c
)
target_include_directories(launcher_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(launcher_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(launcher::launcher ALIAS launcher_core)

add_executable(launcher_cli
    cli/launcher_cli_main.c
)
target_link_libraries(launcher_cli PRIVATE launcher::launcher)
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
add_executable(launcher_tui
    tui/launcher_tui_stub.c
)
set_target_properties(launcher_tui PROPERTIES
    OUTPUT_NAME "launcher_tui"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(launcher::cli ALIAS launcher_cli)
add_library(launcher::gui ALIAS launcher_gui)
add_library(launcher::tui ALIAS launcher_tui)
