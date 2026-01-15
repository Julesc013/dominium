set(DOMINO_LAUNCHER_SOURCES
    launcher.c
    launcher_data.c
    launcher_ui.c
    ui_layout.c
)

add_library(domino_launcher STATIC ${DOMINO_LAUNCHER_SOURCES})
target_include_directories(domino_launcher
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(domino_launcher
    PUBLIC
        domino_engine
)
target_compile_features(domino_launcher PRIVATE c_std_90)

add_executable(domino_launcher_harness launcher_harness.c)
target_include_directories(domino_launcher_harness
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)
target_link_libraries(domino_launcher_harness
    PRIVATE
        domino_launcher
)
target_compile_features(domino_launcher_harness PRIVATE c_std_90)
