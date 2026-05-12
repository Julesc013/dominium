cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_custom_target(build-windows-msi-wrapper
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/wix
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${CMAKE_CURRENT_SOURCE_DIR}/wix
            ${CMAKE_CURRENT_BINARY_DIR}/wix
        COMMENT "Staging WiX sources for setup MSI wrapper"
    )
else()
    add_custom_target(build-windows-msi-wrapper)
endif()
