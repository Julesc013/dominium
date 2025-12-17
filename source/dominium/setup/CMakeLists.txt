cmake_minimum_required(VERSION 3.16)

add_subdirectory(core)

add_executable(dominium-setup
    cli/dominium_setup_main.c
)

target_include_directories(dominium-setup PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/core/include
)

target_link_libraries(dominium-setup
    PRIVATE
        dsu_core
)

set_target_properties(dominium-setup PROPERTIES
    OUTPUT_NAME "dominium-setup"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup)
add_subdirectory(tests)
