cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup-steam
    dominium_setup_adapter_steam.c
)

target_include_directories(dominium-setup-steam PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dominium-setup-steam
    PRIVATE
        dsu_core
)

set_target_properties(dominium-setup-steam PROPERTIES
    OUTPUT_NAME "dominium-setup-steam"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup-steam)

