cmake_minimum_required(VERSION 3.16)

add_library(libs_base INTERFACE)
target_include_directories(libs_base INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/base/include
)
add_library(libs::base ALIAS libs_base)

add_library(libs_crypto INTERFACE)
target_include_directories(libs_crypto INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/crypto/include
)
add_library(libs::crypto ALIAS libs_crypto)

add_library(libs_fsmodel INTERFACE)
target_include_directories(libs_fsmodel INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/fsmodel/include
)
add_library(libs::fsmodel ALIAS libs_fsmodel)

add_library(libs_netproto INTERFACE)
target_include_directories(libs_netproto INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/netproto/include
)
add_library(libs::netproto ALIAS libs_netproto)

add_subdirectory(contracts)
add_subdirectory(appcore)
