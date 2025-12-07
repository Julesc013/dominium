set(DOMINO_SIM_SOURCES
    api/sim_stub.c
)

add_library(domino_sim STATIC ${DOMINO_SIM_SOURCES})
target_include_directories(domino_sim
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(domino_sim PUBLIC domino_sys domino_gfx)
