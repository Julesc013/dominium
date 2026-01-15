cmake_minimum_required(VERSION 3.16)

add_library(dominium_tool_test STATIC
    tool_test.c
)

target_include_directories(dominium_tool_test
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_tool_test
    PRIVATE
        dominium_tools_core
        domino_sys
)

target_compile_features(dominium_tool_test PRIVATE c_std_90)
