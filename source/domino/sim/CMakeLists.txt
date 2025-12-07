set(DOMINO_SIM_SOURCES
    api/engine_api.c
    api/sim_stub.c
    replay/serialize/save_region.c
    replay/serialize/save_tlv.c
    replay/serialize/save_universe.c
)

add_library(domino_sim STATIC ${DOMINO_SIM_SOURCES})
target_include_directories(domino_sim
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/api
        ${CMAKE_CURRENT_SOURCE_DIR}/replay/serialize
        ${CMAKE_CURRENT_SOURCE_DIR}/_legacy/core_sim
        ${CMAKE_CURRENT_SOURCE_DIR}/../system/core/base
        ${CMAKE_CURRENT_SOURCE_DIR}/../system/core/base/dom_core
        ${CMAKE_CURRENT_SOURCE_DIR}/../system/core/math
)
target_link_libraries(domino_sim PUBLIC domino_sys domino_gfx)
target_compile_features(domino_sim PRIVATE c_std_90)
