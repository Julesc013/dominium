cmake_minimum_required(VERSION 3.16)

set(UI_PREVIEW_COMMON_SRC
    common/ui_preview_common.cpp
    common/ui_preview_common.h
)

if(WIN32)
    add_executable(dominium-ui-preview-host-win32 WIN32
        win32/ui_preview_host_win32.cpp
        ${UI_PREVIEW_COMMON_SRC}
    )

    target_include_directories(dominium-ui-preview-host-win32 PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/common
    )

    target_link_libraries(dominium-ui-preview-host-win32
        PRIVATE
            domino_ui_ir
            domino_core
            dui_api
            comctl32
    )

    set_target_properties(dominium-ui-preview-host-win32 PROPERTIES
        OUTPUT_NAME "dominium-ui-preview-host-win32"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    dist_set_role(dominium-ui-preview-host-win32 tools)

    set_property(TARGET dominium-ui-preview-host-win32 PROPERTY
        VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    )
    set_property(TARGET dominium-ui-preview-host-win32 PROPERTY
        VS_DEBUGGER_COMMAND_ARGUMENTS
        "--ui \"${CMAKE_SOURCE_DIR}/tools/launcher/ui/doc/launcher_ui_doc.tlv\" --watch"
    )
endif()

if(APPLE)
    add_executable(dominium-ui-preview-host-macos
        macos/ui_preview_host_macos.cpp
        ${UI_PREVIEW_COMMON_SRC}
    )

    target_include_directories(dominium-ui-preview-host-macos PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/common
    )

    target_link_libraries(dominium-ui-preview-host-macos
        PRIVATE
            domino_ui_ir
            domino_core
            dui_api
    )

    set_target_properties(dominium-ui-preview-host-macos PROPERTIES
        OUTPUT_NAME "dominium-ui-preview-host-macos"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    dist_set_role(dominium-ui-preview-host-macos tools)

    set_property(TARGET dominium-ui-preview-host-macos PROPERTY
        XCODE_SCHEME_ARGUMENTS
        "--ui \"${CMAKE_SOURCE_DIR}/tools/launcher/ui/doc/launcher_ui_doc.tlv\" --watch"
    )
    set_property(TARGET dominium-ui-preview-host-macos PROPERTY
        XCODE_SCHEME_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    )
endif()

if(UNIX AND NOT APPLE)
    add_executable(dominium-ui-preview-host-linux
        linux/ui_preview_host_linux.cpp
        ${UI_PREVIEW_COMMON_SRC}
    )

    target_include_directories(dominium-ui-preview-host-linux PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/common
    )

    target_link_libraries(dominium-ui-preview-host-linux
        PRIVATE
            domino_ui_ir
            domino_core
            dui_api
    )

    set_target_properties(dominium-ui-preview-host-linux PROPERTIES
        OUTPUT_NAME "dominium-ui-preview-host-linux"
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    dist_set_role(dominium-ui-preview-host-linux tools)
endif()
