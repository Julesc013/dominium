cmake_minimum_required(VERSION 3.16)

add_executable(domino_ui_codegen_tests
    ui_codegen_tests.cpp
)

target_link_libraries(domino_ui_codegen_tests
    PRIVATE
        domino_ui_codegen
        domino_ui_ir
)

set_target_properties(domino_ui_codegen_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME domino_ui_codegen_tests COMMAND domino_ui_codegen_tests)
