cmake_minimum_required(VERSION 3.15)

set(LAUNCHER_CORE_SOURCES
    src/core/launcher_context.cpp
    src/core/launcher_db.cpp
    src/core/launcher_state.cpp
    src/core/launcher_discovery.cpp
)

add_library(dom_launcher_core STATIC
    ${LAUNCHER_CORE_SOURCES}
)

target_include_directories(dom_launcher_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/shared/include
)

target_link_libraries(dom_launcher_core
    PRIVATE
        dom_shared
)
target_compile_features(dom_launcher_core PRIVATE cxx_std_98)

add_executable(dom_launcher
    src/main.cpp
    src/ui/launcher_ui_cli.cpp
    src/ui/launcher_ui_gui.cpp
    src/ui/launcher_ui_tui.cpp
)

target_include_directories(dom_launcher
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/shared/include
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
