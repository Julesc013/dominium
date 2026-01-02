cmake_minimum_required(VERSION 3.16)

if(UNIX AND NOT APPLE)
    add_custom_target(build-linux-deb-wrapper
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/packaging
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${CMAKE_CURRENT_SOURCE_DIR}/packaging
            ${CMAKE_CURRENT_BINARY_DIR}/packaging
        COMMENT "Staging setup2 Linux DEB wrapper scripts"
    )
else()
    add_custom_target(build-linux-deb-wrapper)
endif()
