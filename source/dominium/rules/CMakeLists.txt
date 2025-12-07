add_library(dominium_rules STATIC rules_stub.c)
target_include_directories(dominium_rules
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(dominium_rules PUBLIC domino_sys domino_sim domino_mod)
