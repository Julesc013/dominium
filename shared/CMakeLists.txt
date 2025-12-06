cmake_minimum_required(VERSION 3.15)

add_library(dom_shared STATIC
    src/os_paths.cpp
    src/json.cpp
    src/logging.cpp
    src/uuid.cpp
    src/manifest_install.cpp
    src/process.cpp
)

target_include_directories(dom_shared
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(dom_shared PRIVATE cxx_std_98)
