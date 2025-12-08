cmake_minimum_required(VERSION 3.16)

set(DOMINO_CORE_SOURCES
    dnumeric.c
    dworld.c
    dfield.c
    daggregate.c
    dorbit.c
    dbody.c
    dspace_env.c
    dspace_graph.c
    dclimate.c
    dweather.c
    dhydro.c
    dbiome.c
    dvehicle.c
    dtransport.c
    dmatter.c
    dnet.c
    denergy.c
    dzone.c
    dactor.c
    dknowledge.c
    djob.c
    deconomy.c
    dsim.c
    dmachine.c
    drecipe.c
    dblueprint.c
    dresearch.c
)

add_library(domino_core STATIC ${DOMINO_CORE_SOURCES})
target_include_directories(domino_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_compile_features(domino_core PRIVATE c_std_90)

# Domino engine stack
add_subdirectory(system)
add_subdirectory(render)
add_subdirectory(sim)
add_subdirectory(mod)

set(DOMINO_ENGINE_SOURCES
    system/sys.c
    render/gfx.c
    audio/audio.c
    ui/ui.c
    input/input.c
    core/core.c
    core/pkg.c
    core/inst.c
    core/sim.c
    core/canvas.c
    core/model_table.c
    core/model_tree.c
    core/view.c
    core/event.c
    core/mod_loader.c
    core/launcher_ext_loader.c
)

add_library(domino_engine STATIC ${DOMINO_ENGINE_SOURCES})
target_include_directories(domino_engine
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_compile_features(domino_engine PRIVATE c_std_90)

install(TARGETS domino_engine
    ARCHIVE DESTINATION lib
)

install(DIRECTORY ${DOMINIUM_INCLUDE_DIR}/domino
    DESTINATION include
)
