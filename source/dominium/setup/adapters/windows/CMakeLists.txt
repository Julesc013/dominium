cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup-win
    dominium_setup_adapter_windows.c
    dsu_windows_platform_iface.c
)

target_include_directories(dominium-setup-win PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dominium-setup-win
    PRIVATE
        setup_kernel
        setup_services_impl_platform
        advapi32
)

set_target_properties(dominium-setup-win PROPERTIES
    OUTPUT_NAME "dominium-setup-win"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup-win)

