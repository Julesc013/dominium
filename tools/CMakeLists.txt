cmake_minimum_required(VERSION 3.15)

add_executable(dom_tools_editor
    tools_main.c
)

target_include_directories(dom_tools_editor
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_tools_editor
    PRIVATE
        dom_engine
)
