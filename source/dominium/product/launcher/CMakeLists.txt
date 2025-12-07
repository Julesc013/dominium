add_executable(dominium_launcher
    core/launcher_stub.c
)

target_include_directories(dominium_launcher
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal
)

target_link_libraries(dominium_launcher
    PRIVATE
        domino_sys
        domino_sim
        domino_mod
        dominium_rules
)
