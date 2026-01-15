cmake_minimum_required(VERSION 3.16)

add_library(dominium_tool_replay STATIC
    tool_replay.c
)

target_include_directories(dominium_tool_replay
    PUBLIC
        ${DOMINIUM_INCLUDE_DIR}
)

target_link_libraries(dominium_tool_replay
    PRIVATE
        dominium_tools_core
        domino_sys
)

target_compile_features(dominium_tool_replay PRIVATE c_std_90)
