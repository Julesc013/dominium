cmake_minimum_required(VERSION 3.16)

add_library(build_identity STATIC
    src/build_identity.c
)

target_include_directories(build_identity PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(build_identity PUBLIC
    libs::contracts
)

set_target_properties(build_identity PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_library(libs::build_identity ALIAS build_identity)
