cmake_minimum_required(VERSION 3.15)

add_library(dom_sim STATIC
    dom_sim_tick.c
    dom_sim_time.c
    dom_sim_world.c
    dom_sim_ecs.c
    dom_sim_events.c
    dom_sim_jobs.c
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
