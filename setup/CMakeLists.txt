cmake_minimum_required(VERSION 3.16)

add_library(setup_core STATIC
    core/dsk_setup_core.c
)
target_include_directories(setup_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
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
add_executable(setup::cli ALIAS setup_cli)
add_executable(setup::gui ALIAS setup_gui)
add_executable(setup::tui ALIAS setup_tui)
