cmake_minimum_required(VERSION 3.15)

# ----------------------------------------------------------------------
# Client gameplay library (C + deterministic engine API)
# ----------------------------------------------------------------------
add_library(dom_game_client STATIC
    core/client/dom_client_main.c
    core/client/input/dom_input_mapping.c
)

target_include_directories(dom_game_client
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/source/core
        ${CMAKE_SOURCE_DIR}/source/core/base
        ${CMAKE_SOURCE_DIR}/source/core/base/dom_core
        ${CMAKE_SOURCE_DIR}/source/core/math
        ${CMAKE_SOURCE_DIR}/source/core/sim
        ${CMAKE_SOURCE_DIR}/source/render
        ${CMAKE_SOURCE_DIR}/source/render/core
        ${CMAKE_CURRENT_SOURCE_DIR}/core/client
        ${CMAKE_CURRENT_SOURCE_DIR}/core/client/input
)

target_link_libraries(dom_game_client
    PUBLIC
        dom_engine
        dom_core
)

# ----------------------------------------------------------------------
# CLI + server shells
# ----------------------------------------------------------------------
add_executable(dom_cli
    cli/dom_cli_main.cpp
)

target_include_directories(dom_cli
    PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/source/core
        ${CMAKE_SOURCE_DIR}/source/core/base
        ${CMAKE_SOURCE_DIR}/source/core/base/dom_core
        ${CMAKE_SOURCE_DIR}/source/core/math
        ${CMAKE_SOURCE_DIR}/source/core/sim
        ${CMAKE_CURRENT_SOURCE_DIR}/cli
)

target_link_libraries(dom_cli PRIVATE dom_engine dom_core)
target_compile_features(dom_cli PRIVATE cxx_std_98)

add_executable(dom_server
    cli/server/dom_server_main.c
)

target_include_directories(dom_server
    PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/source/core
        ${CMAKE_SOURCE_DIR}/source/core/base
        ${CMAKE_SOURCE_DIR}/source/core/base/dom_core
        ${CMAKE_SOURCE_DIR}/source/core/math
        ${CMAKE_SOURCE_DIR}/source/core/sim
        ${CMAKE_CURRENT_SOURCE_DIR}/cli/server
)

target_link_libraries(dom_server PRIVATE dom_engine dom_core)

# ----------------------------------------------------------------------
# GUI/TUI dispatcher
# ----------------------------------------------------------------------
add_executable(dom_main
    gui/main.cpp
    gui/runtime_app.cpp
    gui/runtime_display.cpp
    gui/runtime_display_cli.cpp
    gui/runtime_display_tui.cpp
    gui/runtime_display_gui.cpp
    gui/runtime_display_headless.cpp
)

target_include_directories(dom_main
    PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/source/core
        ${CMAKE_SOURCE_DIR}/source/core/base
        ${CMAKE_SOURCE_DIR}/source/core/base/dom_core
        ${CMAKE_SOURCE_DIR}/source/core/math
        ${CMAKE_SOURCE_DIR}/source/core/sim
        ${CMAKE_CURRENT_SOURCE_DIR}/gui
)

target_link_libraries(dom_main
    PRIVATE
        dom_engine
        dom_core
)

target_compile_features(dom_main PRIVATE cxx_std_98)

if(MINGW)
    dom_copy_mingw_runtime(dom_cli)
    dom_copy_mingw_runtime(dom_main)
endif()
