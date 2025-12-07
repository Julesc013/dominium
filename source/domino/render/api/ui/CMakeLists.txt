cmake_minimum_required(VERSION 3.15)

add_library(dom_ui STATIC
    dom_ui_core.c
)

target_include_directories(dom_ui
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/engine/core
)

target_link_libraries(dom_ui
    PUBLIC
        dom_core
)
