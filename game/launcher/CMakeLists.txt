cmake_minimum_required(VERSION 3.15)

set(DOM_LAUNCHER_SOURCES
    dom_launcher_main.c
)

# Windows launcher
if (WIN32)
    add_executable(dom_launcher-win32-software WIN32
        ${DOM_LAUNCHER_SOURCES}
    )
    target_include_directories(dom_launcher-win32-software PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
        ${DOM_GENERATED_DIR}
    )
    target_compile_definitions(dom_launcher-win32-software PRIVATE
        DOM_PLATFORM=WIN32
        DOM_RENDER_BACKEND=SOFTWARE
    )
    target_link_libraries(dom_launcher-win32-software
        PRIVATE
            dom_engine
            comctl32
            riched20
    )
endif()

# Posix (Linux/BSD) launcher using SDL2
if (UNIX AND NOT APPLE)
    add_executable(dom_launcher-posix-sdl2-software
        ${DOM_LAUNCHER_SOURCES}
    )
    target_compile_definitions(dom_launcher-posix-sdl2-software PRIVATE
        DOM_PLATFORM=SDL2
        DOM_RENDER_BACKEND=SOFTWARE
    )
    target_include_directories(dom_launcher-posix-sdl2-software PRIVATE ${CMAKE_SOURCE_DIR}/engine)
    target_link_libraries(dom_launcher-posix-sdl2-software
        PRIVATE
            dom_engine
    )
endif()

# macOS launcher
if (APPLE)
    add_executable(dom_launcher-macosx-software
        ${DOM_LAUNCHER_SOURCES}
    )
    target_compile_definitions(dom_launcher-macosx-software PRIVATE
        DOM_PLATFORM=MACOSX
        DOM_RENDER_BACKEND=SOFTWARE
    )
    target_include_directories(dom_launcher-macosx-software PRIVATE ${CMAKE_SOURCE_DIR}/engine)
    target_link_libraries(dom_launcher-macosx-software
        PRIVATE
            dom_engine
    )
endif()
