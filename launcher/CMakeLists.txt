cmake_minimum_required(VERSION 3.16)

add_library(launcher_core INTERFACE)
add_library(launcher::launcher ALIAS launcher_core)

add_library(launcher_cli INTERFACE)
add_library(launcher::cli ALIAS launcher_cli)

add_library(launcher_gui INTERFACE)
add_library(launcher::gui ALIAS launcher_gui)

add_library(launcher_tui INTERFACE)
add_library(launcher::tui ALIAS launcher_tui)
