add_executable(dominium_setup
    core/setup_stub.c
)

target_include_directories(dominium_setup
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal
        ${DOMINIUM_INCLUDE_DIR}/dominium/_internal/dom_priv
)

target_link_libraries(dominium_setup
    PRIVATE
        domino_sys
        domino_sim
        domino_mod
        dominium_rules
)
