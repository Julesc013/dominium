cmake_minimum_required(VERSION 3.15)

# Platform aggregation (sys/term/ui).
add_library(dom_platform STATIC
    shared/dom_plat_sys_stub.c
    shared/dom_plat_term_stub.c
    shared/dom_plat_ui_stub.c
)

target_include_directories(dom_platform
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
)
