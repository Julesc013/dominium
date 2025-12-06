cmake_minimum_required(VERSION 3.15)

add_executable(dom_validate_content
    dom_validate_content.c
)

target_include_directories(dom_validate_content
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_validate_content
    PRIVATE
        dom_engine
)
