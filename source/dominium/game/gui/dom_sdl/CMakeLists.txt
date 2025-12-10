cmake_minimum_required(VERSION 3.15)

add_executable(dom_sdl_stub
    dom_sdl_stub.cpp
)

target_include_directories(dom_sdl_stub
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_sdl_stub
    PRIVATE
        dom_engine
)
