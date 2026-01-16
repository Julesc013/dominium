cmake_minimum_required(VERSION 3.16)

add_library(setup_core INTERFACE)
target_include_directories(setup_core INTERFACE
    ${DOMINIUM_SETUP_INCLUDE_DIR}
)
add_library(setup::setup ALIAS setup_core)

add_library(setup_cli INTERFACE)
add_library(setup::cli ALIAS setup_cli)

add_library(setup_gui INTERFACE)
add_library(setup::gui ALIAS setup_gui)

add_library(setup_tui INTERFACE)
add_library(setup::tui ALIAS setup_tui)
