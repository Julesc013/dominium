cmake_minimum_required(VERSION 3.15)

set(DOM_SETUP_SOURCES
    src/main.cpp
    src/setup_cli.cpp
    src/setup_run_install.cpp
    src/setup_run_repair.cpp
    src/setup_run_uninstall.cpp
    src/setup_run_info.cpp
    src/setup_paths.cpp
    src/setup_registration.cpp
    src/setup_plugins.cpp
)

add_executable(dom_setup
    ${DOM_SETUP_SOURCES}
)

target_include_directories(dom_setup
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/shared/include
)

target_link_libraries(dom_setup
    PRIVATE
        dom_shared
)

target_compile_features(dom_setup PRIVATE cxx_std_98)
