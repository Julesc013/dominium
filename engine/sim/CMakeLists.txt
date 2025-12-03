cmake_minimum_required(VERSION 3.15)

add_library(dom_sim STATIC
    dom_sim_tick.c
)

target_include_directories(dom_sim
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/engine/core
)

target_link_libraries(dom_sim
    PUBLIC
        dom_core
)
