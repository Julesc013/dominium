cmake_minimum_required(VERSION 3.15)

set(DOM_SETUP_CORE_SOURCES
    core/setup_run_install.cpp
    core/setup_run_repair.cpp
    core/setup_run_uninstall.cpp
    core/setup_run_info.cpp
    core/setup_paths.cpp
    core/setup_registration.cpp
    core/setup_plugins.cpp
)

add_library(dom_setup_core STATIC
    ${DOM_SETUP_CORE_SOURCES}
)

target_include_directories(dom_setup_core
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/include/dom_priv/dom_setup
        ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_link_libraries(dom_setup_core
    PUBLIC
        dom_shared
)

target_compile_features(dom_setup_core PRIVATE cxx_std_98)

add_executable(dom_setup
    cli/setup_main.cpp
    cli/setup_cli.cpp
)

target_link_libraries(dom_setup
    PRIVATE
        dom_setup_core
)

target_include_directories(dom_setup
    PRIVATE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_SOURCE_DIR}/include/dom_priv/dom_setup
        ${CMAKE_CURRENT_SOURCE_DIR}
)

if(MINGW)
    target_link_options(dom_setup PRIVATE -static -static-libstdc++ -static-libgcc -Wl,-Bstatic -lwinpthread -Wl,-Bdynamic)
    dom_copy_mingw_runtime(dom_setup)
endif()
