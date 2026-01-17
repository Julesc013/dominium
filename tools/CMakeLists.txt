cmake_minimum_required(VERSION 3.16)

add_library(tools_shared STATIC
    _shared/tools_shared_stub.c
)
target_include_directories(tools_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/_shared
)
target_link_libraries(tools_shared
    PUBLIC
        libs::contracts
)
set_target_properties(tools_shared PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(tools::shared ALIAS tools_shared)

add_executable(dominium-tools
    tools_host_main.c
)
target_link_libraries(dominium-tools PRIVATE tools::shared)
set_target_properties(dominium-tools PROPERTIES
    OUTPUT_NAME "tools"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(coredata_compile
    coredata_compile_stub.c
)
set_target_properties(coredata_compile PROPERTIES
    OUTPUT_NAME "coredata_compile"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_executable(coredata_validate
    coredata_validate_stub.c
)
set_target_properties(coredata_validate PROPERTIES
    OUTPUT_NAME "coredata_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(data_validate
    data_validate/data_validate_main.c
)
target_link_libraries(data_validate PRIVATE domino_engine)
set_target_properties(data_validate PROPERTIES
    OUTPUT_NAME "data_validate"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_executable(tools::host ALIAS dominium-tools)
add_executable(tools::coredata_compile ALIAS coredata_compile)
add_executable(tools::coredata_validate ALIAS coredata_validate)
add_executable(tools::data_validate ALIAS data_validate)
