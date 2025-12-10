add_executable(dominium_modcheck
    dominium_modcheck_main.c
)

target_include_directories(dominium_modcheck
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_modcheck
    PRIVATE
        domino_sys
        domino_mod
        dominium_common
        dominium_tools_core
)
