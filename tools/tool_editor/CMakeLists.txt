cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_executable(dominium-tool-editor WIN32
        tool_editor_main_win32.cpp
    )
else()
    add_executable(dominium-tool-editor
        tool_editor_main_win32.cpp
    )
endif()

target_link_libraries(dominium-tool-editor
    PRIVATE
        domino_ui_ir
        domino_ui_codegen
)

set_target_properties(dominium-tool-editor PROPERTIES
    OUTPUT_NAME "dominium-tool-editor"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
