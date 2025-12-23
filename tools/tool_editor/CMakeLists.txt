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

set(TOOL_EDITOR_UI_DIR ${CMAKE_CURRENT_SOURCE_DIR}/ui)
set(TOOL_EDITOR_UI_DOC_DIR ${TOOL_EDITOR_UI_DIR}/doc)
set(TOOL_EDITOR_UI_GEN_DIR ${TOOL_EDITOR_UI_DIR}/gen)
set(TOOL_EDITOR_UI_USER_DIR ${TOOL_EDITOR_UI_DIR}/user)
set(TOOL_EDITOR_UI_REGISTRY_DIR ${TOOL_EDITOR_UI_DIR}/registry)
set(TOOL_EDITOR_UI_DOC ${TOOL_EDITOR_UI_DOC_DIR}/tool_editor_ui_doc.tlv)
set(TOOL_EDITOR_UI_REGISTRY ${TOOL_EDITOR_UI_REGISTRY_DIR}/ui_actions_registry.json)

set(TOOL_EDITOR_ACTIONS_GEN_H ${TOOL_EDITOR_UI_GEN_DIR}/ui_tool_editor_actions_gen.h)
set(TOOL_EDITOR_ACTIONS_GEN_CPP ${TOOL_EDITOR_UI_GEN_DIR}/ui_tool_editor_actions_gen.cpp)
set(TOOL_EDITOR_ACTIONS_USER_H ${TOOL_EDITOR_UI_USER_DIR}/ui_tool_editor_actions_user.h)
set(TOOL_EDITOR_ACTIONS_USER_CPP ${TOOL_EDITOR_UI_USER_DIR}/ui_tool_editor_actions_user.cpp)

file(MAKE_DIRECTORY ${TOOL_EDITOR_UI_GEN_DIR})
file(MAKE_DIRECTORY ${TOOL_EDITOR_UI_USER_DIR})
file(MAKE_DIRECTORY ${TOOL_EDITOR_UI_DOC_DIR})
file(MAKE_DIRECTORY ${TOOL_EDITOR_UI_REGISTRY_DIR})

add_custom_command(
    OUTPUT
        ${TOOL_EDITOR_ACTIONS_GEN_H}
        ${TOOL_EDITOR_ACTIONS_GEN_CPP}
        ${TOOL_EDITOR_ACTIONS_USER_H}
        ${TOOL_EDITOR_ACTIONS_USER_CPP}
    COMMAND
        $<TARGET_FILE:domui_codegen>
        --input ${TOOL_EDITOR_UI_DOC}
        --registry ${TOOL_EDITOR_UI_REGISTRY}
        --out-gen ${TOOL_EDITOR_UI_GEN_DIR}
        --out-user ${TOOL_EDITOR_UI_USER_DIR}
    DEPENDS
        domui_codegen
        ${TOOL_EDITOR_UI_DOC}
        ${TOOL_EDITOR_UI_REGISTRY}
    COMMENT "Generating tool editor UI action bindings"
)

add_custom_target(dominium_tool_editor_codegen
    DEPENDS
        ${TOOL_EDITOR_ACTIONS_GEN_H}
        ${TOOL_EDITOR_ACTIONS_GEN_CPP}
        ${TOOL_EDITOR_ACTIONS_USER_H}
        ${TOOL_EDITOR_ACTIONS_USER_CPP}
)

add_dependencies(dominium-tool-editor dominium_tool_editor_codegen)

target_sources(dominium-tool-editor PRIVATE
    ${TOOL_EDITOR_ACTIONS_GEN_CPP}
    ${TOOL_EDITOR_ACTIONS_USER_CPP}
)

set_source_files_properties(
    ${TOOL_EDITOR_ACTIONS_GEN_CPP}
    ${TOOL_EDITOR_ACTIONS_USER_CPP}
    PROPERTIES GENERATED TRUE
)

target_include_directories(dominium-tool-editor PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${TOOL_EDITOR_UI_GEN_DIR}
    ${TOOL_EDITOR_UI_USER_DIR}
)

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

add_executable(dominium-tool-editor-docgen
    tool_editor_docgen.cpp
)
target_link_libraries(dominium-tool-editor-docgen
    PRIVATE
        domino_ui_ir
)
set_target_properties(dominium-tool-editor-docgen PROPERTIES
    OUTPUT_NAME "dominium-tool-editor-docgen"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
