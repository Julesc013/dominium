cmake_minimum_required(VERSION 3.16)

add_executable(tool_ui_bind
    ui_bind_main.cpp
    ui_bind_index.cpp
)

target_include_directories(tool_ui_bind PRIVATE
    ${CMAKE_SOURCE_DIR}/tools/ui_shared/include
    ${CMAKE_SOURCE_DIR}/tools/ui_shared/src/ui_ir
    ${CMAKE_SOURCE_DIR}/libs/appcore
)

target_link_libraries(tool_ui_bind PRIVATE
    domino_ui_ir
    libs::appcore
)

set_target_properties(tool_ui_bind PROPERTIES
    OUTPUT_NAME "tool_ui_bind"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dist_set_role(tool_ui_bind tools)

add_executable(tool_ui_doc_annotate
    ui_doc_annotate_main.cpp
    ui_bind_index.cpp
)

target_include_directories(tool_ui_doc_annotate PRIVATE
    ${CMAKE_SOURCE_DIR}/tools/ui_shared/include
    ${CMAKE_SOURCE_DIR}/tools/ui_shared/src/ui_ir
    ${CMAKE_SOURCE_DIR}/libs/appcore
)

target_link_libraries(tool_ui_doc_annotate PRIVATE
    domino_ui_ir
    libs::appcore
)

set_target_properties(tool_ui_doc_annotate PROPERTIES
    OUTPUT_NAME "tool_ui_doc_annotate"
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

dist_set_role(tool_ui_doc_annotate tools)

add_custom_target(ui_bind_phase
    COMMAND $<TARGET_FILE:tool_ui_bind>
        --repo-root ${CMAKE_SOURCE_DIR}
        --ui-index ${CMAKE_SOURCE_DIR}/tools/ui_index/ui_index.json
        --out-dir ${CMAKE_SOURCE_DIR}/libs/appcore/ui_bind
        --check
    DEPENDS tool_ui_bind
)
