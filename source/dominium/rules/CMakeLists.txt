set(DOMINIUM_RULES_SOURCES
    game_api.c
    content_materials.c
    content_parts.c
    content_prefabs.c
    constructions.c
    world.c
    net_power.c
    net_fluid.c
    net_data.c
    actors.c
    environment.c
    economy.c
    rules_stub.c
)

add_library(dominium_rules STATIC ${DOMINIUM_RULES_SOURCES})
target_include_directories(dominium_rules
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
