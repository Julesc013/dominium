cmake_minimum_required(VERSION 3.15)

set(_dom_engine_sources
    core_rng.c
    world_addr.c
    world_chunk.c
    world_surface.c
    world_geom.c
    world_fields.c
    registry_material.c
    registry_volume.c
    registry_recipe.c
    ecs.c
    sim_world.c
    sim_systems.c
    save_tlv.c
    save_region.c
    save_universe.c
    engine_api.c
    core/dom_core_version.c
)

add_library(dom_engine STATIC ${_dom_engine_sources})
target_include_directories(dom_engine PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)
