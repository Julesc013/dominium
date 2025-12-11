add_library(dominium_setup_core STATIC
    core/setup_core.c
    core/product_info.c
)

target_include_directories(dominium_setup_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_setup_core
    PUBLIC
        domino_engine
        dominium_common
)

add_executable(dominium-setup-cli
    main_setup.cpp
    entry.cpp
    cli/setup_cli.c
)

target_include_directories(dominium-setup-cli
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium-setup-cli
    PRIVATE
        domino_core
        domino_engine
        dominium_rules
        dominium_setup_core
)

set_target_properties(dominium-setup-cli PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup-cli)

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

if(APPLE)
    add_executable(dominium_setup_macos_gui
        os/macos/setup_macos_gui.m
    )
    target_link_libraries(dominium_setup_macos_gui
        PRIVATE
            "-framework Cocoa"
    )
    set_source_files_properties(os/macos/setup_macos_gui.m PROPERTIES
        COMPILE_FLAGS "-fobjc-arc"
    )
endif()
