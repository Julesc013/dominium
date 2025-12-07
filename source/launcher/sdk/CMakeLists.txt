cmake_minimum_required(VERSION 3.15)

# Placeholder for launcher extension SDK bindings (script/native).
add_library(dom_launcher_sdk INTERFACE)
target_include_directories(dom_launcher_sdk
    INTERFACE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

# TODO: expose stable C API for launcher extensions.
