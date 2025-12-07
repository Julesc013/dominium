set(DOMINO_SYS_SOURCES
    core/sys_stub.c
)

add_library(domino_sys STATIC ${DOMINO_SYS_SOURCES})
target_include_directories(domino_sys
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
