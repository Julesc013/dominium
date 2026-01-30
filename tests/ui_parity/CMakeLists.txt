cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME ui_client_menu_parity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/client_menu_parity_tests.py
        --client $<TARGET_FILE:dominium_client>
        --temp-root ${CMAKE_BINARY_DIR}/tests/ui_client_menu_parity
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)
