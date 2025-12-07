add_executable(dominium_setup_cli
    core/dominium_setup_core.c
    model/dominium_setup_model.c
    cli/dominium_setup_cli.c
    cli/dominium_setup_cli_main.c
)

target_include_directories(dominium_setup_cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/core
        ${CMAKE_CURRENT_SOURCE_DIR}/model
)

target_link_libraries(dominium_setup_cli
    PRIVATE
        domino_sys
        domino_mod
        dominium_product_common
)
