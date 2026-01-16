cmake_minimum_required(VERSION 3.16)

add_library(libs_contracts INTERFACE)
target_include_directories(libs_contracts INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
add_library(libs::contracts ALIAS libs_contracts)
