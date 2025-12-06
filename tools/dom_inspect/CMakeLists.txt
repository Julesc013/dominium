cmake_minimum_required(VERSION 3.15)

add_executable(dom_inspect
    dom_inspect.c
)

target_include_directories(dom_inspect
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_inspect
    PRIVATE
        dom_engine
)
