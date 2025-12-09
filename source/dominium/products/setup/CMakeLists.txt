add_library(dominium_setup_core STATIC
    core/setup_core.c
)

target_include_directories(dominium_setup_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_setup_core
    PUBLIC
        domino_engine
)

add_executable(dominium-setup-cli
    cli/setup_cli.c
)

target_include_directories(dominium-setup-cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium-setup-cli
    PRIVATE
        domino_engine
        dominium_rules
        dominium_setup_core
)

if(WIN32)
    add_executable(dominium_setup_win32_gui
        os/win32/setup_win32_gui.c
    )
    target_link_libraries(dominium_setup_win32_gui
        PRIVATE
            user32
            shell32
            comctl32
            ole32
    )
endif()
