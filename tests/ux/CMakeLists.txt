cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME ux_presentation_parity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/ux_presentation_tests.py
        --client $<TARGET_FILE:dominium_client>
        --launcher $<TARGET_FILE:launcher_cli>
        --tools $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/ux_presentation
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)
