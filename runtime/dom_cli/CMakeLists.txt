cmake_minimum_required(VERSION 3.15)

add_executable(dom_cli
    dom_cli_main.cpp
)

target_include_directories(dom_cli
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_cli
    PRIVATE
        dom_engine
)
