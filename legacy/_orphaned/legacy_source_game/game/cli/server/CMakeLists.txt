cmake_minimum_required(VERSION 3.15)

add_executable(dom_server
    dom_server_main.c
)

target_include_directories(dom_server
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_server
    PRIVATE
        dom_engine
)
