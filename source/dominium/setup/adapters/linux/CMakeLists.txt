cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup-linux
    dominium_setup_adapter_linux.c
    dsu_linux_platform_iface.c
)

target_include_directories(dominium-setup-linux PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dominium-setup-linux
    PRIVATE
        dsu_core
)

set_target_properties(dominium-setup-linux PROPERTIES
    OUTPUT_NAME "dominium-setup-linux"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup-linux)

