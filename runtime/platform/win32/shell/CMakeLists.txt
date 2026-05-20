cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_library(runtime_platform_win32_ui STATIC
        ${CMAKE_SOURCE_DIR}/runtime/ui/backend/win32/ui_ir_parser_stub.c
        ${CMAKE_SOURCE_DIR}/runtime/ui/backend/win32/win32_control_factory_stub.c
        ${CMAKE_SOURCE_DIR}/runtime/ui/backend/win32/win32_accessibility_stub.c
        ${CMAKE_SOURCE_DIR}/runtime/ui/backend/win32/win32_layout_stub.c
        win32_shell_stub.c
    )
    target_include_directories(runtime_platform_win32_ui PUBLIC
        ${CMAKE_SOURCE_DIR}/runtime/ui/backend/win32/include
        ${CMAKE_SOURCE_DIR}/engine/include
    )
    set_target_properties(runtime_platform_win32_ui PROPERTIES
        C_STANDARD 17
        C_STANDARD_REQUIRED ON
        C_EXTENSIONS OFF
    )
else()
    add_library(runtime_platform_win32_ui INTERFACE)
    target_include_directories(runtime_platform_win32_ui INTERFACE
        ${CMAKE_SOURCE_DIR}/runtime/ui/backend/win32/include
        ${CMAKE_SOURCE_DIR}/engine/include
    )
endif()
