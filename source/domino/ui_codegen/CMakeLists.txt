cmake_minimum_required(VERSION 3.16)

add_library(domino_ui_codegen STATIC
    ui_codegen_stub.cpp
)

target_include_directories(domino_ui_codegen PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
)

set_target_properties(domino_ui_codegen PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
