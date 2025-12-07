cmake_minimum_required(VERSION 3.15)

add_library(dom_audio STATIC
    dom_audio_api.c
)

target_include_directories(dom_audio
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/engine/core
)

target_link_libraries(dom_audio
    PUBLIC
        dom_core
)
