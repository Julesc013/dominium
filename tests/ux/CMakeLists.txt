cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_executable(ui_accessibility_tests
    ui_accessibility_tests.cpp
)
target_include_directories(ui_accessibility_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/libs/contracts/include
    ${CMAKE_SOURCE_DIR}/tools/ui_shared/src/ui_ir
)
target_link_libraries(ui_accessibility_tests PRIVATE domino_ui_ir)
set_target_properties(ui_accessibility_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dom_add_testx(NAME ux_ui_accessibility
    COMMAND $<TARGET_FILE:ui_accessibility_tests>
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)

dom_add_testx(NAME ux_presentation_parity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/ux_presentation_tests.py
        --client $<TARGET_FILE:dominium_client>
        --launcher $<TARGET_FILE:launcher_cli>
        --tools $<TARGET_FILE:dominium-tools>
        --temp-root ${CMAKE_BINARY_DIR}/tests/ux_presentation
    LABELS ${DOM_TESTX_LABEL_SMOKE}
)
