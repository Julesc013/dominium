cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup-macos
    dominium_setup_adapter_macos.c
    dsu_macos_platform_iface.c
)

target_include_directories(dominium-setup-macos PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dominium-setup-macos
    PRIVATE
        dsu_core
)

set_target_properties(dominium-setup-macos PROPERTIES
    OUTPUT_NAME "dominium-setup-macos"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup-macos)

