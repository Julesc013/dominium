cmake_minimum_required(VERSION 3.15)

add_executable(dom_launcher
    dom_launcher_main.c
)

target_include_directories(dom_launcher
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_launcher
    PRIVATE
        dom_engine
)
