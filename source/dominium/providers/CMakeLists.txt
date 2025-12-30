cmake_minimum_required(VERSION 3.16)

add_library(provider_api INTERFACE)
target_include_directories(provider_api INTERFACE
    ${DOMINIUM_INCLUDE_DIR}
)

add_library(providers_builtin STATIC
    provider_null.c
    provider_content_null.c
    provider_content_local_fs.c
    provider_trust_null.c
    provider_keychain_null.c
    provider_net_null.c
    provider_os_integration_null.c
    provider_registry.c
)

target_include_directories(providers_builtin PRIVATE
    ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(providers_builtin
    PUBLIC
        provider_api
    PRIVATE
        core_err
)

set_target_properties(providers_builtin PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
