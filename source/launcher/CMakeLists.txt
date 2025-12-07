cmake_minimum_required(VERSION 3.15)

set(LAUNCHER_CORE_SOURCES
    core/launcher_context.cpp
    core/launcher_db.cpp
    core/launcher_state.cpp
    core/launcher_discovery.cpp
    core/launcher_logging.cpp
    core/launcher_process.cpp
    core/launcher_plugins.cpp
)

add_library(dom_launcher_core STATIC
    ${LAUNCHER_CORE_SOURCES}
)

target_include_directories(dom_launcher_core
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/include/dom_priv/launcher_internal
        ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_link_libraries(dom_launcher_core
    PRIVATE
        dom_shared
)
target_compile_features(dom_launcher_core PRIVATE cxx_std_98)

add_executable(dom_launcher
    core/launcher_main.cpp
    cli/launcher_ui_cli.cpp
    gui/launcher_ui_gui.cpp
    tui/launcher_ui_tui.cpp
)

target_include_directories(dom_launcher
    PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/include/dom_priv/launcher_internal
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dom_launcher
    PRIVATE
        dom_launcher_core
        dom_shared
)

if(MINGW)
    target_link_options(dom_launcher PRIVATE -static -static-libstdc++ -static-libgcc -Wl,-Bstatic -lwinpthread -Wl,-Bdynamic)
    dom_copy_mingw_runtime(dom_launcher)
endif()

target_compile_features(dom_launcher PRIVATE cxx_std_98)
