cmake_minimum_required(VERSION 3.16)

add_library(domino_ui_ir STATIC
    ui_ir_stub.cpp
)

target_include_directories(domino_ui_ir PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
)

set_target_properties(domino_ui_ir PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
