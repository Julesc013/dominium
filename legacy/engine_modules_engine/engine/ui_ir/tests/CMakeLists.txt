cmake_minimum_required(VERSION 3.16)

add_executable(domino_ui_ir_tests
    ui_ir_tests.cpp
)

target_link_libraries(domino_ui_ir_tests
    PRIVATE
        domino_ui_ir
)

set_target_properties(domino_ui_ir_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_test(NAME domino_ui_ir_tests COMMAND domino_ui_ir_tests)

add_executable(domino_ui_ir_fixture_gen
    ui_ir_fixture_gen.cpp
)

target_link_libraries(domino_ui_ir_fixture_gen
    PRIVATE
        domino_ui_ir
)

set_target_properties(domino_ui_ir_fixture_gen PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
