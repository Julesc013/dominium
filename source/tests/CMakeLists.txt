cmake_minimum_required(VERSION 3.16)

add_executable(domino_numeric_test
    numeric_test.c
)

target_include_directories(domino_numeric_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
)

target_link_libraries(domino_numeric_test
    domino_core
)

set_target_properties(domino_numeric_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
