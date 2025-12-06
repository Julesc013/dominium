cmake_minimum_required(VERSION 3.15)

set(DOM_LAUNCHER_SOURCES
    src/main.cpp
    src/launcher_core.cpp
    src/launcher_db.cpp
    src/launcher_discovery.cpp
    src/launcher_logging.cpp
    src/launcher_process.cpp
    src/ui/cli_main.cpp
    src/ui/gui_main.cpp
    src/ui/tui_main.cpp
)

add_library(dom_launcher_lib STATIC
    src/launcher_core.cpp
    src/launcher_db.cpp
    src/launcher_discovery.cpp
    src/launcher_logging.cpp
    src/launcher_process.cpp
)

target_include_directories(dom_launcher_lib
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/setup/include
        ${CMAKE_SOURCE_DIR}/shared/include
)

target_link_libraries(dom_launcher_lib
    PUBLIC dom_shared
)

add_executable(dom_launcher
    src/main.cpp
    src/ui/cli_main.cpp
    src/ui/gui_main.cpp
    src/ui/tui_main.cpp
)

target_include_directories(dom_launcher
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/setup/include
        ${CMAKE_SOURCE_DIR}/shared/include
)

target_link_libraries(dom_launcher
    PRIVATE
        dom_launcher_lib
        dom_shared
)
