cmake_minimum_required(VERSION 3.16)

add_library(provider_api INTERFACE)
target_include_directories(provider_api INTERFACE
    ${DOMINIUM_INCLUDE_DIR}
)

add_library(provider_null_stub STATIC
    provider_null.c
)

target_include_directories(provider_null_stub PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(provider_null_stub PRIVATE
    provider_api
)

set_target_properties(provider_null_stub PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
