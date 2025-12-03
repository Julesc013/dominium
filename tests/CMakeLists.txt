cmake_minimum_required(VERSION 3.15)

add_executable(dom_tests
    tests_runner.c
)

target_include_directories(dom_tests
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_tests
    PRIVATE
        dom_engine
)
