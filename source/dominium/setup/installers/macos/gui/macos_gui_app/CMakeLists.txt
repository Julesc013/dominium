cmake_minimum_required(VERSION 3.16)

if(NOT APPLE)
    return()
endif()

enable_language(OBJC)

set(DSU_MACOS_GUI_SRC
    ${CMAKE_CURRENT_LIST_DIR}/src/main.m
)

add_executable(dominium-setup-gui MACOSX_BUNDLE
    ${DSU_MACOS_GUI_SRC}
)

target_include_directories(dominium-setup-gui PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/../../common/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/include
    ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dominium-setup-gui
    PRIVATE
        dsu_macos_installer_common
        setup_kernel
        setup_services_impl_platform
        "-framework Cocoa"
        "-framework AppKit"
        "-framework Foundation"
)

target_compile_options(dominium-setup-gui PRIVATE
    "-fobjc-arc"
)

set_target_properties(dominium-setup-gui PROPERTIES
    OUTPUT_NAME "dominium-setup-gui"
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_LIST_DIR}/resources/Info.plist"
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

dominium_bundle_runtime(dominium-setup-gui)
