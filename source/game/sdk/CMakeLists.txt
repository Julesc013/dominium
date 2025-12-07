cmake_minimum_required(VERSION 3.15)

# Placeholder for game mod SDK bindings.
add_library(dom_game_sdk INTERFACE)
target_include_directories(dom_game_sdk
    INTERFACE
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/include/dom_priv
)

# TODO: publish dom_game_mod_api.h once scripting/plugin surface is defined.
