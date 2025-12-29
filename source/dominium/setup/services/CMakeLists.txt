cmake_minimum_required(VERSION 3.16)

add_library(setup_services_impl_platform STATIC
    platform/dsu_platform_iface.c
)

target_include_directories(setup_services_impl_platform PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/fs
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/util
)

target_link_libraries(setup_services_impl_platform
    PRIVATE
        setup_kernel
)

set_target_properties(setup_services_impl_platform PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_library(setup_services_impl_null STATIC
    null/dsu_platform_iface_null.c
)

target_include_directories(setup_services_impl_null PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/fs
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/util
)

target_link_libraries(setup_services_impl_null
    PRIVATE
        setup_kernel
)

set_target_properties(setup_services_impl_null PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
