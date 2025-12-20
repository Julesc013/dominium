cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_subdirectory(windows)
endif()

if(APPLE)
    add_subdirectory(macos)
endif()

if(UNIX AND NOT APPLE)
    add_subdirectory(linux)
endif()

add_subdirectory(steam)

