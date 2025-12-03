cmake_minimum_required(VERSION 3.15)

add_library(dom_core STATIC
    dom_core_types.c
    dom_core_err.c
    dom_core_id.c
    dom_core_log.c
    dom_core_mem.c
    dom_core_fp.c
    dom_core_rng.c
    dom_core_bits.c
)

target_include_directories(dom_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)
