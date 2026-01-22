cmake_minimum_required(VERSION 3.16)

add_library(dominium_app_runtime STATIC
    src/app_runtime.c
)
target_include_directories(dominium_app_runtime PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_link_libraries(dominium_app_runtime PUBLIC
    domino_engine
    libs::contracts
)
set_target_properties(dominium_app_runtime PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_library(app::runtime ALIAS dominium_app_runtime)
