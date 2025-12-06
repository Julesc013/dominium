cmake_minimum_required(VERSION 3.15)

add_library(dom_platform_win32 STATIC
    dom_platform_win32.c
    dom_platform_sdl2.c
)

target_include_directories(dom_platform_win32
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/engine/platform
        ${CMAKE_SOURCE_DIR}/engine/core
)

target_link_libraries(dom_platform_win32
    PUBLIC
        dom_core
        user32
        gdi32
)
