add_library(dominium_launcher_core STATIC
    core/launch_core.c
)

target_include_directories(dominium_launcher_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_launcher_core
    PUBLIC
        domino_engine
        domino_sys
)

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
        dominium_launcher_core
        domino_engine
        domino_sys
        domino_mod
        dominium_product_common
)

add_executable(dominium-launcher-cli
    cli/launch_cli.c
)

target_include_directories(dominium-launcher-cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium-launcher-cli
    PRIVATE
        dominium_launcher_core
        domino_engine
        domino_core
        dominium_rules
        domino_sys
)

option(DOMINIUM_ENABLE_LAUNCHER_TUI "Build TUI launcher (curses)" OFF)
if(DOMINIUM_ENABLE_LAUNCHER_TUI)
    find_package(Curses)
    if(CURSES_FOUND)
        add_executable(dominium-launcher-tui
            tui/launch_tui.c
        )
        target_include_directories(dominium-launcher-tui
            PRIVATE
                ${DOMINIUM_INCLUDE_DIR}
                ${CURSES_INCLUDE_DIRS}
        )
        target_link_libraries(dominium-launcher-tui
            PRIVATE
                dominium_launcher_core
                domino_engine
                domino_core
                dominium_rules
                domino_sys
                ${CURSES_LIBRARIES}
        )
    else()
        message(STATUS "Curses not found; dominium-launcher-tui will not be built")
    endif()
endif()
