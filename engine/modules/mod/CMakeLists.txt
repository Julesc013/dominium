set(DOMINO_MOD_SOURCES
    host/mod_stub.c
    domino_semver.c
    package_registry.c
    manifest_io.c
    instance.c
)

add_library(domino_mod STATIC ${DOMINO_MOD_SOURCES})
target_include_directories(domino_mod
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(domino_mod PUBLIC domino_core domino_sys domino_sim)
