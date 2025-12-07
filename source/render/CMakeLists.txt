cmake_minimum_required(VERSION 3.15)

# Minimal renderer abstraction (software-only baseline).
add_library(dom_rend STATIC
    dom_rend_stub.c
)

target_include_directories(dom_rend
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
)
