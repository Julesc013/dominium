cmake_minimum_required(VERSION 3.16)

add_library(domino_ui_ir STATIC
    ui_ir_types.cpp
    ui_ir_string.cpp
    ui_ir_props.cpp
    ui_ir_doc.cpp
    ui_ir_diag.cpp
    ui_ir_fileio.cpp
    ui_ir_tlv.cpp
    ui_ir_json.cpp
    ui_ir_legacy_import.cpp
    ui_caps.cpp
)

target_include_directories(domino_ui_ir PUBLIC
    ${DOMINIUM_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(domino_ui_ir
    PUBLIC
        domino_core
)

set_target_properties(domino_ui_ir PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_subdirectory(tests)
