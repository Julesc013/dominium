cmake_minimum_required(VERSION 3.16)

add_library(dominium_tools_core STATIC
    tool_core.c
    product_info.c
)

target_include_directories(dominium_tools_core
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_tools_core
    PUBLIC
        dominium_common
)

target_compile_features(dominium_tools_core PRIVATE c_std_90)

add_executable(dominium-tools
    tool_host_cli.c
)

target_include_directories(dominium-tools
    PRIVATE
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium-tools
    PRIVATE
        dominium_tools_core
        domino_core
)

target_compile_features(dominium-tools PRIVATE c_std_90)

dominium_bundle_runtime(dominium-tools)
