cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_executable(dominium-ui-editor WIN32
        ui_editor_main_win32.cpp
    )
else()
    add_executable(dominium-ui-editor
        ui_editor_main_win32.cpp
    )
endif()

target_link_libraries(dominium-ui-editor
    PRIVATE
        domino_core
        domino_ui_ir
        domino_ui_codegen
        comctl32
)

target_compile_definitions(dominium-ui-editor
    PRIVATE
        DOMUI_ENABLE_JSON_MIRROR=$<BOOL:${DOMUI_ENABLE_JSON_MIRROR}>
        DOMUI_ENABLE_CODEGEN=$<BOOL:${DOMUI_ENABLE_CODEGEN}>
)

set_target_properties(dominium-ui-editor PROPERTIES
    OUTPUT_NAME "dominium-ui-editor"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
