add_executable(dominium_launcher_cli
    core/dominium_launcher_core.c
    core/dominium_launcher_view_registry.c
    core/dominium_launcher_ext_api.c
    model/dominium_launcher_model.c
    services/instances/dominium_launcher_instances.c
    cli/dominium_launcher_cli.c
    cli/dominium_launcher_cli_main.c
)

target_include_directories(dominium_launcher_cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/core
        ${CMAKE_CURRENT_SOURCE_DIR}/model
        ${CMAKE_CURRENT_SOURCE_DIR}/services
        ${CMAKE_CURRENT_SOURCE_DIR}/services/instances
)

target_link_libraries(dominium_launcher_cli
    PRIVATE
        domino_sys
        domino_mod
        dominium_product_common
)
