cmake_minimum_required(VERSION 3.15)

set(DOM_SETUP_SOURCES
    src/main.cpp
    src/install.cpp
    src/repair.cpp
    src/uninstall.cpp
    src/list_info.cpp
    src/paths.cpp
    src/install_manifest.cpp
    src/fs.cpp
)

add_library(dom_setup_lib STATIC
    src/install.cpp
    src/repair.cpp
    src/uninstall.cpp
    src/list_info.cpp
    src/paths.cpp
    src/install_manifest.cpp
    src/fs.cpp
)

target_include_directories(dom_setup_lib
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(dom_setup
    src/main.cpp
)

target_link_libraries(dom_setup
    PRIVATE
        dom_setup_lib
)

target_include_directories(dom_setup
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)
