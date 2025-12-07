cmake_minimum_required(VERSION 3.15)

add_executable(dom_client
    dom_client_main.c
    input/dom_input_mapping.c
)

target_include_directories(dom_client
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_client
    PRIVATE
        dom_engine
)
