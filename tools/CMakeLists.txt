cmake_minimum_required(VERSION 3.15)

add_executable(dom_tools_editor
    tools_main.c
)

target_include_directories(dom_tools_editor
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_tools_editor
    PRIVATE
        dom_engine
)

# Setup/installer stubs per platform
if (WIN32)
    add_executable(dom_setup-win32
        setup/win32/dom_setup_win32_stub.c
    )
elseif(APPLE)
    add_executable(dom_setup-macosx
        setup/macosx/dom_setup_macosx_stub.c
    )
elseif(UNIX)
    add_executable(dom_setup-posix
        setup/posix/dom_setup_posix_stub.c
    )
endif()
