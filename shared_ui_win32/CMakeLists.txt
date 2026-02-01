cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_library(shared_ui_win32 STATIC
        src/ui_ir_parser_stub.c
        src/win32_control_factory_stub.c
        src/win32_accessibility_stub.c
        src/win32_layout_stub.c
        src/win32_shell_stub.c
    )
    target_include_directories(shared_ui_win32 PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/engine/include
    )
    set_target_properties(shared_ui_win32 PROPERTIES
        C_STANDARD 90
        C_STANDARD_REQUIRED ON
        C_EXTENSIONS OFF
    )
else()
    add_library(shared_ui_win32 INTERFACE)
    target_include_directories(shared_ui_win32 INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_SOURCE_DIR}/engine/include
    )
endif()

add_library(shared_ui::win32 ALIAS shared_ui_win32)
