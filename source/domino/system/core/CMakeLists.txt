cmake_minimum_required(VERSION 3.15)

# ----------------------------------------------------------------------
# Core low-level (deterministic + fixed-point)
# ----------------------------------------------------------------------
set(DOM_CORE_DOM_SOURCES
    base/dom_core/dom_core_types.c
    base/dom_core/dom_core_err.c
    base/dom_core/dom_core_id.c
    base/dom_core/dom_core_log.c
    base/dom_core/dom_core_mem.c
    base/dom_core/dom_core_fp.c
    base/dom_core/dom_core_rng.c
    base/dom_core/dom_core_bits.c
    base/dom_core/dom_core_version.c
    base/dom_log.c
)

add_library(dom_core STATIC ${DOM_CORE_DOM_SOURCES})
target_include_directories(dom_core
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/base
        ${CMAKE_CURRENT_SOURCE_DIR}/base/dom_core
        ${CMAKE_CURRENT_SOURCE_DIR}/math
)

# ----------------------------------------------------------------------
# Shared C++ utilities used by launcher/setup/tools
# ----------------------------------------------------------------------
add_library(dom_shared STATIC
    base/shared/os_paths.cpp
    base/shared/json.cpp
    base/shared/logging.cpp
    base/shared/uuid.cpp
    base/shared/manifest_install.cpp
    base/shared/process.cpp
)

target_include_directories(dom_shared
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

target_compile_features(dom_shared PRIVATE cxx_std_98)

# ----------------------------------------------------------------------
# Deterministic engine core (simulation + serialization)
# ----------------------------------------------------------------------
set(DOM_ENGINE_SOURCES
    engine_api.c
    base/core_rng.c
    serialize/save_tlv.c
    serialize/save_region.c
    serialize/save_universe.c
    sim/ecs.c
    sim/sim_world.c
    sim/sim_systems.c
    sim/world_addr.c
    sim/world_chunk.c
    sim/world_surface.c
    sim/world_geom.c
    sim/world_fields.c
    sim/registry_material.c
    sim/registry_volume.c
    sim/registry_recipe.c
)

add_library(dom_engine STATIC ${DOM_ENGINE_SOURCES})
target_include_directories(dom_engine
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/base
        ${CMAKE_CURRENT_SOURCE_DIR}/base/dom_core
        ${CMAKE_CURRENT_SOURCE_DIR}/math
        ${CMAKE_CURRENT_SOURCE_DIR}/serialize
        ${CMAKE_CURRENT_SOURCE_DIR}/sim
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)
target_link_libraries(dom_engine
    PUBLIC
        dom_core
)

# ----------------------------------------------------------------------
# New-style simulation experiments (kept building to avoid bit-rot)
# ----------------------------------------------------------------------
add_library(dom_sim STATIC
    sim/dom_sim_ecs.c
    sim/dom_sim_events.c
    sim/dom_sim_jobs.c
    sim/dom_sim_tick.c
    sim/dom_sim_time.c
    sim/dom_sim_world.c
)

target_include_directories(dom_sim
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/sim
        ${CMAKE_CURRENT_SOURCE_DIR}/base
        ${CMAKE_CURRENT_SOURCE_DIR}/base/dom_core
        ${CMAKE_CURRENT_SOURCE_DIR}/math
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)
target_link_libraries(dom_sim PUBLIC dom_core)

# Runtime mode helper
add_library(dom_app_mode STATIC app_mode/app_mode.c)
target_include_directories(dom_app_mode PUBLIC
    ${CMAKE_SOURCE_DIR}/include
)
target_link_libraries(dom_app_mode PUBLIC dom_core)

# ----------------------------------------------------------------------
# Audio + UI stubs
# ----------------------------------------------------------------------
add_library(dom_audio STATIC audio/dom_audio_api.c)
target_include_directories(dom_audio
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/audio
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

add_library(dom_ui STATIC ui/dom_ui_core.c)
target_include_directories(dom_ui
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/ui
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)


#
#
#

# Modding scaffold placeholder; real loaders/sandboxes to be wired in later.
add_library(dom_modding INTERFACE)
target_include_directories(dom_modding
    INTERFACE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

# TODO: split into package/data/script/native/sandbox libs when implementations land.
