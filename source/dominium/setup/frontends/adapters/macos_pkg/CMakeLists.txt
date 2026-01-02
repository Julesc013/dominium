cmake_minimum_required(VERSION 3.16)

if(APPLE)
    add_custom_target(build-macos-pkg-wrapper
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/packaging
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${CMAKE_CURRENT_SOURCE_DIR}/packaging
            ${CMAKE_CURRENT_BINARY_DIR}/packaging
        COMMENT "Staging setup macOS PKG wrapper scripts"
    )
else()
    add_custom_target(build-macos-pkg-wrapper)
endif()
