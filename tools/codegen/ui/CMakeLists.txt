cmake_minimum_required(VERSION 3.16)

add_library(domino_ui_codegen STATIC
    ui_codegen.cpp
)

target_include_directories(domino_ui_codegen PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../ui_ir
)

target_link_libraries(domino_ui_codegen
    PUBLIC
        domino_ui_ir
)

set_target_properties(domino_ui_codegen PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if(DOMUI_ENABLE_CODEGEN)
    add_executable(domui_codegen
        ui_codegen_main.cpp
    )

    target_link_libraries(domui_codegen
        PRIVATE
            domino_ui_codegen
    )

    set_target_properties(domui_codegen PROPERTIES
        OUTPUT_NAME "tool_ui_codegen"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    dist_set_role(domui_codegen tools)
endif()

add_executable(dominium-tool-editor-docgen
    tool_editor/tool_editor_docgen.cpp
)
target_link_libraries(dominium-tool-editor-docgen
    PRIVATE
        domino_ui_ir
)
set_target_properties(dominium-tool-editor-docgen PROPERTIES
    OUTPUT_NAME "tool_tool_editor_docgen"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dist_set_role(dominium-tool-editor-docgen tools)

add_subdirectory(tests)
